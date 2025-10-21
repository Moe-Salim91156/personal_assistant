#!/bin/bash

# Set the Terraform working directory
export TF_WORKING_DIR="/home/mohammad/Terraform_GCP/Project1"
echo -e "TERRAFORM DIRECTORY IS ${TF_WORKING_DIR}"
# Initialize Terraform
echo -e "initializing Terraform .. 1\n"
(cd "${TF_WORKING_DIR}" && terraform init)
echo -e $TF_WORKING_DIR

# Run Terraform Plan
echo -e "Running Terraform Plan ... 2\n"
(cd "${TF_WORKING_DIR}" && terraform plan)

# Ask for user confirmation to apply
read -r -p "APPLY ? (Y/N) : " answer
if [[ "${answer}" == "Y" || "${answer}" == "y" ]]; then
    echo -e "\nDEPLOYING INFRASTRUCTURE ... "
    (cd "${TF_WORKING_DIR}" && terraform apply --auto-approve)  
else
    echo "APPLY FAILED/CANCELED"
    exit 1 
fi

echo -e "\nBASH SCRIPT ENDED"


