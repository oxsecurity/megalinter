resource "aws_sagemaker_domain" "pass" {
  domain_name = "examplea"
  auth_mode   = "IAM"
  analyzer_name = "example"
  vpc_id      = aws_vpc.test.id
  subnet_ids  = [aws_subnet.test.id]
  kms_key_id  = aws_kms_key.test.arn

  tags = {
    Environment = "test"
  }

  default_user_settings {
    execution_role = aws_iam_role.test.arn
  }

  retention_policy {
    home_efs_file_system = "Delete"
  }
}

resource "aws_organizations_organization" "example" {
  aws_service_access_principals = ["access-analyzer.amazonaws.com"]

  tags = {
    Environment = "test"
  }  
}

resource "aws_accessanalyzer_analyzer" "example" {
  depends_on = [aws_organizations_organization.example]

  analyzer_name = "example"
  type          = "ORGANIZATION"

  tags = {
    Environment = "test"
  }
}