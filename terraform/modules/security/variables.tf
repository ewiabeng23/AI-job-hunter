variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID for flow logs"
  type        = string
}

variable "account_id" {
  description = "AWS account ID"
  type        = string
}

variable "sns_topic_arn" {
  description = "SNS topic ARN for GuardDuty alerts (optional)"
  type        = string
  default     = ""
}
