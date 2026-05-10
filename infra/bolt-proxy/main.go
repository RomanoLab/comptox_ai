package main

import (
	"crypto/tls"
	"encoding/binary"
	"io"
	"log"
	"net"
	"net/http"
	"os"
	"sync"
	"time"
)

const (
	defaultListenAddr  = ":7688"
	defaultBackendAddr = "memgraph:7687"
	defaultHealthAddr  = ":8081"
)

func main() {
	listenAddr := envOr("LISTEN_ADDR", defaultListenAddr)
	backendAddr := envOr("BACKEND_ADDR", defaultBackendAddr)
	healthAddr := envOr("HEALTH_ADDR", defaultHealthAddr)
	tlsCert := os.Getenv("TLS_CERT")
	tlsKey := os.Getenv("TLS_KEY")

	go startHealthServer(healthAddr, backendAddr)

	var ln net.Listener
	var err error

	if tlsCert != "" && tlsKey != "" {
		cert, certErr := tls.LoadX509KeyPair(tlsCert, tlsKey)
		if certErr != nil {
			log.Fatalf("failed to load TLS keypair: %v", certErr)
		}
		ln, err = tls.Listen("tcp", listenAddr, &tls.Config{
			Certificates: []tls.Certificate{cert},
			MinVersion:   tls.VersionTLS12,
		})
		log.Printf("bolt-proxy listening on %s (TLS), forwarding to %s", listenAddr, backendAddr)
	} else {
		ln, err = net.Listen("tcp", listenAddr)
		log.Printf("bolt-proxy listening on %s, forwarding to %s", listenAddr, backendAddr)
	}
	if err != nil {
		log.Fatalf("failed to listen on %s: %v", listenAddr, err)
	}

	for {
		clientConn, err := ln.Accept()
		if err != nil {
			log.Printf("accept error: %v", err)
			continue
		}
		go handleConnection(clientConn, backendAddr)
	}
}

func envOr(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

// startHealthServer exposes a minimal /healthz endpoint that returns 200 if
// the backend Bolt port can be dialled, 503 otherwise. Used by Docker
// HEALTHCHECK and post-deploy probes.
func startHealthServer(addr, backendAddr string) {
	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
		conn, err := net.DialTimeout("tcp", backendAddr, 2*time.Second)
		if err != nil {
			http.Error(w, "backend unreachable: "+err.Error(), http.StatusServiceUnavailable)
			return
		}
		_ = conn.Close()
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte("ok"))
	})
	srv := &http.Server{
		Addr:              addr,
		Handler:           mux,
		ReadHeaderTimeout: 5 * time.Second,
	}
	log.Printf("health server listening on %s", addr)
	if err := srv.ListenAndServe(); err != nil {
		log.Printf("health server exited: %v", err)
	}
}

// handleConnection proxies a single Bolt client session.
// It performs the Bolt handshake passthrough, then inspects every client
// message for write operations before forwarding to the backend.
func handleConnection(clientConn net.Conn, backendAddr string) {
	defer clientConn.Close()

	backendConn, err := net.Dial("tcp", backendAddr)
	if err != nil {
		log.Printf("failed to connect to backend %s: %v", backendAddr, err)
		return
	}
	defer backendConn.Close()

	// Pass through the Bolt handshake (preamble + version negotiation).
	// 20 bytes from client (4-byte magic + 4x4-byte versions),
	// 4 bytes back from server (chosen version).
	handshakeBuf := make([]byte, 20)
	if _, err := io.ReadFull(clientConn, handshakeBuf); err != nil {
		log.Printf("handshake read error: %v", err)
		return
	}
	if _, err := backendConn.Write(handshakeBuf); err != nil {
		log.Printf("handshake forward error: %v", err)
		return
	}
	versionBuf := make([]byte, 4)
	if _, err := io.ReadFull(backendConn, versionBuf); err != nil {
		log.Printf("handshake response read error: %v", err)
		return
	}
	if _, err := clientConn.Write(versionBuf); err != nil {
		log.Printf("handshake response forward error: %v", err)
		return
	}

	var wg sync.WaitGroup
	wg.Add(2)

	// Backend → Client: pass through unmodified
	go func() {
		defer wg.Done()
		_, _ = io.Copy(clientConn, backendConn)
	}()

	// Client → Backend: inspect messages for write queries
	go func() {
		defer wg.Done()
		proxyClientMessages(clientConn, backendConn)
	}()

	wg.Wait()
}

// proxyClientMessages reads chunked Bolt messages from the client, inspects
// RUN messages for write queries, and either forwards or rejects them.
func proxyClientMessages(clientConn, backendConn net.Conn) {
	for {
		msg, err := readBoltMessage(clientConn)
		if err != nil {
			return
		}

		if query, ok := extractRunQuery(msg); ok {
			if isWriteQuery(query) {
				log.Printf("BLOCKED write query: %.100s", query)
				sendFailure(clientConn, "Write operations are not permitted on this endpoint")
				continue
			}
		}

		if err := writeBoltMessage(backendConn, msg); err != nil {
			return
		}
	}
}

