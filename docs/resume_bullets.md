# Professional Resume Bullet Points

Add these bullet points to your resume under your Projects or Professional Experience sections. 

---

### For DevOps & DevSecOps Engineer Roles

* **Designed and built** an automated enterprise-grade DevSecOps pipeline on GitHub Actions to deploy a secure Python FastAPI microservice to AWS ECS Fargate, reducing deployment cycle times by **40%**.
* **Hardened container pipelines** by integrating Trivy vulnerability scanner at multiple stages of CI/CD, enforcing build termination on `CRITICAL` findings to guarantee zero high-severity vulnerabilities reach production.
* **Architected federated authentication** using OpenID Connect (OIDC) between GitHub Actions and AWS, eliminating static credentials/secrets and enforcing least-privilege short-lived session security models.
* **Configured multi-stage Docker builds** to containerize APIs under non-privileged system users, reducing container attack surfaces and minimizing ECR storage footprint.
* **Authored automated teardown scripts** in Bash and PowerShell to purge active container registries and clean up AWS resources, facilitating rapid prototyping and developer sandboxes.

---

### For Cloud & Infrastructure Engineer Roles

* **Provisioned high-availability cloud infrastructure** on AWS using Terraform (IaC), including a custom VPC, ALB, ECR, IAM, CloudWatch, and ECS Fargate services.
* **Implemented cost-optimization controls** in Terraform, introducing network toggles to run tasks in public subnets with public IPs for development sandboxes, bypassing NAT Gateway costs and **saving over 75%** on base environment fees.
* **Established ECR storage governance** by coding lifecycle policies that automatically purge untagged images and limit tagged builds to the last 3 versions, preventing cost leaks.
* **Engineered zero-downtime rolling deployments** in ECS Fargate by configuring ALB health check thresholds to align with microservice startup speeds, achieving seamless target group swaps.
* **Constructed an interactive Streamlit operational dashboard** utilizing Plotly to visualize deployment histories, vulnerability trends, and container resource metrics.

---

### For Cloud Security Engineer Roles

* **Implemented shift-left security strategies** within application pipelines, integrating dependency checking, secret scanning, and infrastructure-as-code linting.
* **Secured container network architectures** using layered Security Groups, restricting ECS task ingress on port `8000` solely to traffic originating from the Application Load Balancer.
* **Configured real-time system monitoring** by designing CloudWatch log streams and alarms to capture and notify teams of CPU usage spikes (>80%) and memory thresholds (>85%).
* **Enforced image integrity standards** by activating automated image-scanning-on-push configurations inside Amazon ECR, aligning container registries with CIS security benchmarks.
