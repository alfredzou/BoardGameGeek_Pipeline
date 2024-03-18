variable "credentials" {
    description = "My Credential Location"
    default = "~/.gcp/bgg.json"
}

variable "Project" {
    description = "My Project Name"
    default = "sharp-harbor-411301" 
}

variable "region" {
    description = "My Project Region"
    default = "australia-southeast1" 
}

variable "gcs_bucket_name" {
    description = "My Storage Bucket Name"
    default = "boardgamegeek-bucket"
}

variable "bq_dataset_name" {
    description = "My BigQuery Dataset Name"
    default = "boardgamegeek"
}

