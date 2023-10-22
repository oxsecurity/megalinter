terraform {
  required_version = ">= 1.2.5"
}

resource "aws_instance" "bad" {
  instance_type               = "t2.small"
  associate_public_ip_address = false

  murf = "cupcake8"

  ebs_block_device {
    encrypted = true
    wesh = false
  }
}

