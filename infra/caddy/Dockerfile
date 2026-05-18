# Caddy with the layer4 module so we can TLS-terminate raw TCP for Bolt
# (bolt.comptox.ai:7687) and forward the cleartext stream to bolt-proxy:7688.
FROM caddy:2.10-builder AS builder

RUN xcaddy build \
    --with github.com/mholt/caddy-l4

FROM caddy:2.10-alpine

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
