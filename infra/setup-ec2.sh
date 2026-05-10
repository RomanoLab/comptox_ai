#!/usr/bin/env bash
set -euo pipefail

# One-time setup script for the ComptoxAI host on Amazon Linux 2023 ARM64
# (r7g.large or similar). Run as root or with sudo.
#
# Prerequisites this script does NOT handle (do them before running):
#   1. EC2 security group inbound rules:
#        - 22  TCP from your admin IP only
#        - 80  TCP from 0.0.0.0/0   (Caddy HTTP -> ACME challenge / redirect)
#        - 443 TCP from 0.0.0.0/0   (Caddy HTTPS for api.comptox.ai, lab.comptox.ai)
#        - 7687 TCP from 0.0.0.0/0  (Caddy layer4 -> bolt-proxy, public Bolt+TLS)
#      Memgraph (7687 internal) and bolt-proxy (7688) MUST NOT be reachable
#      directly from the internet — only through Caddy.
#   2. IAM instance profile attached with the AmazonSSMManagedInstanceCore
#      managed policy so GitHub Actions can deploy via SSM Send-Command.
#   3. DNS A records: api.comptox.ai, lab.comptox.ai, bolt.comptox.ai → this host.

echo "==> Installing Docker..."
dnf install -y docker
systemctl enable --now docker
usermod -aG docker ec2-user

echo "==> Installing Docker Compose plugin..."
DOCKER_CONFIG=/usr/local/lib/docker
mkdir -p "$DOCKER_CONFIG/cli-plugins"
COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep '"tag_name"' | cut -d'"' -f4)
curl -SL "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-linux-aarch64" \
  -o "$DOCKER_CONFIG/cli-plugins/docker-compose"
chmod +x "$DOCKER_CONFIG/cli-plugins/docker-compose"

echo "==> Configuring 4GB swap..."
if [ ! -f /swapfile ]; then
    dd if=/dev/zero of=/swapfile bs=1M count=4096
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile swap swap defaults 0 0' >> /etc/fstab
fi

echo "==> Ensuring SSM agent is running..."
systemctl enable --now amazon-ssm-agent || \
    echo "  (amazon-ssm-agent not preinstalled; install via dnf or AMI selection)"

echo "==> Cloning repo to /opt/comptox_ai..."
if [ ! -d /opt/comptox_ai ]; then
    git clone https://github.com/JDRomano2/comptox_ai.git /opt/comptox_ai
fi
chown -R ec2-user:ec2-user /opt/comptox_ai

echo "==> Removing dev-only override on production host..."
rm -f /opt/comptox_ai/docker-compose.override.yml

echo "==> Done!"
echo ""
echo "Next steps:"
echo "  1. Log out and back in (for docker group membership to apply)"
echo "  2. cd /opt/comptox_ai"
echo "  3. docker login ghcr.io -u <gh-user> --password-stdin <<< \$GHCR_TOKEN"
echo "     (only needed if the packages are private; public packages are pull-anonymous)"
echo "  4. docker compose pull && docker compose up -d"
echo "  5. Caddy auto-provisions TLS certs for api/lab/bolt.comptox.ai on first request."
echo "  6. Verify:"
echo "       curl -fsS https://api.comptox.ai/health"
echo "       openssl s_client -servername bolt.comptox.ai -connect bolt.comptox.ai:7687 < /dev/null"
echo "  7. Capture this host's instance ID for the EC2_INSTANCE_ID GitHub secret:"
echo "       curl -s http://169.254.169.254/latest/meta-data/instance-id"
