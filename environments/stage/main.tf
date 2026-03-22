provider "aws" {
  region = "ap-southeast-2"
}

module "ec2" {
  source        = "../../modules/ec2"
  ami_id        = "ami-0f5d1713c9af4fe30"
  instance_type = "t3.small"
}