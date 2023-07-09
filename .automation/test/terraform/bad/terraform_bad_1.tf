resource "aws_instance" "bad" {
  instance_type               = "t2.small"
  associate_public_ip_address = false


  ebs_block_device {
    encrypted = true
    wesh = false
  }
}

