#!/usr/bin/env bash

# ==============================================================================
# AWS Resource Cleanup & Shutdown Script (Bash)
# ==============================================================================
# This script completely tears down the AWS resources created by the project.
# It handles ECR image deletion (which blocks standard terraform destroy) 
# and runs Terraform destroy automatically.
# ==============================================================================

set -euo pipefail

# Configuration
APP_NAME="secure-aws-cicd-app"
TERRAFORM_DIR="$(dirname "$0")/../terraform"

echo "===================================================="
echo "🚨 AWS DevSecOps Pipeline Cleanup Script Started 🚨"
echo "===================================================="

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ Error: AWS CLI is not installed. Please install it to proceed."
    exit 1
fi

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "❌ Error: Terraform is not installed. Please install it to proceed."
    exit 1
fi

# Confirming deletion
read -p "⚠️  Are you sure you want to delete all resources for '$APP_NAME'? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cleanup canceled."
    exit 0
fi

# 1. Purge ECR Repository Images (Terraform cannot delete ECR if it has images)
echo "🧹 Step 1: Querying ECR images in repository '$APP_NAME'..."
if aws ecr describe-repositories --repository-names "$APP_NAME" &> /dev/null; then
    IMAGES=$(aws ecr list-images --repository-name "$APP_NAME" --query "imageIds" --output json)
    
    if [ "$IMAGES" != "[]" ] && [ -n "$IMAGES" ]; then
        echo "🗑️  Deleting ECR container images..."
        aws ecr batch-delete-image --repository-name "$APP_NAME" --image-ids "$IMAGES" &> /dev/null || true
        echo "✅ ECR container images purged successfully."
    else
        echo "ℹ️  ECR repository is already empty."
    fi
else
    echo "ℹ️  ECR repository '$APP_NAME' not found or already deleted."
fi

# 2. Run Terraform Destroy
echo "🧹 Step 2: Navigating to Terraform directory and destroying resources..."
if [ -d "$TERRAFORM_DIR" ]; then
    cd "$TERRAFORM_DIR"
    
    echo "🔄 Running terraform init..."
    terraform init
    
    echo "🔥 Destroying infrastructure..."
    terraform destroy -auto-approve
    echo "✅ Infrastructure destroyed successfully."
else
    echo "❌ Error: Terraform directory not found at $TERRAFORM_DIR"
    exit 1
fi

echo "===================================================="
echo "🎉 Cleanup completed successfully. $APP_NAME shutdown. 🎉"
echo "===================================================="
