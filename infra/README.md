# Pre-requisites:
* Ensure you have a Google Cloud account and access to the chainlit-test project.
* Install and configure the Google Cloud SDK on your local machine.
* Install Terraform if it's not already installed.
* Ensure you have Poetry set up for your Python project.
* Familiarize yourself with Google Cloud Build for CI/CD pipelines.

# Quickstart

PROJECT_ID=andreyseas
gcloud projects create $PROJECT_ID
gcloud auth application-default set-quota-project $PROJECT_ID
gcloud config set project $PROJECT_ID

gcloud secrets create my-secret --replication-policy="automatic"
gcloud secrets versions add my-secret --data-file=../openai-assistant/.env 
