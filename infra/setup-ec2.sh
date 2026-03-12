#!/usr/bin/env bash
set -euo pipefail

# Setup script for ComptoxAI on Amazon Linux 2023 ARM64 (r7g.large)
# Run as root or with sudo.

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

echo "==> Done!"
echo ""
echo "Next steps:"
echo "  1. Log out and back in (for docker group)"
echo "  2. Clone the repo and cd into it"
echo "  3. docker compose up -d"
echo "  4. Point DNS for api.comptox.ai and lab.comptox.ai to this instance"
echo "  5. Caddy will auto-provision TLS certificates"
