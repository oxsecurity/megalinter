resource "aws_ami" "good_example" {
  name                = "terraform-example"
  virtualization_type = "hvm"
  root_device_name    = "/dev/xvda2"

  ebs_block_device {
    device_name = "/dev/xvda2"
    snapshot_id = "snap-xxxxxxxx"
    volume_size = 8
	  encrypted   = true
  }

  tags = {
    Name = "test-ami-good-example"
    MyTag = "test-tag"
  }
}
