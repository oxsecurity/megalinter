terraform {
  required_version = ">= 1.8.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.55.0" # https://registry.terraform.io/providers/hashicorp/aws/latest
    }
  }
}

provider "aws" {
  region = "us-west-2"
}

resource "aws_s3_bucket" "example" {
  bucket = "my-tf-test-bucket-${random_id.bucket_suffix.hex}"
}

resource "aws_s3_bucket_versioning" "example" {
  bucket = aws_s3_bucket.example.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}
