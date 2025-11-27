terraform {
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
