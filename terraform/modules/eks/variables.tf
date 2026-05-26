variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for EKS nodes"
  type        = list(string)
}

variable "cluster_version" {
  description = "Kubernetes version"
  type        = string
}

variable "node_instance_type" {
  description = "EC2 instance type for nodes"
  type        = string
}

variable "node_min_size" {
  description = "Minimum nodes"
  type        = number
}

variable "node_max_size" {
  description = "Maximum nodes"
  type        = number
}

variable "node_desired_size" {
  description = "Desired nodes"
  type        = number
}
