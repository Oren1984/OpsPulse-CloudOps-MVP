output "app_log_group_name" {
  value = aws_cloudwatch_log_group.app.name
}

output "cloudtrail_bucket_name" {
  value = aws_s3_bucket.cloudtrail.id
}

output "cloudtrail_arn" {
  value = aws_cloudtrail.this.arn
}
