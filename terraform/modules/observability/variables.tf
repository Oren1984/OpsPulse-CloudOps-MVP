variable "name_prefix" {
  type = string
}

variable "app_log_retention_days" {
  type = number
}

variable "cloudtrail_log_retention_days" {
  type = number
}

variable "tags" {
  type    = map(string)
  default = {}
}
