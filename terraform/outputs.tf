output "vpc_id" {
  value = module.vpc.vpc_id
}

output "ecr_repository_url" {
  value = module.ecr.repository_url
}

output "eks_cluster_name" {
  value = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "rds_endpoint" {
  value = module.rds.endpoint
}

output "rds_secrets_manager_arn" {
  value = module.rds.secrets_manager_secret_arn
}

output "github_actions_deploy_role_arn" {
  value = module.iam_oidc.deploy_role_arn
}

output "cloudtrail_bucket_name" {
  value = module.observability.cloudtrail_bucket_name
}

output "app_log_group_name" {
  value = module.observability.app_log_group_name
}
