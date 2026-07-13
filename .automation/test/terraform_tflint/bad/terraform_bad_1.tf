terraform {
  required_version = ">= 1.8.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.55.0" # https://registry.terraform.io/providers/hashicorp/aws/latest
    }
  }
}

provider "template" {}

provider "aws" {
  region = "us-west-2"
}

resource "aws_s3_bucket" "example" {
   bucket = "my-tf-test-bucket-${random_id.bucket_suffix.hex}"
}

module "latest" {
  source  = "terraform-aws-modules/vpc/aws"
}

module "latest" {
  source  = "terraform-aws-modules/vpc/aws"
}

resource "aws_s3_bucket" "too_long" {
  bucket = "a-really-ultra-hiper-super-long-foo-bar-baz-bucket-name.domain.test"
}

resource "aws_s3_bucket" "too_long" {
  bucket = "a-really-ultra-hiper-super-long-foo-bar-baz-bucket-name.domain.test"
}
