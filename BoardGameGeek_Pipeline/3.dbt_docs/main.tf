terraform {
  required_version = ">= 0.14"

  required_providers {
    google = ">= 3.3"
  }
}

provider "google" {
  credentials = file(var.credentials)
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Create LB backend buckets
resource "google_compute_backend_bucket" "dbt_docs_be_bucket" {
  name        = "dbt-docs-be-bucket"
  description = "DBT docs backend bucket"
  bucket_name = var.dbt_gcs_bucket_name
}

# Create url map
resource "google_compute_url_map" "default" {
  name = "dbt-docs-http-lb"
  default_service = google_compute_backend_bucket.dbt_docs_be_bucket.id

  host_rule {
    hosts        = ["*"]
    path_matcher = "path-matcher-1"
  }
  path_matcher {
    name            = "path-matcher-1"
    default_service = google_compute_backend_bucket.dbt_docs_be_bucket.id
    }
}

# Create HTTP target proxy
resource "google_compute_target_http_proxy" "default" {
  name    = "dbt-docs-http-lb-proxy"
  url_map = google_compute_url_map.default.id
}

# Create forwarding rule
resource "google_compute_global_forwarding_rule" "default" {
  name                  = "dbt-docs-http-lb-forwarding-rule"
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL"
  port_range            = "80"
  target                = google_compute_target_http_proxy.default.id
}
