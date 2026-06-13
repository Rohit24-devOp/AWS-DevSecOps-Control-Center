# ==========================================
# Outputs
# ==========================================

output "vpc_id" {
  description = "The ID of the provisioned VPC"
  value       = aws_vpc.main.id
}

output "alb_dns_name" {
  description = "The public DNS name of the Application Load Balancer"
  value       = "http://${aws_lb.main.dns_name}"
}

output "ecr_repository_url" {
  description = "The URL of the Amazon ECR repository"
  value       = aws_ecr_repository.app.repository_url
}

output "github_actions_role_arn" {
  description = "The ARN of the IAM role configured for GitHub Actions OIDC deploy trust"
  value       = aws_iam_role.github_actions.arn
}

output "ecs_cluster_name" {
  description = "The name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "The name of the ECS service"
  value       = aws_ecs_service.main.name
}

output "ecs_task_definition_family" {
  description = "The family name of the ECS Task Definition"
  value       = aws_ecs_task_definition.app.family
}
