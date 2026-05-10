#!/usr/bin/env bash
# App host bootstrap. Runs once on first boot via cloud-init.
# Templated by Terraform — variables ${git_repo}, ${git_ref}, ${db_private_ip}.
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

# --- Source checkout --------------------------------------------------------
if [ ! -d /opt/comptox_ai ]; then
  git clone --branch "${git_ref}" --depth 1 "${git_repo}" /opt/comptox_ai
fi
chown -R ec2-user:ec2-user /opt/comptox_ai
rm -f /opt/comptox_ai/docker-compose.override.yml

# --- Pin the DB host's private IP so compose templating finds it ------------
cat > /opt/comptox_ai/.env <<EOF
DB_PRIVATE_IP=${db_private_ip}
EOF
chown ec2-user:ec2-user /opt/comptox_ai/.env

# --- Bring up everything except Memgraph ------------------------------------
cd /opt/comptox_ai
sudo -u ec2-user docker compose \
  -f docker-compose.yml \
  -f docker-compose.prod-app.yml \
  up -d
