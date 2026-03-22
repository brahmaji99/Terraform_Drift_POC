provider "aws" {
  region = "ap-southeast-2"
}

module "ec2" {
  source        = "../../modules/ec2"
  ami_id        = "ami-0abcdef1234567890"
  instance_type = "t3.small"
}