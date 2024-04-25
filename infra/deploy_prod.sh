#!/bin/bash
# Take the current staging image, tag it as latest, and deploy it to the production instance.

source .env
gcloud config set project $GOOGLE_CLOUD_PROJECT
gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT

gcloud container images add-tag gcr.io/$GOOGLE_CLOUD_PROJECT/app:staging gcr.io/$GOOGLE_CLOUD_PROJECT/app:latest
gcloud run deploy app --image gcr.io/$GOOGLE_CLOUD_PROJECT/app:latest