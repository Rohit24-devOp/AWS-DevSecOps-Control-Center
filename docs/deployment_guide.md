# End-to-End Deployment Guide

This guide describes how to deploy the **Secure Cloud-Native CI/CD Pipeline on AWS** from scratch.

---

## Prerequisites

Before starting, ensure you have the following installed and configured:
1. **AWS Account**: Access to an AWS account with admin/power-user permissions.
2. **AWS CLI**: Installed and configured with your credentials (`aws configure`).
3. **Terraform**: Installed (version `v1.5.0` or higher).
4. **Git**: Installed and configured.
5. **Python 3.11+**: Installed (to run tests and the dashboard locally).
6. **Docker**: (Optional, for building/testing containers locally).

---

## Step 1: Initial Repository Push

1. Create a private or public repository on GitHub (e.g., `github.com/your-username/your-repo-name`).
2. Initialize Git in the project root:
   ```bash
   git init
   git add .
   git commit -m "feat: initial commit of secure pipeline codebase"
   ```
3. Link the repository to your GitHub remote and push:
   ```bash
   git remote add origin https://github.com/your-username/your-repo-name.git
   git branch -M main
   git push -u origin main
   ```

---

## Step 2: Configure and Run Terraform

1. Navigate to the `terraform/` directory:
   ```bash
   cd terraform
   ```
2. Copy the example variables file:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```
3. Edit `terraform.tfvars` with your settings:
   * Change `github_repo` to match your actual GitHub repository (e.g., `"your-username/your-repo-name"`). **This is critical for OIDC validation.**
   * Ensure `use_nat_gateway = false` if you want to keep deployment costs under $10/month.
4. Initialize Terraform:
   ```bash
   terraform init
   ```
5. Validate configuration:
   ```bash
   terraform validate
   ```
6. Run `plan` to check the resources to be created:
   ```bash
   terraform plan
   ```
7. Apply the configuration to provision AWS resources:
   ```bash
   terraform apply -auto-approve
   ```
8. Take note of the Terraform Outputs printed on completion:
   * `alb_dns_name` (The endpoint to access your app once deployed)
   * `ecr_repository_url` (The repository address)
   * `github_actions_role_arn` (The IAM Role ARN to assume via OIDC)

---

## Step 3: Configure GitHub Secrets

1. Go to your GitHub repository on GitHub.com.
2. Click **Settings** -> **Secrets and variables** -> **Actions**.
3. Create a new repository secret:
   * **Name**: `AWS_ROLE_ARN`
   * **Value**: Copy the exact value of `github_actions_role_arn` from your Terraform output (e.g., `arn:aws:iam::123456789012:role/secure-aws-cicd-app-github-actions-role`).
4. Ensure the workflow matches your region and service names (defaults are set to `us-east-1` and `secure-aws-cicd-app`).

---

## Step 4: Run the CI/CD Pipeline

To trigger the pipeline, commit a small change or push the repository. Since we ignored task definition updates in Terraform lifecycle rules, the initial task will fail to pull a real image (as ECR was empty). The GitHub Actions pipeline will fix this immediately by building and deploying the real image:

1. Stage and push a minor edit (e.g., adding an environment variable or editing a comment):
   ```bash
   git add .
   git commit -m "ci: trigger first deployment pipeline"
   git push origin main
   ```
2. Go to the **Actions** tab in your GitHub repository.
3. Select the **Secure DevSecOps Pipeline** run.
4. Watch the pipeline run:
   * **Build, Test & Security Scan**: Runs unit tests and runs Trivy to check code.
   * **Containerize & Deploy to AWS**: Authenticates with AWS via OIDC, builds the Docker image, scans it for vulnerabilities using Trivy, pushes the image to ECR, and triggers the ECS Fargate rolling deployment.
5. Once the deployment stage completes (takes ~3-5 minutes for ECS service stability), open the `alb_dns_name` URL in your browser. You should see:
   `{"status":"online", "service":"Secure Cloud-Native CI/CD Pipeline App", ...}`

---

## Step 5: Launch the Streamlit Monitoring Dashboard

To run the monitoring dashboard locally:
1. Navigate to the `dashboard/` directory:
   ```bash
   cd dashboard
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit server:
   ```bash
   streamlit run dashboard.py
   ```
4. A browser window will open automatically at `http://localhost:8501`. Explore the tabs:
   * **Overview**: Real-time traffic, CPU load, and vulnerability summary.
   * **CI/CD Pipeline**: Logs from pipeline stages.
   * **Security Findings**: History of vulnerabilities over time.
   * **Container Health**: Real-time resources.
   * **Cost Analytics**: View projected monthly costs and calculate savings toggles.

---

## Step 6: Cleanup Resources (Shutdown)

When you are done demonstrating the project, run the cleanup script to guarantee zero ongoing AWS costs:

**Using Bash (Linux/macOS/WSL/Git Bash)**:
```bash
bash scripts/cleanup.sh
```

**Using PowerShell (Windows)**:
```powershell
.\scripts\cleanup.ps1
```
The script will purge all images inside the ECR repository and run `terraform destroy -auto-approve` automatically.
