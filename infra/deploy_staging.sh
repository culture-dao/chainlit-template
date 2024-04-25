#!/bin/bash

source .env
gcloud config set project $GOOGLE_CLOUD_PROJECT
gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT

cd ..
gcloud builds submit --config=cloudbuild.yaml --substitutions=_TAG_NAME=staging openai-assistant
gcloud run deploy staging --image gcr.io/$GOOGLE_CLOUD_PROJECT/app:staging