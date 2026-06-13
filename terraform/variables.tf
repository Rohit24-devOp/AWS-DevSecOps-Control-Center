variable "aws_region" {
  description = "AWS region to deploy resources in"
  type        = string
  default     = "us-east-1"
}

variable "app_name" {
  description = "Name of the application"
  type        = string
  default     = "secure-aws-cicd-app"
}

variable "environment" {
  description = "Deployment environment name"
  type        = string
  default     = "production"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "use_nat_gateway" {
  description = "Toggle to provision NAT Gateway (set to true for full isolation, false for free-tier friendly cost saving where Fargate runs in public subnets)"
  type        = bool
  default     = false
}

variable "container_port" {
  description = "Port exposed by the FastAPI container"
  type        = number
  default     = 8000
}

variable "fargate_cpu" {
  description = "Fargate instance CPU units (256 = 0.25 vCPU)"
  type        = number
  default     = 256 # 0.25 vCPU - Free-tier / low cost friendly
}

variable "fargate_memory" {
  description = "Fargate instance memory (in MiB)"
  type        = number
  default     = 512 # 0.5 GB RAM - Free-tier / low cost friendly
}

variable "desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
  default     = 1
}

variable "github_repo" {
  description = "GitHub repository formatted as 'owner/repo' (used to configure OIDC role trust)"
  type        = string
  default     = "Rohit24-devOp/Cloud-Security-Monitoring-WAF-Protection-Platform"
}
