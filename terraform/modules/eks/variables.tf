variable "name_prefix" {
  type = string
}

variable "kubernetes_version" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "endpoint_public_access" {
  type    = bool
  default = false
}

variable "public_access_cidrs" {
  type    = list(string)
  default = []

  validation {
    condition = alltrue([
      for cidr in var.public_access_cidrs : cidr != "0.0.0.0/0"
    ])
    error_message = "Public EKS endpoint CIDR allowlist must not include 0.0.0.0/0. Use a restricted set of approved CIDRs only."
  }

  validation {
    condition     = !var.endpoint_public_access || length(var.public_access_cidrs) > 0
    error_message = "If endpoint_public_access is true, public_access_cidrs must contain at least one approved CIDR."
  }
}

variable "node_instance_types" {
  type = list(string)
}

variable "node_desired_size" {
  type = number
}

variable "node_min_size" {
  type = number
}

variable "node_max_size" {
  type = number
}

variable "tags" {
  type    = map(string)
  default = {}
}
