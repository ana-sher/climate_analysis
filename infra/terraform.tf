terraform {
  backend "s3" {
    bucket       = "terraform-state-bucket-4848"
    key          = "climate_analysis/terraform.tfstate"
    region       = "eu-north-1"
    encrypt      = true
    use_lockfile = true
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.22"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.6.1"
    }
  }

  required_version = ">= 1.2"
}
