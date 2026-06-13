# Cloud-Native DevSecOps Infrastructure Architecture

This document describes the design, security postures, and traffic flow of the **Secure Cloud-Native CI/CD Pipeline on AWS** project.

## Architecture Diagram

The system comprises two core planes: the **Deployment Plane (CI/CD)** on GitHub Actions and the **Runtime Plane (AWS)** within a custom-configured VPC.

```mermaid
graph TD
    subgraph Developer Domain
        Dev[Developer] -->|1. Git Push / PR| GH[GitHub Repository]
    end

    subgraph CI/CD Plane (GitHub Actions)
        GH_Runner[GitHub Runner]
        GH_Runner -->|2. Lint & Unit Tests| GH_Test[Pytest Suite]
        GH_Test -->|3. Security Scan| GH_Trivy[Trivy Vulnerabilities & Secrets]
        GH_Trivy -->|4. Authenticate| GH_OIDC[AWS OIDC Federation]
        GH_OIDC -->|5. Build & Image Scan| GH_Docker[Docker Buildx & Trivy Image Scan]
        GH_Docker -->|6. Push Image| ECR[(Amazon ECR)]
        GH_Docker -->|7. Update Task Def| GH_Deploy[ECS Service Update]
    end

    subgraph AWS Runtime Plane (VPC - 10.0.0.0/16)
        subgraph Public Subnets (10.0.0.0/24, 10.0.1.0/24)
            ALB[Application Load Balancer]
            IGW[Internet Gateway]
        end

        subgraph Private Subnets (10.0.10.0/24, 10.0.11.0/24)
            Fargate[ECS Fargate Tasks]
        end

        CW[CloudWatch Logs & Alarms]
        
        IGW <--> ALB
        ALB -->|8. Forward Traffic (Port 8000)| Fargate
        Fargate -->|Pull Container| ECR
        Fargate -->|Ship Logs & Metrics| CW
    end

    subgraph Monitoring Control Center
        Dashboard[Streamlit Dashboard] -->|Query Metrics & Logs| CW
    end

    GH_Deploy -->|Trigger Rolling Update| Fargate
```

---

## Component Details

### 1. VPC Networking
* **Custom VPC (`10.0.0.0/16`)**: Segmented into 2 Public Subnets and 2 Private Subnets across 2 Availability Zones for high availability.
* **Internet Gateway**: Allows the Application Load Balancer (ALB) to receive traffic from the public Internet.
* **NAT Gateway (Optional for Cost Optimization)**: 
  * In **Enterprise Mode** (`use_nat_gateway = true`), ECS Fargate containers are launched in private subnets and route outgoing traffic (to ECR and CloudWatch) through the NAT Gateway.
  * In **Cost-Saving Mode** (`use_nat_gateway = false`), ECS Fargate containers are launched in public subnets with public IPs assigned to communicate directly with AWS public endpoints, eliminating the NAT Gateway's hourly charge.
* **Security Group Isolation**:
  * **ALB SG**: Allows port 80/443 from any IP (`0.0.0.0/0`).
  * **ECS Task SG**: Strictly allows ingress on port `8000` (FastAPI) *only* from the ALB security group. Prevents any direct access to the container.

### 2. Identity & Security (IAM OIDC)
* **Federated Identity**: An OpenID Connect (OIDC) provider establishes trust between GitHub and AWS.
* **Least Privilege**: The GitHub Actions runner assumes a short-lived IAM Role (`secure-aws-cicd-app-github-actions-role`) bounded by conditional checks:
  * Only requests from the matching GitHub Repository `owner/repo` are authorized.
  * Permissions are strictly scoped to ECR push operations, ECS task registration, and IAM PassRole (limited to passing task roles to ECS).

### 3. Container Security
* **Trivy Scanner**: Run at two key checkpoints in the CI/CD pipeline:
  * **Static File Scan**: Checks code, dependencies, and configuration templates (like Dockerfiles) for secrets and misconfigurations.
  * **Image Scan**: Scans the compiled container image before pushing to ECR.
  * **Failure Criteria**: The pipeline terminates immediately with an exit code `1` if any `CRITICAL` vulnerability or secret is detected.
* **Hardened Docker Image**:
  * Uses a minimal `python:3.11-slim` base image to reduce attack surface.
  * Utilizes a multi-stage build structure (leaving build tools behind in the builder stage).
  * Executes application process under a non-root user (`appuser` with UID `10001`).

### 4. Logging & Monitoring
* **Structured Logs**: FastAPI emits structured JSON logs. Uvicorn stdout is captured by the ECS logging driver (`awslogs`) and streamed to CloudWatch under the log group `/ecs/secure-aws-cicd-app`.
* **Metric Alarms**: CloudWatch Alarms trigger if ECS Fargate task CPU utilization exceeds 80% or memory utilization exceeds 85% for two consecutive evaluation periods.
* **Streamlit Dashboard**: Pulls logs and resource metrics directly from CloudWatch APIs or models them to display container state and vulnerability trends.
