provider "aws" {
  region = "ap-southeast-2"
}

module "iam" {
  source    = "../../modules/iam"
  user_name = "high-risk-user"
}