# chainlit-template
#### Chainlit example app using Terraform, Google Cloud Run, and OpenAI's Assistants API

## Purpose

This is a demo repo for some of the work that we've been doing lately. It's our starting point for deploying chainlit app and it is very much a WIP. We're trying to capture all the steps needed to get up and running, but there's still a lot of stuff that we're figuring out. There's some tech debt, to say the least. 

Right now we're using OpenAI's Assistants API. We've found it to be the fastest way to prototype RAG apps, although it's not perfect. We would like to expand to other models and APIs in the future, but this is where we're at. 

We deploy to Google Cloud Run, we've got Terraform state stored in a bucket, and use Cloudbuild to manage our Docker image, which we deploy to staging and production instances. 

Our app uses Google Auth, which you'll have to set up yourself. Those get passed as Terraform variables in our production repo, but we don't have them integrated here yet. 

We've also added Discord webhooks for user login events, as well as a callback to Mailchimp to add users to our mailing list. 

/infra: holds the Terraform config files and batch scripts
/literal: A simple wrapper to help us clean up our dev instances when we need to purge. 
/openai-assistant: Our current implementation of the OpenAI Assistant API.