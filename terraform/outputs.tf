output "jenkins_public_ip" {
  description = "Jenkins server public IP"
  value       = module.ec2.jenkins_public_ip
}

output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "connect_to_jenkins" {
  description = "SSH command to connect to Jenkins"
  value       = "ssh -i ~/.ssh/new.pem ubuntu@${module.ec2.jenkins_public_ip}"
}

output "configure_kubectl" {
  description = "Command to configure kubectl"
  value       = "aws eks update-kubeconfig --region us-east-1 --name ${module.eks.cluster_name}"
}
