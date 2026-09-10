module "vpc" {
  source = "./modules/vpc"

  name_prefix             = local.name_prefix
  vpc_cidr                = var.vpc_cidr
  availability_zone_count = var.availability_zone_count
  single_nat_gateway      = var.single_nat_gateway
  tags                    = local.common_tags
}

module "ecr" {
  source = "./modules/ecr"

  repository_name = var.project_name
  tags            = local.common_tags
}

module "eks" {
  source = "./modules/eks"

  name_prefix              = local.name_prefix
  kubernetes_version       = var.kubernetes_version
  vpc_id                   = module.vpc.vpc_id
  private_subnet_ids       = module.vpc.private_subnet_ids
  endpoint_public_access   = var.eks_endpoint_public_access
  public_access_cidrs      = var.eks_public_access_cidrs
  node_instance_types      = var.node_instance_types
  node_desired_size        = var.node_desired_size
  node_min_size            = var.node_min_size
  node_max_size            = var.node_max_size
  tags                     = local.common_tags
}

module "rds" {
  source = "./modules/rds"

  name_prefix                = local.name_prefix
  vpc_id                     = module.vpc.vpc_id
  private_subnet_ids         = module.vpc.private_subnet_ids
  allowed_security_group_ids = [module.eks.cluster_security_group_id]
  instance_class             = var.db_instance_class
  allocated_storage_gb       = var.db_allocated_storage_gb
  engine_version             = var.db_engine_version
  db_name                    = var.db_name
  db_username                = var.db_username
  tags                       = local.common_tags
}

module "iam_oidc" {
  source = "./modules/iam-oidc"

  name_prefix        = local.name_prefix
  github_repository  = var.github_repository
  ecr_repository_arn = module.ecr.repository_arn
  eks_cluster_arn    = "arn:aws:eks:${var.aws_region}:${data.aws_caller_identity.current.account_id}:cluster/${module.eks.cluster_name}"
  tags               = local.common_tags
}

module "observability" {
  source = "./modules/observability"

  name_prefix                   = local.name_prefix
  app_log_retention_days        = var.app_log_retention_days
  cloudtrail_log_retention_days = var.cloudtrail_log_retention_days
  tags                          = local.common_tags
}

# Restrict the deployment role to the OpsPulse namespace rather than the whole
# cluster. This keeps the POC deploy flow working without granting cluster-wide
# administrative access.
resource "aws_eks_access_entry" "github_actions_deploy" {
  cluster_name  = module.eks.cluster_name
  principal_arn = module.iam_oidc.deploy_role_arn
}

resource "aws_eks_access_policy_association" "github_actions_deploy" {
  cluster_name  = module.eks.cluster_name
  principal_arn = module.iam_oidc.deploy_role_arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSAdminPolicy"

  access_scope {
    type       = "namespace"
    namespaces = ["opspulse"]
  }

  depends_on = [aws_eks_access_entry.github_actions_deploy]
}

data "aws_caller_identity" "current" {}
