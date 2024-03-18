variable "credentials" {
    description = "My Credential Location"
    default = "~/.gcp/gcs_bq.json"
}

variable "Project" {
    description = "My Project Name"
    default = "crested-talon-417601" 
}

variable "region" {
    description = "My Project Region"
    default = "australia-southeast2" 
}

variable "gcs_bucket_name" {
    description = "My Storage Bucket Name"
    default = "boardgamegeek-bucket1"
}

variable "bq_dataset_name" {
    description = "My BigQuery Dataset Name"
    default = "boardgamegeek"
}

