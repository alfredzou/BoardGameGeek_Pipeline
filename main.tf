# Storage Admin
# BigQuery Admin

terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "5.20.0"
    }
  }
}

provider "google" {
  project     = var.Project
  credentials = file(var.credentials)
}

resource "google_storage_bucket" "bgg-bucket" {
  name          = var.gcs_bucket_name
  location      = var.region

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}