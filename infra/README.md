# Infrastructure As Code

We use Terraform to manage our Google resources, we've got scripts to build our Docker image and deploy it to staging cloud run instance, as well as one to deploy to production. We've attempted to keep everything as dynamic as possible, but we've had to make changes from our last production run, and we haven't templated it quite all the way through. There may be some inconsistencies due to us trying to anonymize the project, so feel free to file an issue if you need help, or a PR if you have some contributions. 

## Pre-requisites:
* Ensure you have a Google Cloud account and access to your project.
* Install and configure the Google Cloud SDK on your local machine.
* Install Terraform if it's not already installed.
* Ensure you have Poetry set up for your Python project.
* Familiarize yourself with Google Cloud Build for CI/CD pipelines.

