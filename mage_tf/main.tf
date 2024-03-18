# Serverless VPC Access Admin
# Compute Admin

# main.tf

terraform {
  required_version = ">= 0.14"

  required_providers {
    # Cloud Run support was added on 3.3.0
    google = ">= 3.3"
  }
}

provider "google" {
  credentials = file(var.credentials)
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

provider "google-beta" {
  credentials = file(var.credentials)
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# #############################################
# #               Enable API's                #
# #############################################
# Enable IAM API
resource "google_project_service" "iam" {
  service            = "iam.googleapis.com"
  disable_on_destroy = false
}

# Enable Artifact Registry API
resource "google_project_service" "artifactregistry" {
  service            = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

# Enable Cloud Run API
resource "google_project_service" "cloudrun" {
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

# Enable Cloud Resource Manager API
resource "google_project_service" "resourcemanager" {
  service            = "cloudresourcemanager.googleapis.com"
  disable_on_destroy = false
}

# Enable VCP Access API
resource "google_project_service" "vpcaccess" {
  service            = "vpcaccess.googleapis.com"
  disable_on_destroy = false
}

# Enable Secret Manager API
resource "google_project_service" "secretmanager" {
  service            = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

# Enable Cloud SQL Admin API
resource "google_project_service" "sqladmin" {
  service            = "sqladmin.googleapis.com"
  disable_on_destroy = false
}


# Create the Cloud Run service
resource "google_cloud_run_service" "run_service" {
  provider = google-beta
  name     = var.app_name
  location = var.region

  template {
    spec {
      containers {
        image = var.docker_image
        ports {
          container_port = 6789
        }
        resources {
          limits = {
            cpu    = var.container_cpu
            memory = var.container_memory
          }
        }
        env {
          name  = "FILESTORE_IP_ADDRESS"
          value = module.nfs.internal_ip
        }
        env {
          name  = "FILE_SHARE_NAME"
          value = "share/mage"
        }
        env {
          name  = "GCP_PROJECT_ID"
          value = var.project_id
        }
        env {
          name  = "GCP_REGION"
          value = var.region
        }
        env {
          name  = "GCP_SERVICE_NAME"
          value = var.app_name
        }
        env {
          name  = "ULIMIT_NO_FILE"
          value = 16384
        }
        env {
          name  = "MAGE_DATABASE_CONNECTION_URL"
          value = "postgresql://${var.database_user}:${var.database_password}@/${var.app_name}-db?host=/cloudsql/${google_sql_database_instance.instance.connection_name}"
        }

        # volume_mounts {
        #   mount_path = "/secrets/bigquery"
        #   name       = "secret-bigquery-key"
        # }
      }
      # volumes {
      #   name = "secret-bigquery-key"
      #   secret {
      #     secret_name  = "bigquery_key"
      #     items {
      #       key  = "latest"
      #       path = "bigquery_key"
      #     }
      #   }
      # }
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale"         = "1"
        "run.googleapis.com/cpu-throttling"        = false
        "run.googleapis.com/execution-environment" = "gen2"
        "run.googleapis.com/vpc-access-connector"  = google_vpc_access_connector.connector.id
        "run.googleapis.com/vpc-access-egress"     = "private-ranges-only"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  metadata {
    annotations = {
      "run.googleapis.com/launch-stage" = "BETA"
    }
  }

  autogenerate_revision_name = true

  # Waits for the Cloud Run API to be enabled
  depends_on = [google_project_service.cloudrun]
}

# Allow unauthenticated users to invoke the service
resource "google_cloud_run_service_iam_member" "run_all_users" {
  service  = google_cloud_run_service.run_service.name
  location = google_cloud_run_service.run_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
