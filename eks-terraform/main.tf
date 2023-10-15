provider "aws" {
  region = var.aws_region
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}


module "eks" {
  source          = "terraform-aws-modules/eks/aws"
  version         = "~> 19.0"
  cluster_name    = "my-cluster"
  cluster_version = "1.27"

  vpc_id     = "vpc-0474b259b4b167a24"
  subnet_ids = ["subnet-0096a4bbe380d8e84", "subnet-0eaa22c222e7dc6ca", "subnet-0c196e08edf7ed801"]

  eks_managed_node_group_defaults = {
    instance_types = ["m5.large"]
  }

  eks_managed_node_groups = {
    blue = {
      min_size     = 1
      max_size     = 3
      desired_size = 2
    }
  }
}


output "cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  value = module.eks.cluster_security_group_id
}

output "cluster_iam_role_name" {
  value = module.eks.cluster_iam_role_name
}
