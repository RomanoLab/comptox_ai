FROM golang:1.22-alpine AS builder

WORKDIR /src
COPY go.mod ./
# If go.sum exists, copy it too
COPY go.su[m] ./
RUN go mod download 2>/dev/null || true

COPY *.go ./
RUN CGO_ENABLED=0 GOOS=linux go build -o /bolt-proxy .

FROM alpine:3.19
RUN apk add --no-cache ca-certificates
COPY --from=builder /bolt-proxy /usr/local/bin/bolt-proxy

EXPOSE 7688
ENTRYPOINT ["bolt-proxy"]
