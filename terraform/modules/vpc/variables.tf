variable "name_prefix" {
  type = string
}

variable "vpc_cidr" {
  type = string
}

variable "availability_zone_count" {
  type = number
}

variable "single_nat_gateway" {
  type = bool
}

variable "tags" {
  type    = map(string)
  default = {}
}
