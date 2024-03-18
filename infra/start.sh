#!/bin/bash
source .env

# If new project:
# gcloud projects create $GOOGLE_CLOUD_PROJECT
gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
gcloud config set project $GOOGLE_CLOUD_PROJECT

# Set up billing and linked project account

# Create bucket for terraform state
bucketname="gs://${GOOGLE_CLOUD_PROJECT}_TF_STATE"
bucketname=$(echo "$bucketname" | tr '[:upper:]' '[:lower:]')

gcloud storage buckets create $bucketname --location=$GOOGLE_CLOUD_REGION
terraform init

# ENABLE CLOUD RUN ADMIN CLI: https://console.cloud.google.com/apis/api/run.googleapis.com/metrics
terraform apply --auto-approve