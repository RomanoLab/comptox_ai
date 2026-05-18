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
# IAM — the instance profile is created out-of-band by an account admin
# because federated identities at most institutions can't run
# iam:CreateRole / iam:CreateInstanceProfile themselves. We look it up by
# name (var.ec2_instance_profile_name, default "comptoxai-ec2") and pass
# the resulting ARN to the EC2 instances in instances.tf.
#
# The profile's wrapped role must have:
#   - AmazonSSMManagedInstanceCore  (so SSM agent can register)
#   - inline policy granting PutObject/ListBucket/GetBucketLocation on
#     arn:aws:s3:::comptoxai-backups-<account_id> (for nightly backups)
# ---------------------------------------------------------------------------

data "aws_iam_instance_profile" "ec2" {
  name = var.ec2_instance_profile_name
}
