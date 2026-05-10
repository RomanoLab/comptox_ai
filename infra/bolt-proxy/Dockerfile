FROM golang:1.22-alpine AS builder

WORKDIR /src
COPY go.mod ./
COPY go.su[m] ./
RUN go mod download 2>/dev/null || true

COPY *.go ./
RUN CGO_ENABLED=0 GOOS=linux go build -o /bolt-proxy .

FROM alpine:3.19
RUN apk add --no-cache ca-certificates wget
COPY --from=builder /bolt-proxy /usr/local/bin/bolt-proxy

EXPOSE 7688 8081

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -q -O- http://localhost:8081/healthz || exit 1

ENTRYPOINT ["bolt-proxy"]
