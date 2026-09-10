variable "name_prefix" {
  type = string
}

variable "github_repository" {
  description = "GitHub \"org/repo\" allowed to assume this role via OIDC."
  type        = string
}

variable "ecr_repository_arn" {
  type = string
}

variable "eks_cluster_arn" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
