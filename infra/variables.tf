variable "project" {
  description = "The GCP project ID."
  type        = string
}

variable "region" {
  description = "The GCP region for resources."
  type        = string
}

variable "service_name" {
  description = "The name of the Cloud Run service."
  type        = string
}
