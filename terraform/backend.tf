# Local state by default, intentionally, to keep this POC dependency-free.
# For real use, configure a remote backend (S3 + DynamoDB lock table) here,
# e.g.:
#
# terraform {
#   backend "s3" {
#     bucket         = "your-terraform-state-bucket"
#     key            = "opspulse/terraform.tfstate"
#     region         = "us-east-1"
#     dynamodb_table = "your-terraform-lock-table"
#     encrypt        = true
#   }
# }
