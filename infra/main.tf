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
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}
