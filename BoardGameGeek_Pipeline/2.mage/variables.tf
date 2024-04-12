# Credentials
variable "gcs_bq_credentials" {
    description = "My Credential Location"
    default = "~/.gcp/gcs_bq.json"
}

variable "credentials" {
    description = "My Credential Location"
    default = "~/.gcp/mage.json"
}

# Change these
variable "project_id" {
  type        = string
  description = "The name of the project"
  default     = "crested-talon-417601"
}

variable "gcs_bucket_name" {
    description = "My Storage Bucket Name"
    default = "boardgamegeek-bucket1"
}

variable "dbt_gcs_bucket_name" {
    description = "My Storage Bucket Name"
    default = "boardgamegeek-bucket1-dbt"
}

# Keep default
variable "region" {
  type        = string
  description = "The default compute region"
  default     = "australia-southeast2"
}

variable "zone" {
  type        = string
  description = "The default compute zone"
  default     = "australia-southeast2-b"
}

variable "app_name" {
  type        = string
  description = "Application Name"
  default     = "mage"
}

variable "container_cpu" {
  description = "Container cpu"
  default     = "2000m"
}

variable "container_memory" {
  description = "Container memory"
  default     = "4G"
}

variable "docker_image" {
  type        = string
  description = "The docker image to deploy to Cloud Run."
  default     = "mageai/mageai:latest"
}

variable "dbt_profiles_dir" {
  type        = string
  description = "The path that dbt looks for profile.yml"
  default     = "/home/src/default_repo/dbt/bgg"
}

