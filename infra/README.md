# ComptoxAI infrastructure

This directory holds everything below the application layer: the Docker
images, Caddy config, bolt-proxy, EC2 setup script, and the Terraform
spec for the AWS deployment.

```
infra/
├── bolt-proxy/         Go service that filters Bolt RUN messages for writes
├── caddy/              Caddy + caddy-l4 plugin Dockerfile
├── terraform/          AWS infra-as-code (two-host EC2 deploy)
├── Caddyfile           api/lab/bolt subdomain config + layer4 Bolt-over-TLS
├── setup-ec2.sh        Manual single-host bootstrap (legacy; not used by terraform)
└── deploy-site.sh      Sphinx + Vite → S3 + CloudFront (called by deploy-site.yml)
```

## Production architecture

Two EC2 instances. **App host** fronts everything public (Caddy, API,
Lab, bolt-proxy). **DB host** is internal-only (Memgraph), reachable only
from the app host's security group on the VPC private network.

```
                    Internet
                       │
              ┌────────┴────────┐
              │  EIP — app host │   t4g.small
              │  Caddy ─────────┼── api.comptox.ai   :443  → api:3001
              │                 │── lab.comptox.ai   :443  → lab:3000
              │                 │── bolt.comptox.ai  :7687 → bolt-proxy:7688
              │                 │                            (TLS terminated
              │                 │                             at Caddy via
              │                 │                             layer4 module)
              └────────┬────────┘
                       │ bolt://<db-private-ip>:7687
              ┌────────┴────────┐
              │  EIP — db host  │   r7g.large, Memgraph only
              │  SG: app SG only on 7687, admin IP on 22
              └─────────────────┘
```

## How to deploy

**For first-time bring-up: see [`terraform/README.md`](terraform/README.md).**
That's the canonical walkthrough — what to set up in AWS by hand, what
Terraform creates, and the verify steps.

For day-to-day code deploys, the GitHub Actions workflows handle it:

| Workflow | Trigger | Effect |
| --- | --- | --- |
| `publish-images.yml` | push to `master` | builds API + bolt-proxy images, pushes to GHCR with `sha-<commit>` tag |
| `deploy.yml` | after `publish-images.yml` succeeds, or manual dispatch | SSM `Send-Command` to the app host: `git pull && docker compose pull && up -d` |
| `deploy-site.yml` | push to `master` touching `docs/` or `web/packages/app/` | Sphinx + Vite build, sync to S3, invalidate CloudFront |

## Read-only enforcement

Memgraph Community Edition has no native read-only role. Instead:

- Memgraph's Bolt port (7687) is unreachable from the internet — only the
  app host's security group can reach the DB host on that port over the
  VPC private network.
- External clients connect at `bolt.comptox.ai:7687`. Caddy's `layer4`
  module on the app host TLS-terminates and forwards to `bolt-proxy:7688`,
  which then dials the DB host's private IP.
- `bolt-proxy` (`infra/bolt-proxy/`) parses each Bolt RUN message, checks
  the leading Cypher keyword, and returns a `ComptoxAI.Proxy.WriteNotAllowed`
  failure for `CREATE / MERGE / SET / DELETE / DETACH / REMOVE / DROP /
  LOAD / CALL <write proc>`.
- The API connects directly to the DB host (bypassing bolt-proxy) because
  it's trusted application code. It pins `defaultAccessMode: READ` on
  driver sessions and issues only read queries by convention.

## Local dev (Compose, all services on one machine)

```
docker compose up -d            # builds dev images, exposes 3000/3001/7687/7688/8081
curl http://localhost:3001/health
python demo_queries.py
```

The `docker-compose.override.yml` brings up the dev variant of all five
services on one box. It must NOT be present on production hosts —
`infra/terraform/user-data/{db,app}-bootstrap.sh` deletes it on first boot.

For local dev *without* Compose (running API and React app via npm
against a host-local Memgraph), see `CONTRIBUTING.md` in the repo root.
