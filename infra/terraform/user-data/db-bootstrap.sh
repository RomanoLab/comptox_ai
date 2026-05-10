#!/usr/bin/env bash
# DB host bootstrap. Runs once on first boot via cloud-init.
# Templated by Terraform — variables ${git_repo}, ${git_ref}, ${backup_bucket}.
set -euxo pipefail
exec > >(tee /var/log/user-data.log) 2>&1

# --- Docker + Compose -------------------------------------------------------
dnf install -y docker git
systemctl enable --now docker
usermod -aG docker ec2-user

mkdir -p /usr/local/lib/docker/cli-plugins
COMPOSE_VERSION=$(curl -fsSL https://api.github.com/repos/docker/compose/releases/latest | grep '"tag_name"' | cut -d'"' -f4)
curl -fsSL "https://github.com/docker/compose/releases/download/$${COMPOSE_VERSION}/docker-compose-linux-aarch64" \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# --- Swap (Memgraph occasionally bursts past RAM during imports) ------------
if [ ! -f /swapfile ]; then
  dd if=/dev/zero of=/swapfile bs=1M count=4096
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile swap swap defaults 0 0' >> /etc/fstab
fi

# --- Source checkout --------------------------------------------------------
if [ ! -d /opt/comptox_ai ]; then
  git clone --branch "${git_ref}" --depth 1 "${git_repo}" /opt/comptox_ai
fi
chown -R ec2-user:ec2-user /opt/comptox_ai

# Production: never use the dev override.
rm -f /opt/comptox_ai/docker-compose.override.yml

# --- Nightly backup to S3 ---------------------------------------------------
# Dumps the graph to gzipped Cypher and uploads to s3://${backup_bucket}/memgraph/.
# Lifecycle on the bucket transitions to IA after 14d and expires at 90d.
cat > /usr/local/bin/comptoxai-backup <<'BACKUP_EOF'
#!/usr/bin/env bash
set -euo pipefail
ts=$(date -u +%Y-%m-%dT%H-%M-%SZ)
out="/tmp/memgraph-$${ts}.cypher.gz"
docker exec memgraph mgconsole --execute "DUMP DATABASE;" 2>/dev/null \
  | gzip > "$${out}"
aws s3 cp "$${out}" "s3://${backup_bucket}/memgraph/memgraph-$${ts}.cypher.gz" --no-progress
rm -f "$${out}"
BACKUP_EOF
chmod +x /usr/local/bin/comptoxai-backup

cat > /etc/cron.d/comptoxai-backup <<EOF
# Nightly Memgraph snapshot at 03:15 UTC
15 3 * * * root /usr/local/bin/comptoxai-backup >> /var/log/comptoxai-backup.log 2>&1
EOF
chmod 644 /etc/cron.d/comptoxai-backup

# --- Bring up just Memgraph -------------------------------------------------
# The compose-prod-db.yml overlay disables app/lab/proxy/caddy so this host
# only runs the database.
cd /opt/comptox_ai
sudo -u ec2-user docker compose \
  -f docker-compose.yml \
  -f docker-compose.prod-db.yml \
  up -d
