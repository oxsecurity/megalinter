resource "aws_instanceee" "instanceWithNoVpc" {
  amiwu           = "some-id"
  instance_type = "t2.microblablabla"

  tagres = {
    Namex = "HelloWorld"
  }
}
