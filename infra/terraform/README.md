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

---

## First-time deploy walkthrough

Do this once, in order. After this is done, day-to-day deploys are
automated by GitHub Actions (see "Going forward" at the bottom).

### Step 1 — Prerequisites you create in AWS by hand

These five things live outside Terraform because they're either
account-global, chicken-and-egg with Terraform itself, or specific to
your DNS provider.

**a. AWS CLI configured locally** with credentials that can create
EC2/IAM/S3 resources.

```bash
aws sts get-caller-identity   # should print your account ID, no error
```

**b. An EC2 key pair** for SSH into the hosts.

```bash
aws ec2 create-key-pair \
  --key-name comptoxai-admin \
  --query 'KeyMaterial' --output text > ~/.ssh/comptoxai-admin.pem
chmod 600 ~/.ssh/comptoxai-admin.pem
```

The name `comptoxai-admin` is what you'll pass to Terraform as
`key_pair_name`.

**c. A GitHub Actions OIDC role** so CI can deploy without long-lived
AWS keys. If you've ever made the static-site `deploy-site.yml` work,
this already exists in your account — its ARN is in your repo secrets
as `AWS_DEPLOY_ROLE_ARN`. Skip to step (c2).

If you've never set this up:

  1. AWS Console → IAM → Identity providers → **Add provider**
  2. Type: OpenID Connect, URL: `https://token.actions.githubusercontent.com`,
     audience: `sts.amazonaws.com`
  3. IAM → Roles → **Create role** → Web identity → that provider
  4. Trust policy condition:
     `token.actions.githubusercontent.com:sub` =
     `repo:JDRomano2/comptox_ai:*`
  5. Attach a permissions policy with: `s3:*` on your static-site bucket,
     `cloudfront:CreateInvalidation` on your distribution, plus the SSM
     actions in (c2) below.
  6. Save the role ARN as the `AWS_DEPLOY_ROLE_ARN` GitHub repo secret.

**c2. Extend that role with SSM permissions** so the new
`deploy.yml` workflow can `Send-Command` to the app host. Add this
inline policy to the existing role:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "ssm:SendCommand",
      "ssm:GetCommandInvocation",
      "ssm:DescribeInstanceInformation"
    ],
    "Resource": "*"
  }]
}
```

`Resource: "*"` is fine to start. You can scope it down to the app
instance ARN after step 2 if you want.

**d. A static-site S3 bucket and CloudFront distribution** (if you want
the docs+SPA at https://comptox.ai). Create per AWS docs; record the
bucket name and distribution ID as the `S3_BUCKET` and
`CLOUDFRONT_DIST_ID` repo secrets. Skip if you don't deploy a static
site.

**e. DNS access for `comptox.ai`.** Wherever you manage it (Route 53,
Cloudflare, registrar). You'll add three `A` records in step 4.

### Step 2 — Run Terraform

```bash
cd infra/terraform
terraform init
terraform apply \
  -var "admin_ssh_cidr=$(curl -s https://checkip.amazonaws.com)/32" \
  -var "key_pair_name=comptoxai-admin"
