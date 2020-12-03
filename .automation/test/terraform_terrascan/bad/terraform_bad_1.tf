resource "aws_instance" "nico" {
  ami           = "some-id"
  instance_type = "t2.micro"

  tags = {
    Name = "HelloWorld"
  }
}
