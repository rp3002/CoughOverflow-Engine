et -e

#  Use AWS credentials from credentials file
export AWS_SHARED_CREDENTIALS_FILE=./credentials
export AWS_CONFIG_FILE=./credentials
export AWS_PROFILE=default

#  Initialize Terraform
echo "Initializing Terraform..."
terraform init

#  Apply Terraform configuration
echo "Applying Terraform..."
terraform apply -auto-approve

#  Get Load Balancer DNS from Terraform output
echo "Writing API DNS to api.txt..."
API_URL=$(terraform output -raw coughoverflow_url)
echo "http://${API_URL}/api/v1" > api.txt

# Print final endpoint
echo "Deployed successfully at: http://${API_URL}/api/v1"

