# VPC Module
module "vpc" {
  source = "./modules/vpc"

  project_name         = var.project_name
  environment          = var.environment
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
}

# EC2 Module - Jenkins Server
module "ec2" {
  source = "./modules/ec2"

  project_name     = var.project_name
  environment      = var.environment
  vpc_id           = module.vpc.vpc_id
  public_subnet_id = module.vpc.public_subnet_ids[0]
  instance_type    = var.ec2_instance_type
  key_name         = var.ec2_key_name
}

# EKS Module - Kubernetes Cluster
module "eks" {
  source = "./modules/eks"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  cluster_version    = var.eks_cluster_version
  node_instance_type = var.eks_node_instance_type
  node_min_size      = var.eks_node_min_size
  node_max_size      = var.eks_node_max_size
  node_desired_size  = var.eks_node_desired_size
}

# Monitoring Module - Prometheus, Grafana, ELK
module "monitoring" {
  source = "./modules/monitoring"

  eks_cluster_name = module.eks.cluster_name
  grafana_password = "admin123"

  depends_on = [module.eks]
}

# Security Module - GuardDuty, CloudTrail, VPC Flow Logs
module "security" {
  source = "./modules/security"

  project_name  = var.project_name
  environment   = var.environment
  vpc_id        = module.vpc.vpc_id
  account_id    = data.aws_caller_identity.current.account_id
  sns_topic_arn = ""

  depends_on = [module.vpc]
}

# Get current AWS account ID
data "aws_caller_identity" "current" {}

# AWS Load Balancer Controller - Helm release
resource "helm_release" "aws_load_balancer_controller" {
  name       = "aws-load-balancer-controller"
  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  version    = "1.7.1"
  namespace  = "kube-system"

  set {
    name  = "clusterName"
    value = module.eks.cluster_name
  }

  set {
    name  = "region"
    value = var.aws_region
  }

  set {
    name  = "vpcId"
    value = module.vpc.vpc_id
  }

  set {
    name  = "serviceAccount.create"
    value = "true"
  }

  set {
    name  = "serviceAccount.name"
    value = "aws-load-balancer-controller"
  }

  set {
    name  = "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"
    value = module.eks.aws_load_balancer_controller_role_arn
  }

  depends_on = [module.eks]
}
