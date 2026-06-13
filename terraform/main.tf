# ==========================================
# Terraform Main Configuration
# ==========================================

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Local state backend for simplicity.
  # For team environments, configure a remote S3 backend with DynamoDB locking.
  backend "local" {
    path = "terraform.tfstate"
  }
}

# ==========================================
# Provider Definition & Default Tags
# ==========================================
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "Secure-Cloud-Native-CICD"
      ManagedBy   = "Terraform"
      Environment = var.environment
    }
  }
}
