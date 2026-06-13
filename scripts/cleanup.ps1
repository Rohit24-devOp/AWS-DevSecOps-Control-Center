# ==============================================================================
# AWS Resource Cleanup & Shutdown Script (PowerShell)
# ==============================================================================
# This script completely tears down the AWS resources created by the project.
# It handles ECR image deletion (which blocks standard terraform destroy) 
# and runs Terraform destroy automatically.
# ==============================================================================

$ErrorActionPreference = "Stop"

# Configuration
$AppName = "secure-aws-cicd-app"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TerraformDir = Join-Path $ScriptDir "..\terraform"

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "🚨 AWS DevSecOps Pipeline Cleanup Script Started 🚨" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# Check if AWS CLI is installed
if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
    Write-Error "AWS CLI is not installed. Please install it to proceed."
}

# Check if Terraform is installed
if (-not (Get-Command terraform -ErrorAction SilentlyContinue)) {
    Write-Error "Terraform is not installed. Please install it to proceed."
}

# Confirming deletion
$Confirmation = Read-Host "⚠️  Are you sure you want to delete all resources for '$AppName'? (y/n)"
if ($Confirmation -notmatch "^[Yy]$") {
    Write-Host "❌ Cleanup canceled." -ForegroundColor Yellow
    Exit
}

# 1. Purge ECR Repository Images (Terraform cannot delete ECR if it has images)
Write-Host "🧹 Step 1: Querying ECR images in repository '$AppName'..." -ForegroundColor Yellow
$RepoCheck = aws ecr describe-repositories --repository-names $AppName 2>$null | ConvertFrom-Json

if ($RepoCheck) {
    $Images = aws ecr list-images --repository-name $AppName --query "imageIds" --output json 2>$null | ConvertFrom-Json
    
    if ($Images -and $Images.Count -gt 0) {
        Write-Host "🗑️  Deleting ECR container images..." -ForegroundColor Yellow
        $ImageIdsArg = aws ecr list-images --repository-name $AppName --query "imageIds" --output json
        aws ecr batch-delete-image --repository-name $AppName --image-ids $ImageIdsArg > $null
        Write-Host "✅ ECR container images purged successfully." -ForegroundColor Green
    } else {
        Write-Host "ℹ️  ECR repository is already empty." -ForegroundColor Gray
    }
} else {
    Write-Host "ℹ️  ECR repository '$AppName' not found or already deleted." -ForegroundColor Gray
}

# 2. Run Terraform Destroy
Write-Host "🧹 Step 2: Navigating to Terraform directory and destroying resources..." -ForegroundColor Yellow
if (Test-Path $TerraformDir) {
    Push-Location $TerraformDir
    
    Write-Host "🔄 Running terraform init..." -ForegroundColor Yellow
    terraform init
    
    Write-Host "🔥 Destroying infrastructure..." -ForegroundColor Red
    terraform destroy -auto-approve
    
    Pop-Location
    Write-Host "✅ Infrastructure destroyed successfully." -ForegroundColor Green
} else {
    Write-Error "Terraform directory not found at $TerraformDir"
}

Write-Host "====================================================" -ForegroundColor Green
Write-Host "🎉 Cleanup completed successfully. $AppName shutdown. 🎉" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green
