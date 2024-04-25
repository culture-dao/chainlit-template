#!/bin/bash
# This script will build a docker image of the app, tag it with the branch name, and deploy it to the staging instance.
# Eventually we want CI jobs to build branch endpoints as part of the PR process.

# Set the project
source .env
gcloud config set project $GOOGLE_CLOUD_PROJECT
gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT

# Get the current branch name
branch=$(git rev-parse --abbrev-ref HEAD)

# Convert to lowercase and replace non-alphanumeric characters with hyphens
formattedbranch=${branch//[^[:alnum:]]/-}
imagename=${formattedbranch:0:15}

# Build the Docker image
cd ..

gcloud builds submit --config=cloudbuild.yaml --substitutions=_TAG_NAME=$formattedbranch app
gcloud run deploy staging --image gcr.io/$GOOGLE_CLOUD_PROJECT/app:$formattedbranch