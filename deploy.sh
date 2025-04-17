#!/bin/bash
set -e

# Export AWS credentials from file
export AWS_SHARED_CREDENTIALS_FILE=./credentials
export AWS_CONFIG_FILE=./credentials
export AWS_PROFILE=default

echo "Initializing Terraform..."
terraform init

echo "Applying Terraform..."
terraform apply -auto-approve

echo "Writing API DNS to api.txt..."
API_URL=$(terraform output -raw coughoverflow_url)
echo "http://${API_URL}/api/v1" > api.txt

echo "Deployed successfully at: http://${API_URL}/api/v1"

