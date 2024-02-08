# Pre-requisites:
* Ensure you have a Google Cloud account and access to the chainlit-test project.
* Install and configure the Google Cloud SDK on your local machine.
* Install Terraform if it's not already installed.
* Ensure you have Poetry set up for your Python project.
* Familiarize yourself with Google Cloud Build for CI/CD pipelines.

# Google Cloud APIs
```
gcloud services enable cloudbuild.googleapis.com`
gcloud services enable run.googleapis.com
```

Artifact Registry API					
Cloud Build API					
Cloud Logging API					
Cloud OS Login API					
Cloud Pub/Sub API
Cloud Resource Manager API
Compute Engine API					
Container Registry API					
Google Cloud Storage JSON API		


`gcloud config set project chainlit-test`

`gcloud builds submit --config=cloudbuild.yaml . --substitutions=_PROJECT_NAME="chainlit-test-413716"`