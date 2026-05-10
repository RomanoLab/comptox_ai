# ComptoxAI two-host AWS deployment.
#
# Two EC2 instances in the default VPC:
#   - db host (r7g.large)  : Memgraph only, no public ingress except SSH from admin IP
#   - app host (t4g.small) : API + Lab + bolt-proxy + Caddy. Single public ingress point.
#
# All traffic from the internet enters via the app host. The app host
# connects to the db host on port 7687 over the VPC private network.
#
# Run with:
#   cd infra/terraform
#   terraform init
#   terraform apply -var="admin_ssh_cidr=YOUR.IP.HERE/32" -var="key_pair_name=your-key"

terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.60"
    }
  }

  # To share state across machines, replace this with an S3 backend:
  #   backend "s3" {
  #     bucket = "comptoxai-tfstate"
  #     key    = "prod/terraform.tfstate"
  #     region = "us-east-1"
  #   }
}

provider "aws" {
  region = var.region
}

data "aws_caller_identity" "current" {}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Latest Amazon Linux 2023 ARM64 AMI.
data "aws_ami" "al2023_arm" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-arm64"]
  }
  filter {
    name   = "architecture"
    values = ["arm64"]
  }
  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

locals {
  name = "comptoxai"
  tags = {
    Project = "ComptoxAI"
    Managed = "terraform"
  }
}

# ---------------------------------------------------------------------------
# IAM — single instance role, used by both hosts. Grants:
#   - SSM agent registration (so deploy.yml's SSM Send-Command works)
#   - Write access to the backup S3 bucket (db host uses it; app host won't
#     exercise this in practice but having one role keeps the spec lean)
# ---------------------------------------------------------------------------

resource "aws_iam_role" "ec2" {
  name = "${local.name}-ec2"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
  tags = local.tags
}

resource "aws_iam_role_policy_attachment" "ssm_core" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy" "backup_writer" {
  name = "${local.name}-backup-writer"
  role = aws_iam_role.ec2.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:PutObject",
        "s3:ListBucket",
        "s3:GetBucketLocation",
      ]
      Resource = [
        aws_s3_bucket.backups.arn,
        "${aws_s3_bucket.backups.arn}/*",
      ]
    }]
  })
}

resource "aws_iam_instance_profile" "ec2" {
  name = "${local.name}-ec2"
  role = aws_iam_role.ec2.name
}
