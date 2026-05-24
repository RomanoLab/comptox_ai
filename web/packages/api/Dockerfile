# Build context for this Dockerfile is the `web/` directory (the npm workspace
# root), not the api package itself, so the workspace-managed lock file is
# accessible. See docker-compose.yml and .github/workflows/publish-images.yml.
FROM node:26-alpine

RUN apk add --no-cache wget tini

WORKDIR /app

# Copy workspace manifests first for better layer caching.
COPY package.json package-lock.json ./
COPY packages/api/package.json packages/api/package.json

# Install only the api workspace's production deps. npm hoists shared deps
# to /app/node_modules; Node's resolution algorithm finds them from the
# nested workspace directory.
RUN npm ci --workspace=@comptoxai/comptox-api --omit=dev

# Now copy the api source.
COPY packages/api packages/api

WORKDIR /app/packages/api

USER node

EXPOSE 3001

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD wget -q -O- http://localhost:3001/health || exit 1

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "app.js"]
