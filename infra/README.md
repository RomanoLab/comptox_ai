# ComptoxAI infrastructure

Single-host Docker Compose deployment on EC2 (Amazon Linux 2023, ARM64). All
services run on one box behind Caddy, which terminates TLS for HTTP and Bolt.

## Service map

```
┌──────────────────────── EC2 instance ────────────────────────┐
│                                                              │
│      ┌─────────────── Caddy (image: infra/caddy) ────────┐   │
│      │ :80 :443       layer4 :7687                       │   │
│      └─────────────────┬───────────┬────────────────────┘   │
│              api.comptox.ai     lab.comptox.ai     bolt.comptox.ai
│                        │              │                  │  │
│                ┌───────▼──────┐  ┌────▼─────┐    ┌──────▼─────┐
│                │   API (Node) │  │   Lab    │    │ bolt-proxy │
│                │   :3000      │  │ (web UI) │    │ :7688      │
│                └───────┬──────┘  └────┬─────┘    └──────┬─────┘
│                        │              │                 │
│                        └──────┬───────┴─────────────────┘
│                               │
│                       ┌───────▼────────┐
│                       │   Memgraph     │
│                       │   :7687 (int.) │
│                       └────────────────┘
└──────────────────────────────────────────────────────────────┘
```

Public ingress is **only** via Caddy. Memgraph's Bolt port (7687) is exposed
to the host network in dev (via `docker-compose.override.yml`) but NOT in
prod — production traffic must enter through Caddy → bolt-proxy, which
inspects RUN messages and rejects writes.

## Production bring-up

1. Provision an Amazon Linux 2023 ARM64 instance with an instance profile
   that has `AmazonSSMManagedInstanceCore` attached.
2. Set the security group inbound rules: 22 (admin IP), 80, 443, 7687.
3. Point DNS A records `api.comptox.ai`, `lab.comptox.ai`, `bolt.comptox.ai`
   at the instance's public IP.
4. SSH in and run `sudo ./infra/setup-ec2.sh`.
5. `cd /opt/comptox_ai && docker compose pull && docker compose up -d`.

## Updates from CI

The `deploy.yml` GitHub Actions workflow uses AWS SSM Send-Command to run:

```
cd /opt/comptox_ai && git pull && \
  IMAGE_TAG=sha-<commit> docker compose pull && \
  docker compose up -d --remove-orphans
```

The IAM role behind `AWS_DEPLOY_ROLE_ARN` needs an inline policy permitting
`ssm:SendCommand`, `ssm:GetCommandInvocation`, and
`ssm:DescribeInstanceInformation` against this instance.

The host instance ID goes into the `EC2_INSTANCE_ID` GitHub secret.

## Read-only enforcement

Memgraph Community Edition has no native read-only role. Instead:

- Memgraph's Bolt port (7687) is unreachable from the internet (Docker
  bridge network, no host port mapping in prod).
- All external traffic enters via `bolt.comptox.ai:7687`, which Caddy's
  layer4 module TLS-terminates and forwards to `bolt-proxy:7688` inside the
  Docker network.
- `bolt-proxy` (Go service in `infra/bolt-proxy/`) parses each Bolt
  RUN message, looks at the leading Cypher keyword, and returns a
  `ComptoxAI.Proxy.WriteNotAllowed` failure for `CREATE / MERGE / SET /
  DELETE / DETACH / REMOVE / DROP / LOAD / CALL <write proc>`.
- The API service connects directly to Memgraph (not through the proxy)
  because it is trusted application code; it issues only read queries by
  convention and pins `defaultAccessMode: READ` on its driver sessions.

## Local dev

```
docker compose up -d           # builds images, exposes 3000/3001/7687/7688
curl http://localhost:3001/health
python demo_queries.py          # runs the canonical query suite
```

`docker-compose.override.yml` is the dev profile and must NOT be present
on the production host.
