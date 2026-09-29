variable "bucket_name" {
  description = "Name of the bucket used by this example module"
  type        = string
  default     = "megalinter-example"
}

variable "versioning_enabled" {
  description = "Whether versioning is enabled on the bucket"
  type        = bool
  default     = true
}

locals {
  tags = {
    Name       = var.bucket_name
    Versioning = var.versioning_enabled ? "enabled" : "disabled"
  }
}

output "bucket_name" {
  description = "Name of the bucket"
  value       = var.bucket_name
}

output "tags" {
  description = "Tags computed for the bucket"
  value       = local.tags
}
