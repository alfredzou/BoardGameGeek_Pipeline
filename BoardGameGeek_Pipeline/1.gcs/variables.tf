# Credentials
variable "gcs_bq_credentials" {
    description = "My Credential Location"
    default = "~/.gcp/gcs_bq.json"
}

# Change these
variable "Project" {
    description = "My Project Name"
    default = "crested-talon-417601" 
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
    description = "My Project Region"
    default = "australia-southeast2" 
}