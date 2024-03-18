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
  default     = "sharp-harbor-411301"
}

variable "region" {
  type        = string
  description = "The default compute region"
  default     = "australia-southeast1"
}

variable "zone" {
  type        = string
  description = "The default compute zone"
  default     = "australia-southeast1-b"
}

variable "docker_image" {
  type        = string
  description = "The docker image to deploy to Cloud Run."
  default     = "mageai/mageai:latest"
}

variable "domain" {
  description = "Domain name to run the load balancer on. Used if `ssl` is `true`."
  type        = string
  default     = ""
}

variable "ssl" {
  description = "Run load balancer on HTTPS and provision managed certificate with provided `domain`."
  type        = bool
  default     = false
}
