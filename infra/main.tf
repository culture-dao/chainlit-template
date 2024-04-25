provider "google" {
  project = var.project
  region  = var.region
}

terraform {
  backend "gcs" {
    bucket  = ""
    prefix  = "terraform/state"
  }
}

resource "google_project_iam_member" "secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${var.project_id}-compute@developer.gserviceaccount.com"
}

resource "google_project_iam_member" "secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${var.project_id}-compute@developer.gserviceaccount.com"
}


resource "google_cloud_run_service" "staging" {
  name     = "staging"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project}/app:staging"

        ports {
          container_port = 8080  # Specify your application's port here
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

resource "google_cloud_run_domain_mapping" "staging" {
  location = var.region
  name     = "staging.yourdomain.com"

  metadata {

    namespace = var.project
  }

  spec {
    route_name = google_cloud_run_service.staging.name
  }
}