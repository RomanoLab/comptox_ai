# EC2 instances + Elastic IPs.
#
# The DB instance is created first so the app's user-data can be templated
# with the DB host's stable private IP. The app then reaches Memgraph at
# bolt://<db_private_ip>:7687 over the VPC.

resource "aws_instance" "db" {
  ami                    = data.aws_ami.al2023_arm.id
  instance_type          = var.db_instance_type
  subnet_id              = data.aws_subnets.default.ids[0]
  vpc_security_group_ids = [aws_security_group.db.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2.name
  key_name               = var.key_pair_name

  user_data = templatefile("${path.module}/user-data/db-bootstrap.sh", {
    git_repo      = var.git_repo
    git_ref       = var.git_ref
    backup_bucket = aws_s3_bucket.backups.id
  })

  root_block_device {
    volume_type = "gp3"
    volume_size = var.db_volume_size_gb
    encrypted   = true
  }

  tags = merge(local.tags, {
    Name = "${local.name}-db"
    Role = "db"
  })
}

resource "aws_instance" "app" {
  ami                    = data.aws_ami.al2023_arm.id
  instance_type          = var.app_instance_type
  subnet_id              = data.aws_subnets.default.ids[0]
  vpc_security_group_ids = [aws_security_group.app.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2.name
  key_name               = var.key_pair_name

  user_data = templatefile("${path.module}/user-data/app-bootstrap.sh", {
    git_repo      = var.git_repo
    git_ref       = var.git_ref
    db_private_ip = aws_instance.db.private_ip
  })

  root_block_device {
    volume_type = "gp3"
    volume_size = var.app_volume_size_gb
    encrypted   = true
  }

  tags = merge(local.tags, {
    Name = "${local.name}-app"
    Role = "app"
  })

  depends_on = [aws_instance.db]
}

# Stable public IPs so DNS records survive reboots and replacements.
resource "aws_eip" "db" {
  instance = aws_instance.db.id
  tags     = merge(local.tags, { Name = "${local.name}-db" })
}

resource "aws_eip" "app" {
  instance = aws_instance.app.id
  tags     = merge(local.tags, { Name = "${local.name}-app" })
}
