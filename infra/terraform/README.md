# ComptoxAI AWS infrastructure (Terraform)

Two-host EC2 deployment in the default VPC. App host fronts everything
public; DB host is internal-only (Memgraph + nightly S3 snapshots).

```
              Internet
                 │
        ┌────────┴────────┐
        │  EIP — app host │   t4g.small, 2 GB RAM
        │  ┌────────────┐ │   80, 443, 7687  (Caddy + bolt-proxy + API + Lab)
        │  │ Caddy      │ │
        │  │ bolt-proxy │ │
        │  │ API + Lab  │ │
        │  └─────┬──────┘ │
        └────────┼────────┘
                 │ bolt://<db-private-ip>:7687  (VPC internal, SG-restricted)
        ┌────────┴────────┐
        │  EIP — db host  │   r7g.large, 16 GB RAM
        │  ┌────────────┐ │   22 from admin IP, 7687 from app SG
        │  │ Memgraph   │ │   nightly snapshots → S3 (90-day retention)
        │  └────────────┘ │
        └─────────────────┘
```

## Files

| File | Purpose |
| --- | --- |
| `main.tf` | Provider, AMI lookup, IAM (one role, used by both hosts; SSM + S3 backup write) |
| `network.tf` | App SG (80/443/7687/22) + DB SG (7687 from app SG, 22 from admin) |
| `instances.tf` | Two EC2 instances + two Elastic IPs |
| `storage.tf` | Versioned, encrypted S3 bucket with lifecycle rules for snapshots |
| `variables.tf` / `outputs.tf` | Inputs and useful exports |
| `user-data/{db,app}-bootstrap.sh` | Cloud-init scripts that install Docker, clone the repo, and run the right Compose overlay |

## Apply it

You'll need an existing EC2 key pair; create one in the AWS console first.

```bash
cd infra/terraform
terraform init
terraform plan \
  -var "admin_ssh_cidr=$(curl -s https://checkip.amazonaws.com)/32" \
  -var "key_pair_name=your-key-pair"
terraform apply ...   # same vars
```

`terraform output` then prints the public IPs and the A records you need
to add at your DNS provider:

- `api.comptox.ai`  → app EIP
- `lab.comptox.ai`  → app EIP
- `bolt.comptox.ai` → app EIP

After the EIPs propagate, Caddy on the app host auto-provisions TLS for
all three subdomains on first request.

## Wire it into deploys

Set `EC2_INSTANCE_ID` in GitHub repo secrets to the value of
`terraform output app_instance_id`. The existing `.github/workflows/deploy.yml`
already targets that secret via SSM `Send-Command`.

For the DB host, you generally don't redeploy on git push — the database
state is the value, not the code. Treat it as a pet: SSH in for upgrades,
or extend `deploy.yml` with a manual `workflow_dispatch` job that targets
the DB instance ID for occasional `docker compose pull` runs.

## State

Local state by default — fine for one operator. To share state with a
teammate or with CI, uncomment the `backend "s3"` block in `main.tf`,
create the bucket+DynamoDB lock table out-of-band (one-shot `aws s3 mb`
and `aws dynamodb create-table`), then `terraform init -migrate-state`.

## Cost

At list price in `us-east-1`, 24/7:

| Item | Monthly |
| --- | --- |
| `r7g.large` (DB) | ~$78 |
| `t4g.small` (app) | ~$15 |
| 2× EIPs (in use, no charge) | $0 |
| 100 GB gp3 (DB) + 20 GB gp3 (app) | ~$10 |
| S3 backups (typical KG dump <500 MB, IA after 14d, 90d retention) | ~$1 |
| Data transfer (light) | ~$1 |
| **Total** | **~$105** |

Reserved-instance pricing for 1 year drops it to ~$80–90. You're well
under the $120 ceiling either way, leaving room for CloudWatch alarms or
a bigger DB volume if the graph grows.

## Tear-down

```bash
terraform destroy -var "admin_ssh_cidr=..." -var "key_pair_name=..."
```

The S3 bucket is *not* force-emptied on destroy by default. If you want
to nuke everything including snapshots, empty the bucket first
(`aws s3 rm s3://<bucket> --recursive`) or add `force_destroy = true` to
the bucket resource.
