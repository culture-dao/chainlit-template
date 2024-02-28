#!/bin/bash

# TODO: Get this from infra env
GOOGLE_CLOUD_PROJECT=chainlit-test-413716
gcloud config set project $GOOGLE_CLOUD_PROJECT
gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT


# Path to your .env file
ENV_FILE="../openai-assistant/.env"

# Read each line in the .env file
while IFS='=' read -r key value; do
  if [[ ! -z "$key" ]]; then
    # Check if the secret already exists
    if ! gcloud secrets describe "$key" &>/dev/null; then
      # Create the secret if it doesn't exist
      gcloud secrets create "$key" --replication-policy="automatic"
    fi

    # Add the secret value as a new version
    echo -n "$value" | gcloud secrets versions add "$key" --data-file=-
  fi
done < "$ENV_FILE"
