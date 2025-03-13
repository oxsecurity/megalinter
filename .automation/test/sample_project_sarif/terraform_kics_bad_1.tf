resource "aws_ami" "bad_example" {
  name                = "terraform-example"
  virtualization_type = "hvm"
  root_device_name    = "/dev/xvda2"

  ebs_block_device {
    device_name = "/dev/xvda2"
    snapshot_id = "snap-xxxxxxxx"
    volume_size = 8
	  encrypted   = false
  }
}
