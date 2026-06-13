# Terraform Infrastructure as Code (IaC) Guide

This guide explains the Terraform architecture, variables, state management, and production enhancements for the **Secure Cloud-Native CI/CD Pipeline on AWS**.

---

## Infrastructure Directory Structure

```
terraform/
├── main.tf                 # Core configuration, provider definitions, local state backend
├── variables.tf            # Input variables declarations
├── outputs.tf              # Target outputs (ALB URL, ECR URL, IAM Roles)
├── vpc.tf                  # Custom VPC, public/private subnets, security groups, IGW & NAT
├── alb.tf                  # ALB, Target group with health checks, and Port 80 listener
├── ecs.tf                  # ECS Cluster, Task definition (Fargate), and Service configuration
├── ecr.tf                  # ECR repo, vulnerability scan, and image retention policy
├── iam.tf                  # ECS task execution, ECS task, and GitHub Actions OIDC roles
└── cloudwatch.tf           # Log groups and alarms (CPU, Memory threshold alerts)
```

---

## Component Configuration Review

### 1. The Cost Saving Toggle (`vpc.tf` & `ecs.tf`)
A key feature of this setup is the cost-saving optimization toggle `use_nat_gateway`.
* **Private Network (Standard Enterprise)**: `use_nat_gateway = true`
  * Deploys Fargate tasks into Private Subnets.
  * Launches 1 NAT Gateway in a Public Subnet ($32.40/mo base rate).
  * Outbound traffic routes from Fargate -> NAT Gateway -> Internet Gateway.
* **Public Network (Demo/Lab Optimization)**: `use_nat_gateway = false` (Default)
  * Deploys Fargate tasks into Public Subnets.
  * Assigns a Public IP address to Fargate tasks (`assign_public_ip = true`).
  * Outbound traffic routes from Fargate -> Internet Gateway directly.
  * Bypasses the NAT Gateway entirely, **reducing monthly baseline AWS costs by ~75%**.

### 2. IAM OIDC Security Federation (`iam.tf`)
The GitHub Actions pipeline communicates with AWS without a static, long-lived access key (e.g. `AKIA...`).
* **Identity Provider**: `aws_iam_openid_connect_provider.github` registers `https://token.actions.githubusercontent.com` as a trusted identity provider.
* **Federated Trust Policy**: The trust policy for `aws_iam_role.github_actions` verifies:
  1. The token issuer is indeed GitHub.
  2. The audience is `sts.amazonaws.com`.
  3. The repository matches the exact repository path defined in `github_repo` (e.g. `repo:your-username/your-repo-name:*`).
* **Deployment Permissions**: Scoped only to what is needed to push images and update ECS services.

### 3. Container Retention and Purge Policy (`ecr.tf`)
To prevent accumulating charges from storing multiple untagged or old docker images in ECR (billed at $0.10 per GB/month), we implement ECR Lifecycle Rules:
* **Rule 1 (Tagged Images)**: Keeps only the last **3** images matching production prefixes (`prod`, `v`, `build`).
* **Rule 2 (Untagged Images)**: Expires and purges all untagged images within **3** days of creation.

---

## State File Management: Migrating to Remote State

In the default configuration, Terraform stores state files locally (`terraform.tfstate`). This is suitable for single developers. In a production environment with multiple engineers, the state must be stored in a remote, encrypted, and locked backend.

### How to Migrate to S3 & DynamoDB Backend

1. **Create the S3 Bucket & DynamoDB table**:
   Create these resources via the AWS Console or a bootstrap Terraform configuration:
   * S3 Bucket Name: `your-organization-terraform-state-bucket` (must enable Versioning and KMS encryption).
   * DynamoDB Table Name: `terraform-state-locks` (Partition key must be `LockID` of type `String`).

2. **Update `terraform/main.tf`**:
   Replace the local backend block with the S3 backend block:
   ```hcl
   # Replace this block:
   # backend "local" {
   #   path = "terraform.tfstate"
   # }

   # With this block:
   backend "s3" {
     bucket         = "your-organization-terraform-state-bucket"
     key            = "secure-cicd-pipeline/terraform.tfstate"
     region         = "us-east-1"
     encrypt        = true
     dynamodb_table = "terraform-state-locks"
   }
   ```

3. **Initialize the migration**:
   Run the following command to copy your existing local state file into the remote S3 bucket:
   ```bash
   terraform init -migrate-state
   ```
   Terraform will detect the backend change and securely transfer state records to S3, enabling team-wide locking and consistency checks.
