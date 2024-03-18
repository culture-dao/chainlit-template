source .env

cd ..
gcloud builds submit --config=cloudbuild.yaml app
# gcloud run deploy afge-staging --image gcr.io/afge-408215/afge-app:staging