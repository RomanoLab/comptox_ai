variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "admin_ssh_cidr" {
  description = "CIDR allowed to SSH to both hosts (your home/office IP, e.g. 198.51.100.7/32)"
  type        = string
}

variable "key_pair_name" {
  description = "Name of an existing EC2 key pair for SSH access"
  type        = string
}

variable "db_instance_type" {
  description = "Instance type for the Memgraph host. r7g.large = 2 vCPU / 16 GB RAM."
  type        = string
  default     = "r7g.large"
}

variable "app_instance_type" {
  description = "Instance type for the API/Lab/Caddy host."
  type        = string
  default     = "t4g.small"
}

variable "db_volume_size_gb" {
  description = "Root EBS volume size on the DB host (gp3)."
  type        = number
  default     = 100
}

variable "app_volume_size_gb" {
  description = "Root EBS volume size on the app host (gp3)."
  type        = number
  default     = 20
}

variable "git_ref" {
  description = "Branch or tag of comptox_ai to clone on first boot."
  type        = string
  default     = "master"
}

variable "git_repo" {
  description = "Git URL of the comptox_ai repo."
  type        = string
  default     = "https://github.com/JDRomano2/comptox_ai.git"
}

variable "ec2_instance_profile_name" {
  description = <<EOT
Name of a pre-existing EC2 instance profile to attach to both hosts.
This is created out-of-band by an account admin (see
infra/terraform/README.md). The wrapped IAM role must have the
AmazonSSMManagedInstanceCore managed policy and an inline policy
permitting writes to s3://comptoxai-backups-<account_id>.
EOT
  type        = string
  default     = "comptoxai-ec2"
}
