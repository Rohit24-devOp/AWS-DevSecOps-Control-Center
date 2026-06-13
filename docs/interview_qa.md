# Technical Interview Questions & Answers

Use this guide to prepare for job interviews. The questions below focus on the design choices, security models, and cloud-native practices implemented in this project.

---

### Q1: What is GitHub Actions OIDC (OpenID Connect) and why did you use it instead of standard AWS Access Keys?
**Answer:**
Standard AWS Access Keys (`AKIA...`) are static, long-lived credentials. If developers store them in GitHub Secrets, they risk being leaked through accidental pipeline exposures, compromised logs, or supply chain attacks.
Instead, I implemented **OIDC Federated Authentication** using GitHub's identity provider. 
* **How it works:** When the GitHub Actions workflow runs, it requests a temporary, cryptographic JSON Web Token (JWT) from GitHub. It presents this JWT to the AWS Security Token Service (STS) via an IAM Role with OIDC trust. AWS verifies the signature and issues temporary credentials that expire in 1 hour.
* **Security Benefit:** There are no static credentials stored anywhere. The IAM role trust policy is heavily restricted to verify the exact GitHub repository and branch, enforcing the principle of least privilege.

---

### Q2: How did you implement container security scanning, and what happens if a vulnerability is detected?
**Answer:**
Security scanning is integrated natively at multiple stages using **Trivy**:
1. **Source Code & Secret Scanning**: Before any image is built, Trivy scans the repository directory for hardcoded secrets, configuration issues (like Dockerfile root execution), and outdated dependencies.
2. **Container Image Scanning**: After building the Docker image locally on the runner, Trivy scans the image filesystem layers for operating system and library vulnerabilities.
3. **Pipeline Failure Enforcement**: The pipeline runs Trivy with the `--exit-code 1` parameter specifically for `CRITICAL` severity findings. If a critical vulnerability is found, the script returns a non-zero exit status, instantly failing the CI/CD pipeline and halting deployment. This prevents high-risk images from ever reaching the Amazon ECR registry or running on ECS Fargate.

---

### Q3: Explain how you optimized costs on AWS for this project.
**Answer:**
Standard AWS reference architectures can be highly expensive due to fixed hourly costs. I implemented three main cost-optimization strategies:
1. **Conditional NAT Gateway Bypass**: I introduced a Terraform variable `use_nat_gateway`. When set to `false`, Fargate tasks are provisioned directly in public subnets with public IPs assigned. This bypasses the need for an AWS NAT Gateway, which saves **~$32.40/month** in base charges. Fargate tasks still communicate securely via the Application Load Balancer and can access ECR/CloudWatch directly.
2. **Task Size Downscaling**: Configured the Fargate task sizes to the minimum possible limits—0.25 vCPU (256 CPU units) and 0.5 GB RAM (512 MiB memory), keeping compute costs low.
3. **ECR Lifecycle Rules**: Configured ECR to automatically purge untagged images within 3 days and retain only the last 3 tagged build images, minimizing AWS ECR storage costs.
4. **Log Retention Limits**: Set CloudWatch Log Groups to expire records after 7 days instead of indefinite retention.

---

### Q4: Why did you use `jq` during the ECS task definition deployment step in GitHub Actions?
**Answer:**
When you retrieve the active task definition from AWS using the CLI (`aws ecs describe-task-definition`), the returned JSON contains AWS-injected metadata fields such as `taskDefinitionArn`, `revision`, `status`, `requiresAttributes`, and `compatibilities`.
If you pass this raw JSON block directly to `aws ecs register-task-definition` (or the GitHub ECS deploy action), AWS will reject it with a validation error because these read-only parameters cannot be specified during registration.
To solve this, I wrote a shell pipeline using `jq` to strip these metadata tags:
```bash
jq '. | del(.taskDefinitionArn, .revision, .status, .requiresAttributes, .compatibilities, .registeredAt, .registeredBy)' raw-task-def.json > task-definition.json
```
This isolates the deployment configuration cleanly, allowing the ECS Render Task Definition action to run successfully.

---

### Q5: How is network isolation achieved for the containers running in ECS Fargate?
**Answer:**
Network security is enforced using two layers of Security Groups:
1. **Application Load Balancer SG**: Exposes ports `80` (and `443` in production TLS setups) to the public Internet (`0.0.0.0/0`) to accept client web requests.
2. **ECS Task SG**: Blocks all ingress from the public Internet. It contains a security group rule that allows incoming TCP traffic on port `8000` (the FastAPI port) **only** if the source is the Application Load Balancer's security group.
This ensures that users cannot bypass the ALB to access the containers directly, and prevents port scanners or direct network attacks from reaching the application.
