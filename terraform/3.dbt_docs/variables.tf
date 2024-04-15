# Credentials
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

