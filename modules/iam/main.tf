resource "aws_iam_user" "user" {
  name = var.user_name
}

resource "aws_iam_user_policy" "admin_policy" {
  name = "admin-policy"
  user = aws_iam_user.user.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "*"
      Resource = "*"
    }]
  })
}