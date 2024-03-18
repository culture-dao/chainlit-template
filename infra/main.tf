provider "google" {
  project = var.project
  region  = var.region
}

terraform {
  backend "gcs" {
    bucket  = "clickmakersapp_tf_state"
    prefix  = "terraform/state"
  }
}

resource "google_cloud_run_service" "staging" {
  name     = "chainlit-app"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project}/chainlit-app:staging"

        ports {
          container_port = 80  # Specify your application's port here
        }
        # Inject environment variables
        env {
          name = "OPENAI_API_KEY"
          value_from {
            secret_key_ref {
              name = "OPENAI_API_KEY" # Name of your secret in Secret Manager
              key  = "latest" # Use "latest" or specify a version
            }
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_cloud_run_service_iam_member" "public_invoker" {
  location = google_cloud_run_service.staging.location

  service  = google_cloud_run_service.staging.name

  role   = "roles/run.invoker"
  member = "allUsers"
}
