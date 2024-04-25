variable "project" {
  description = "The GCP project name."
  type        = string
}

variable "project_id" {
  description = "The GCP project number."
  type        = number
}
variable "region" {
  description = "The GCP region for resources."
  type        = string
}

variable "service_name" {
  description = "The name of the Cloud Run service."
  type        = string
}