```

Type `yes` when prompted. Apply takes ~2 minutes.

What it creates:

| Resource | Purpose |
| --- | --- |
| `aws_instance.db` (`r7g.large`) | Memgraph |
| `aws_instance.app` (`t4g.small`) | API + Lab + bolt-proxy + Caddy |
| `aws_eip.{db,app}` | Stable public IPs so DNS records survive replacement |
| `aws_security_group.{db,app}` | DB locked to app SG + admin IP; app open on 80/443/7687 |
| `aws_iam_role.ec2` + instance profile | SSM agent + write to backup bucket |
| `aws_s3_bucket.backups` | Versioned, encrypted; 90-day lifecycle on snapshots |

Print the outputs:

```bash
terraform output
```

You'll need three of them:

- `app_instance_id` — for the `EC2_INSTANCE_ID` GitHub secret in step 3
- `app_public_ip` — for DNS in step 4
- `dns_records_to_create` — exact A records to add

### Step 3 — Add the EC2 instance ID as a GitHub secret

```bash
gh secret set EC2_INSTANCE_ID --body "$(terraform output -raw app_instance_id)"
```

(Or paste it in via the GitHub UI: repo → Settings → Secrets → Actions.)
This is what `.github/workflows/deploy.yml` targets via SSM.

### Step 4 — Add DNS A records

At your DNS provider, add three records pointing at
`terraform output -raw app_public_ip`:

```
api.comptox.ai     A  <app_public_ip>
lab.comptox.ai     A  <app_public_ip>
bolt.comptox.ai    A  <app_public_ip>
```

Wait a minute or two for propagation:

```bash
dig +short api.comptox.ai
```

### Step 5 — Wait for cloud-init to finish

The user-data scripts take 3-5 minutes per host to install Docker,
clone the repo, and bring up Compose. Watch the app host's progress:

```bash
ssh -i ~/.ssh/comptoxai-admin.pem \
    ec2-user@$(terraform output -raw app_public_ip) \
    'sudo tail -f /var/log/user-data.log'
```

You're done when you see `Container ... Started` lines for `caddy`,
`api`, `lab`, and `bolt-proxy`. Same on the DB host (replace IP) for
`memgraph`.

### Step 6 — Verify end-to-end

Caddy auto-provisions TLS on first request, so the first call to each
host might take ~5 seconds while the cert is issued.

```bash
# REST API
curl https://api.comptox.ai/health
# → {"status":"ok","db":"up"}

# Public Bolt over TLS (anonymous read)
python -c "from neo4j import GraphDatabase; \
  d=GraphDatabase.driver('neo4j+s://bolt.comptox.ai'); \
  print(list(d.session().run('MATCH (n) RETURN count(n) AS c')))"

# Confirm writes are rejected
python -c "from neo4j import GraphDatabase; \
  d=GraphDatabase.driver('neo4j+s://bolt.comptox.ai'); \
  list(d.session().run('CREATE (n:X)'))"
# → ClientError: ComptoxAI.Proxy.WriteNotAllowed
```

You're live.

---

## Going forward

After step 6, you don't run any of the steps above again unless you're
changing infra. The day-to-day flow is fully automated:

- **App or API code change** → push to `master` →
  `publish-images.yml` builds and pushes Docker images to GHCR →
  `deploy.yml` SSMs the app host to `docker compose pull && up -d`.
- **Docs or React-app change** → push to `master` →
  `deploy-site.yml` builds Sphinx + Vite and syncs to S3 + invalidates
  CloudFront.
- **Infra change** (instance type, SG, etc.) → edit the `.tf` files →
  `terraform apply`.

The DB host is treated as a pet, not cattle. You don't redeploy code to
it on every push — just SSH in for upgrades, or extend `deploy.yml` with
a `workflow_dispatch` job that targets `db_instance_id` for occasional
`docker compose pull`.

---

## Cost (us-east-1, list price, 24/7)

| Item | Monthly |
| --- | --- |
| `r7g.large` (DB) | ~$78 |
| `t4g.small` (app) | ~$15 |
| 2× EIPs (in use, no charge) | $0 |
| 100 GB gp3 (DB) + 20 GB gp3 (app) | ~$10 |
| S3 backups (typical KG dump <500 MB, IA after 14d, 90d retention) | ~$1 |
| Data transfer (light) | ~$1 |
| **Total** | **~$105** |

Reserved-instance pricing for 1 year drops it to ~$80–90.

---

## State management

Local state by default — fine for one operator. To share state with a
teammate or with CI, uncomment the `backend "s3"` block in `main.tf`,
create the bucket + DynamoDB lock table out-of-band (one-shot
`aws s3 mb` and `aws dynamodb create-table`), then
`terraform init -migrate-state`.

## Tear-down

```bash
terraform destroy \
  -var "admin_ssh_cidr=..." \
  -var "key_pair_name=..."
```

The S3 backup bucket isn't force-emptied on destroy. To nuke it too,
either empty it first (`aws s3 rm s3://<bucket> --recursive`) or add
`force_destroy = true` to the bucket resource in `storage.tf`.
