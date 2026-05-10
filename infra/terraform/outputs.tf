output "app_public_ip" {
  description = "Public IP of the app host. Point api/lab/bolt.comptox.ai A records here."
  value       = aws_eip.app.public_ip
}

output "db_public_ip" {
  description = "Public IP of the db host (admin SSH only)."
  value       = aws_eip.db.public_ip
}

output "db_private_ip" {
  description = "VPC-internal IP that the app host uses to reach Memgraph."
  value       = aws_instance.db.private_ip
}

output "app_instance_id" {
  description = "App host instance ID — set as the EC2_INSTANCE_ID GitHub secret for deploy.yml."
  value       = aws_instance.app.id
}

output "db_instance_id" {
  description = "DB host instance ID — for SSM commands targeting the DB."
  value       = aws_instance.db.id
}

output "backup_bucket" {
  description = "S3 bucket holding nightly Memgraph snapshots."
  value       = aws_s3_bucket.backups.id
}

output "dns_records_to_create" {
  description = "Add these A records at your DNS provider."
  value = {
    "api.comptox.ai"  = aws_eip.app.public_ip
    "lab.comptox.ai"  = aws_eip.app.public_ip
    "bolt.comptox.ai" = aws_eip.app.public_ip
  }
}
