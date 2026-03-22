provider "aws" {
  region = "ap-southeast-2"
}

module "s3" {
  source      = "../../modules/s3"
  bucket_name = "brahmaji-dev-bucket-12345"

  versioning_configuration {
    status = "Suspended"   # or Disabled
  }
}