variable "aws_region" {
  description = "AWS region"
  default     = "eu-north-1"
}

variable "create_local_user" {
  description = "Create user with app required policies"
  type        = bool
  default     = false
}

variable "local_user" {
  description = "Local user name to create in aws and add policies to"
  default     = "local-dev"
}
