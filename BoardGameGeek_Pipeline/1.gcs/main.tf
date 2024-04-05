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
  credentials = file(var.gcs_bq_credentials)
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

resource "google_storage_bucket" "bgg-dbt-bucket" {
  name          = var.dbt_gcs_bucket_name
  location      = var.region

  website {
    main_page_suffix = "index.html"
  }

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

resource "google_storage_bucket_iam_member" "bgg-dbt-bucket" {
  bucket = google_storage_bucket.bgg-dbt-bucket.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}