variable "credentials" {
    description = "My Credential Location"
    default = "~/.gcp/mage.json"
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
  default     = "2G"
}

variable "project_id" {
  type        = string
  description = "The name of the project"
  default     = "crested-talon-417601"
}

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

variable "docker_image" {
  type        = string
  description = "The docker image to deploy to Cloud Run."
  default     = "mageai/mageai:latest"
}

variable "database_user" {
  type        = string
  description = "The username of the Postgres database."
  default     = "mage"
}

variable "database_password" {
  type        = string
  description = "The password of the Postgres database."
  default     = "mage"
}