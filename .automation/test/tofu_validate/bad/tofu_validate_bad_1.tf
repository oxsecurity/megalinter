variable "bucket_name" {
  description = "Name of the bucket used by this example module"
  type        = string
  default     = "megalinter-example"
}

locals {
  tags = {
    # Typo: there is no variable named bucket_nmae
    Name = var.bucket_nmae
  }
}

output "bucket_name" {
  description = "Name of the bucket"
  value       = var.bucket_name
}

# There is no local value named missing_tags
output "tags" {
  description = "Tags computed for the bucket"
  value       = local.missing_tags
}
