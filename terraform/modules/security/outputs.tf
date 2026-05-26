output "guardduty_detector_id" {
  description = "GuardDuty detector ID"
  value       = aws_guardduty_detector.main.id
}

output "cloudtrail_bucket" {
  description = "S3 bucket storing CloudTrail logs"
  value       = aws_s3_bucket.cloudtrail.bucket
}

output "cloudtrail_arn" {
  description = "CloudTrail ARN"
  value       = aws_cloudtrail.main.arn
}

output "vpc_flow_log_group" {
  description = "CloudWatch log group for VPC flow logs"
  value       = aws_cloudwatch_log_group.vpc_flow_logs.name
}
