resource "aws_instance" "instanceWithNoVpc2" {
  ami           = "some-id"
  instance_type = "t2.micro"

  tags = {
    Name = "HelloWorld2"
  }
}
