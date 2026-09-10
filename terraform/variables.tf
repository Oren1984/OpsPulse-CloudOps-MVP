variable "project_name" {
  description = "Short project identifier used in resource names and tags."
  type        = string
  default     = "opspulse"
}

variable "environment" {
  description = "Deployment environment tag. Kept as a non-production POC."
  type        = string
  default     = "poc"
}

variable "aws_region" {
  description = "Single AWS region for this isolated POC deployment (no multi-region)."
  type        = string
  default     = "us-east-1"
}

variable "cost_center_tag" {
  description = "Free-form cost-control tag applied to all resources."
  type        = string
  default     = "opspulse-poc"
}

variable "vpc_cidr" {
  description = "CIDR block for the OpsPulse VPC."
  type        = string
  default     = "10.42.0.0/16"
}

variable "availability_zone_count" {
  description = "Number of AZs to spread subnets across (kept small for POC cost control)."
  type        = number
  default     = 2
}

variable "single_nat_gateway" {
  description = "Use one shared NAT gateway instead of one per AZ. POC cost trade-off: reduces AZ-level fault tolerance for egress traffic."
  type        = bool
  default     = true
}

variable "node_instance_types" {
  description = "EC2 instance types for the EKS managed node group."
  type        = list(string)
  default     = ["t3.small"]
}

variable "node_desired_size" {
  type    = number
  default = 2
}

variable "node_min_size" {
  type    = number
  default = 1
}

variable "node_max_size" {
  type    = number
  default = 3
}

variable "kubernetes_version" {
  description = "EKS control plane Kubernetes version."
  type        = string
  default     = "1.31"
}

variable "db_instance_class" {
  description = "Small, non-production RDS instance class."
  type        = string
  default     = "db.t4g.micro"
}

variable "db_allocated_storage_gb" {
  type    = number
  default = 20
}

variable "db_name" {
  type    = string
  default = "opspulse"
}

variable "db_username" {
  type    = string
  default = "opspulse"
}

variable "db_engine_version" {
  description = "PostgreSQL major.minor version for RDS."
  type        = string
  default     = "16.4"
}

variable "github_repository" {
  description = "GitHub \"org/repo\" allowed to assume the CI/CD deployment role via OIDC."
  type        = string
  default     = "Oren1984/OpsPulse-CloudOps-MVP"
}

variable "eks_endpoint_public_access" {
  description = "Whether to enable public EKS API access. Keep this disabled by default for a POC behind private networking."
  type        = bool
  default     = false
}

variable "eks_public_access_cidrs" {
  description = "Approved CIDR ranges allowed to reach the public EKS API endpoint when public access is enabled. Must never include 0.0.0.0/0."
  type        = list(string)
  default     = []

  validation {
    condition = alltrue([
      for cidr in var.eks_public_access_cidrs : cidr != "0.0.0.0/0"
    ])
    error_message = "eks_public_access_cidrs must not include 0.0.0.0/0. Use a restricted allowlist only."
  }
}

variable "cloudtrail_log_retention_days" {
  description = "S3 lifecycle expiration for CloudTrail logs. Kept short for a POC to control cost."
  type        = number
  default     = 30
}

variable "app_log_retention_days" {
  description = "CloudWatch Logs retention for application/EKS logs."
  type        = number
  default     = 14
}
