variable "eks_cluster_name" {
  description = "EKS cluster name"
  type        = string
}

variable "grafana_password" {
  description = "Grafana admin password"
  type        = string
  default     = "admin123"
  sensitive   = true
}
