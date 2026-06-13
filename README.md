# Secure Cloud-Native CI/CD Pipeline on AWS

This project demonstrates a production-quality, enterprise-grade DevSecOps pipeline that builds, tests, scans, containerizes, and deploys a secured Python FastAPI application to AWS ECS Fargate using GitHub Actions and Terraform.

---

## 🚀 Key Features

* **Infrastructure as Code**: Full Terraform configurations for provision of networking, computing, security, and logging services.
* **Modern CI/CD**: Seamless GitHub Actions workflows executing tests, running Trivy security scans, and updating tasks.
* **Zero-Secrets OIDC Trust**: Passwordless federated authentication between GitHub Actions and AWS (no static Access Keys).
* **Hardened Containers**: Multi-stage, non-root Docker builds running on slim runtimes with built-in health checks.
* **Trivy Shift-Left Security**: Pipeline immediately fails if repository checks find secrets or container scans find critical vulnerabilities.
* **Interactive Control Center**: A custom glassmorphic Streamlit dashboard featuring a custom-designed logo and interactive charts for container health, build duration trends, vulnerability source breakdowns, and dynamic cost allocation projections.
* **Cost Optimization Toggles**: Configured to run ECS Fargate tasks in cost-saving public subnets for dev/testing, bypassing expensive NAT Gateways (~$32/month saving).
* **Comprehensive Documentation**: Complete deployment guides, interview preparation, and resume points.

---

## 🛠️ Technology Stack

* **Cloud Platform**: AWS (VPC, ECS Fargate, ECR, ALB, IAM, CloudWatch)
* **Infrastructure as Code**: Terraform (version `>= 1.5.0`)
* **Pipeline Engine**: GitHub Actions
* **Application Framework**: Python, FastAPI, Uvicorn, Pytest
* **Security Scanning**: Trivy (Vulnerabilities, Secrets, and Dockerfile)
* **Visualization**: Streamlit, Pandas, Plotly

---

## 📂 Project Structure

```
├── .github/
│   └── workflows/
│       └── devops-pipeline.yml      # CI/CD Workflow (Build, Test, Scan, ECR Push, ECS Deploy)
├── app/
│   ├── app.py                      # FastAPI Web Application
│   ├── requirements.txt            # Application dependencies
│   ├── Dockerfile                  # Secure multi-stage Docker build
│   └── tests/
│       └── test_app.py             # Unit tests for API endpoints
├── terraform/
│   ├── main.tf                     # Entry point calling networking & ECS
│   ├── variables.tf                # Configuration variables
│   ├── outputs.tf                  # Deployment outputs (ALB URL, ECR URL, etc.)
│   ├── vpc.tf                      # Network setup (VPC, Subnets, SG, NAT)
│   ├── alb.tf                      # Load balancer setup
│   ├── ecs.tf                      # ECS Cluster, Task definition, and Fargate Service
│   ├── ecr.tf                      # ECR repository with lifecycle rules
│   ├── iam.tf                      # Roles for ECS and GitHub Actions OIDC trust
│   ├── cloudwatch.tf               # Log groups and alarms
│   └── terraform.tfvars.example    # Template variable values
├── dashboard/
│   ├── dashboard.py                # Streamlit Monitoring Dashboard
│   ├── requirements.txt            # Streamlit dependencies
│   └── Dockerfile.dashboard        # Streamlit deployment container
├── scripts/
│   ├── cleanup.sh                  # AWS resource cleanup shell script
│   └── cleanup.ps1                 # AWS resource cleanup PowerShell script
└── docs/                           # Detailed Documentation Guides
```


---

## 📊 Operations Dashboard Analytics

The local Streamlit application (**[dashboard/dashboard.py](file:///d:/AWS%20WAF%20Project/aws%20ci%20cd%20project/dashboard/dashboard.py)**) acts as a DevSecOps control panel and visualizes key metrics:

* **Dynamic Cost Allocation**: A Plotly donut chart that recalculates in real-time as you slide the Fargate compute dials or toggle the NAT Gateway active/inactive state.
* **Vulnerability Source Breakdown**: A grouped bar chart displaying Trivy findings categorized by layers—Base OS libraries, Python runtime, and project dependencies.
* **Build Duration History**: A line chart tracking the pipeline's execution duration across consecutive runs to track build latency.
* **Custom Logo Asset**: Configured to load the custom-generated logo located at **[dashboard/devsecops_logo.png](file:///d:/AWS%20WAF%20Project/aws%20ci%20cd%20project/dashboard/devsecops_logo.png)** relative to the script directory, with a clean fallback to the official AWS brand icon.

---

## 📖 Detailed Guides & Resources

For thorough deployment steps, architectural details, and career preparation materials, refer to the following documents:

1. **[Architecture Design Guide](file:///d:/AWS%20WAF%20Project/aws%20ci%20cd%20project/docs/architecture_diagram.md)**: Reviews the VPC network configuration, IAM OIDC trust, and security group isolation.
2. **[End-to-End Deployment Guide](file:///d:/AWS%20WAF%20Project/aws%20ci%20cd%20project/docs/deployment_guide.md)**: Step-by-step instructions on setting up AWS OIDC trust, running Terraform, configuring GitHub secrets, and running the pipeline.
3. **[Terraform Configuration Guide](file:///d:/AWS%20WAF%20Project/aws%20ci%20cd%20project/docs/terraform_guide.md)**: Describes input variables, ECR retention rules, and how to migrate to an S3/DynamoDB remote state backend.
4. **[Interview Q&A Guide](file:///d:/AWS%20WAF%20Project/aws%20ci%20cd%20project/docs/interview_qa.md)**: Curated list of high-impact interview questions and answers mapping to this architecture.
5. **[Resume Bullet Points](file:///d:/AWS%20WAF%20Project/aws%20ci%20cd%20project/docs/resume_bullets.md)**: Copy-pasteable STAR-formatted bullet points for DevOps, Cloud, and Security Engineer resumes.

---

## 🚀 Quick Start (Tear Down)

When you are done demonstrating or testing this deployment, clean up the AWS resources immediately to avoid incurring fees:

* **On Linux/macOS/Git Bash**:
  ```bash
  bash scripts/cleanup.sh
  ```
* **On Windows PowerShell**:
  ```powershell
  .\scripts\cleanup.ps1
  ```
These scripts will purge ECR repository images (which block standard deletes) and run `terraform destroy -auto-approve` automatically.
