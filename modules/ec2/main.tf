resource "aws_instance" "ec2" {
  ami           = var.ami_id
  instance_type = var.instance_type

  vpc_security_group_ids = [aws_security_group.ec2_sg.id]

  tags = {
    Name = "Demo-EC2"
  }
}

# ✅ Security Group (no inline rules)
resource "aws_security_group" "ec2_sg" {
  name        = "ec2-sg"
  revoke_rules_on_delete = true
  description = "EC2 security group"
}

# ✅ SSH Rule
resource "aws_security_group_rule" "ssh" {
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = ["10.0.0.0/16"]
  security_group_id = aws_security_group.ec2_sg.id
}

# ✅ Outbound Rule
resource "aws_security_group_rule" "egress" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.ec2_sg.id
}