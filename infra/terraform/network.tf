# Two security groups. The app host fronts everything public; the db host
# only accepts Bolt from the app SG and SSH from the admin IP.

# ----- App host SG ---------------------------------------------------------

resource "aws_security_group" "app" {
  name        = "${local.name}-app"
  description = "ComptoxAI app host (API, Lab, bolt-proxy, Caddy)"
  vpc_id      = data.aws_vpc.default.id
  tags        = merge(local.tags, { Name = "${local.name}-app" })
}

resource "aws_vpc_security_group_ingress_rule" "app_http" {
  security_group_id = aws_security_group.app.id
  description       = "HTTP — ACME challenges + redirect to HTTPS"
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "app_https" {
  security_group_id = aws_security_group.app.id
  description       = "HTTPS — api.comptox.ai and lab.comptox.ai"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "app_bolt_tls" {
  security_group_id = aws_security_group.app.id
  description       = "Public Bolt+TLS via Caddy layer4 -> bolt-proxy"
  ip_protocol       = "tcp"
  from_port         = 7687
  to_port           = 7687
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "app_ssh" {
  security_group_id = aws_security_group.app.id
  description       = "Admin SSH"
  ip_protocol       = "tcp"
  from_port         = 22
  to_port           = 22
  cidr_ipv4         = var.admin_ssh_cidr
}

resource "aws_vpc_security_group_egress_rule" "app_egress" {
  security_group_id = aws_security_group.app.id
  description       = "All egress"
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}

# ----- DB host SG ----------------------------------------------------------

resource "aws_security_group" "db" {
  name        = "${local.name}-db"
  description = "ComptoxAI db host (Memgraph) — internal only"
  vpc_id      = data.aws_vpc.default.id
  tags        = merge(local.tags, { Name = "${local.name}-db" })
}

resource "aws_vpc_security_group_ingress_rule" "db_bolt_from_app" {
  security_group_id            = aws_security_group.db.id
  description                  = "Bolt from app host SG only"
  ip_protocol                  = "tcp"
  from_port                    = 7687
  to_port                      = 7687
  referenced_security_group_id = aws_security_group.app.id
}

resource "aws_vpc_security_group_ingress_rule" "db_ssh" {
  security_group_id = aws_security_group.db.id
  description       = "Admin SSH"
  ip_protocol       = "tcp"
  from_port         = 22
  to_port           = 22
  cidr_ipv4         = var.admin_ssh_cidr
}

resource "aws_vpc_security_group_egress_rule" "db_egress" {
  security_group_id = aws_security_group.db.id
  description       = "All egress (Docker pulls, S3 backups, package updates)"
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}
