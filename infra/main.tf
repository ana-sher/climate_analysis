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

  create_role = false
  lambda_role = aws_iam_role.app_role.arn

  policies = [
    aws_iam_role_policy_attachment.ecs_read.policy_arn,
    aws_iam_role_policy_attachment.lambda_basic.policy_arn
  ]
}

data "archive_file" "docker_context" {
  type        = "zip"
  source_dir  = "../src/"
  output_path = "${path.module}/context.zip"
}

locals {
  docker_tag = substr(data.archive_file.docker_context.output_base64sha256, 0, 12)
}

resource "null_resource" "cleanup_zip" {
  triggers = {
    docker_tag = local.docker_tag
  }

  provisioner "local-exec" {
    command = "rm -f ${path.module}/context.zip"
  }
}

module "docker_image" {
  source = "terraform-aws-modules/lambda/aws//modules/docker-build"

  create_ecr_repo = true
  ecr_repo        = "climate-analysis"

  use_image_tag = true
  image_tag     = local.docker_tag

  source_path = "../"

  ecr_repo_lifecycle_policy = jsonencode({
    "rules" : [
      {
        "rulePriority" : 1,
        "description" : "Keep only the last 1 image",
        "selection" : {
          "tagStatus" : "any",
          "countType" : "imageCountMoreThan",
          "countNumber" : 1
        },
        "action" : {
          "type" : "expire"
        }
      }
    ]
  })
}

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

resource "aws_iam_role_policy_attachment" "ecs_read" {
  role       = aws_iam_role.app_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.app_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "app_role_policy_attach" {
  role       = aws_iam_role.app_role.name
  policy_arn = aws_iam_policy.policy.arn
}

###---------------------------------------------

# Create api gateway

resource "aws_apigatewayv2_api" "api" {
  name          = "climate-analysis-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id                 = aws_apigatewayv2_api.api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = module.aws_lambda_function.lambda_function_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "root_route" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_stage" "default_stage" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "apigw_invoke" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = module.aws_lambda_function.lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}

###---------------------------------------------



