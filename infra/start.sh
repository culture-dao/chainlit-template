#!/bin/bash
source .env

gcloud projects create $GOOGLE_CLOUD_PROJECT
gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
gcloud config set project $GOOGLE_CLOUD_PROJECT