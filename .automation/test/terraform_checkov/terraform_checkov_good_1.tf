resource "aws_secretsmanager_secret" "good" {
  name  = "foo"
  type  = "String"
  value = "bar"
}
