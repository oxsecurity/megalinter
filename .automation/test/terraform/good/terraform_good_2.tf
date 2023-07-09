resource "aws_instance" "good" {
  required_version = ">= 0.15.0"
  ami                         = "ami-0ff8a91507f77f867"
  instance_type               = "t2.small"
  associate_public_ip_address = false

  vpc_security_group_ids = ["sg-12345678901234567"]

  ebs_block_device {
    encrypted = true
  }
}

