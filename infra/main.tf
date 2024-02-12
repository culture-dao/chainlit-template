provider "google" {
  project = "chainlit-test-413716"
  region  = "us-east4"
}

resource "google_cloud_run_service" "default" {
  name     = "chainlit-app"
  location = "us-east4"

  template {
    spec {
      containers {
        image = "gcr.io/chainlit-test-413716/chainlit-app:latest"

        ports {
          container_port = 8000  # Specify your application's port here
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
        env {
          name = "ASSISTANT_ID"
          value_from {
            secret_key_ref {
              name = "ASSISTANT_ID" # Name of your secret in Secret Manager
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
  location = google_cloud_run_service.default.location

  service  = google_cloud_run_service.default.name

  role   = "roles/run.invoker"
  member = "allUsers"
}
