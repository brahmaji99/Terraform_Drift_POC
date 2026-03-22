provider "aws" {
  region = "ap-southeast-2"
}

module "s3" {
  source      = "../../modules/s3"
  bucket_name = "brahmaji-dev-bucket-12345"

 }

resource "aws_s3_bucket_versioning" "versioning" {
  bucket = module.s3.bucket_id   # or bucket name output

  versioning_configuration {
    status = "Suspended"
  }
}