// readBoltMessage reads a chunked Bolt message from conn.
// Bolt chunks: [uint16 size][size bytes]... terminated by [0x00 0x00].
func readBoltMessage(conn net.Conn) ([]byte, error) {
	var msg []byte
	sizeBuf := make([]byte, 2)

	for {
		if _, err := io.ReadFull(conn, sizeBuf); err != nil {
			return nil, err
		}
		chunkSize := int(binary.BigEndian.Uint16(sizeBuf))
		if chunkSize == 0 {
			break
		}
		chunk := make([]byte, chunkSize)
		if _, err := io.ReadFull(conn, chunk); err != nil {
			return nil, err
		}
		msg = append(msg, chunk...)
	}

	return msg, nil
}

// writeBoltMessage writes a complete message back as a single chunk + terminator.
func writeBoltMessage(conn net.Conn, msg []byte) error {
	sizeBuf := make([]byte, 2)
	binary.BigEndian.PutUint16(sizeBuf, uint16(len(msg)))
	if _, err := conn.Write(sizeBuf); err != nil {
		return err
	}
	if _, err := conn.Write(msg); err != nil {
		return err
	}
	if _, err := conn.Write([]byte{0x00, 0x00}); err != nil {
		return err
	}
	return nil
}

// extractRunQuery tries to extract the Cypher query string from a Bolt RUN message.
// Bolt RUN message structure (PackStream):
//   - Marker byte 0xB1..0xBF (tiny struct) or 0xDC/0xDD
//   - Signature byte 0x10 (RUN)
//   - First field: the query string
//
// Returns the query and true if this is a RUN message, otherwise ("", false).
func extractRunQuery(msg []byte) (string, bool) {
	if len(msg) < 3 {
		return "", false
	}

	marker := msg[0]
	var sigIdx int

	if marker >= 0xB0 && marker <= 0xBF {
		sigIdx = 1
	} else if marker == 0xDC {
		sigIdx = 2
	} else if marker == 0xDD {
		sigIdx = 3
	} else {
		return "", false
	}

	if sigIdx >= len(msg) {
		return "", false
	}

	sig := msg[sigIdx]
	if sig != 0x10 {
		return "", false
	}

	strStart := sigIdx + 1
	if strStart >= len(msg) {
		return "", false
	}

	str, ok := readPackStreamString(msg[strStart:])
	if !ok {
		return "", false
	}

	return str, true
}

// readPackStreamString reads a PackStream-encoded string from buf.
func readPackStreamString(buf []byte) (string, bool) {
	if len(buf) == 0 {
		return "", false
	}

	marker := buf[0]

	if marker >= 0x80 && marker <= 0x8F {
		length := int(marker & 0x0F)
		if len(buf) < 1+length {
			return "", false
		}
		return string(buf[1 : 1+length]), true
	}

	if marker == 0xD0 {
		if len(buf) < 2 {
			return "", false
		}
		length := int(buf[1])
		if len(buf) < 2+length {
			return "", false
		}
		return string(buf[2 : 2+length]), true
	}

	if marker == 0xD1 {
		if len(buf) < 3 {
			return "", false
		}
		length := int(binary.BigEndian.Uint16(buf[1:3]))
		if len(buf) < 3+length {
			return "", false
		}
		return string(buf[3 : 3+length]), true
	}

	if marker == 0xD2 {
		if len(buf) < 5 {
			return "", false
		}
		length := int(binary.BigEndian.Uint32(buf[1:5]))
		if len(buf) < 5+length {
			return "", false
		}
		return string(buf[5 : 5+length]), true
	}

	return "", false
}

// sendFailure sends a Bolt FAILURE message to the client.
// FAILURE is struct with signature 0x7F, containing a map with "code" and "message".
func sendFailure(conn net.Conn, message string) {
	code := "ComptoxAI.Proxy.WriteNotAllowed"

	var buf []byte
	buf = append(buf, 0xB1)
	buf = append(buf, 0x7F)
	buf = append(buf, 0xA2)
	buf = append(buf, packString("code")...)
	buf = append(buf, packString(code)...)
	buf = append(buf, packString("message")...)
	buf = append(buf, packString(message)...)

	_ = writeBoltMessage(conn, buf)
}

// packString encodes a string in PackStream format.
func packString(s string) []byte {
	l := len(s)
	var buf []byte

	if l <= 15 {
		buf = append(buf, byte(0x80|l))
	} else if l <= 255 {
		buf = append(buf, 0xD0, byte(l))
	} else if l <= 65535 {
		buf = append(buf, 0xD1)
		b := make([]byte, 2)
		binary.BigEndian.PutUint16(b, uint16(l))
		buf = append(buf, b...)
	} else {
		buf = append(buf, 0xD2)
		b := make([]byte, 4)
		binary.BigEndian.PutUint32(b, uint32(l))
		buf = append(buf, b...)
	}

	buf = append(buf, []byte(s)...)
	return buf
}
