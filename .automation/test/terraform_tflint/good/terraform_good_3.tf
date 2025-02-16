terraform {
  required_version = ">= 1.8.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.34.0" # https://registry.terraform.io/providers/hashicorp/google/latest
    }
  }
}

provider "google" {
  project = "my-project-id"
  region  = "us-central1"
}

resource "google_storage_bucket" "example" {
  name          = "my-bucket-${random_id.suffix.hex}"
  location      = "US"
  force_destroy = true

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}

resource "random_id" "suffix" {
  byte_length = 4
}
