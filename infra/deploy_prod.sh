GOOGLE_CLOUD_PROJECT=afge-408215
GOOGLE_CLOUD_REGION=us-east4

gcloud container images add-tag gcr.io/$GOOGLE_CLOUD_PROJECT/afge-app:staging gcr.io/$GOOGLE_CLOUD_PROJECT/afge-app:latest

gcloud run deploy afge-app --image gcr.io/afge-408215/afge-app:latest