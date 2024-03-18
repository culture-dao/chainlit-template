source .env
gcloud config set project $GOOGLE_CLOUD_PROJECT
gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT

gcloud container images add-tag gcr.io/$GOOGLE_CLOUD_PROJECT/afge-app:staging gcr.io/$GOOGLE_CLOUD_PROJECT/afge-app:latest

gcloud run deploy afge-app --image gcr.io/afge-408215/afge-app:latestage gcr.io/afge-408215/afge-app:latest