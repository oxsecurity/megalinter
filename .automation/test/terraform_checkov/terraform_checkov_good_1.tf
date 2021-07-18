resource "aws_ssm_parameter" "good" {
  name  = "foo"
  type  = "String"
  value = "bar"
}
