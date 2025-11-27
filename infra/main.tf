provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

data "aws_ecr_authorization_token" "token" {}

provider "docker" {
  registry_auth {
    address  = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com"
    username = data.aws_ecr_authorization_token.token.user_name
    password = data.aws_ecr_authorization_token.token.password
  }
}

# Create S3 bucket

resource "aws_s3_bucket" "app_s3" {
  bucket = "climate-analysis-bucket"

  tags = {
    Name        = "Climate Analysis Bucket"
    Environment = "Dev"
  }
}

resource "aws_s3_bucket_public_access_block" "s3_access" {
  bucket = aws_s3_bucket.app_s3.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
###---------------------------------------------

# Create policy to access the bucket

data "aws_iam_policy_document" "aws_policy_doc" {
  statement {
    actions = [
      "s3:ListBucket",
    ]
    effect    = "Allow"
    resources = [aws_s3_bucket.app_s3.arn]
  }
  statement {
    actions = [
      "s3:GetObject",
      "s3:PutObject"
    ]
    effect    = "Allow"
    resources = ["${aws_s3_bucket.app_s3.arn}/*"]
  }
}

resource "aws_iam_policy" "policy" {
  name        = "climate_analysis_resources_policy"
  path        = "/"
  description = "Climate Analysis Resources access"

  policy = data.aws_iam_policy_document.aws_policy_doc.json
}

###---------------------------------------------

# Create local user for s3 access (optional)

resource "aws_iam_user" "local_dev" {
  count = var.create_local_user ? 1 : 0
  name  = var.local_user
}

resource "aws_iam_user_policy_attachment" "local_dev_s3" {
  count      = var.create_local_user ? 1 : 0
  user       = aws_iam_user.local_dev[0].name
  policy_arn = aws_iam_policy.policy.arn
}

resource "aws_iam_access_key" "local_dev_key" {
  count = var.create_local_user ? 1 : 0
  user  = aws_iam_user.local_dev[0].name
}

###---------------------------------------------

# Create docker image, app lambda, it's role and attach policy

module "aws_lambda_function" {
  source = "terraform-aws-modules/lambda/aws"

  function_name  = "climate_analysis_lambda"
  create_package = false

  image_uri    = module.docker_image.image_uri
  package_type = "Image"
}

module "docker_image" {
  source = "terraform-aws-modules/lambda/aws//modules/docker-build"

  create_ecr_repo = true
  ecr_repo        = "climate-analysis"

  use_image_tag = true
  image_tag     = "1.0"

  source_path = "../"
}

# resource "aws_api_gateway_integration" "app_api_gateway" {
#   rest_api_id = ""
#   resource_id = aws_lambda_function.example.id
#   http_method = aws_api_gateway_method.example.http_method
#
#   integration_http_method = "POST"
#   type                    = "AWS_PROXY"
#   uri                     = aws_lambda_function.app_lambda.invoke_arn
# }

resource "aws_iam_role" "app_role" {
  name = "climate_app_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect    = "Allow",
      Principal = { Service = "lambda.amazonaws.com" },
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "app_role_policy_attach" {
  role       = aws_iam_role.app_role.name
  policy_arn = aws_iam_policy.policy.arn
}

###---------------------------------------------

# Create api gateway




