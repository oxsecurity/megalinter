terraform {
  required_version = ">= 1.2.5"
}

resource "aws_instance" "bad" {
  ami                         = "ami-0ff8a91507f77f867"
  associate_public_ip_address = false

  vpc_security_group_ids = ["sg-12345678901234567"]

  murf = "cupcake"

  ebs_block_device {
    encrypted = true
    wesh2 = false
  }
}

