// https://github.com/terraform-linters/tflint/blob/master/docs/user-guide/config.md

config {
  call_module_type = "local"
  force = false
}

plugin "terraform" {
  enabled = true
  preset  = "recommended"
}

plugin "azurerm" {
    enabled = true
    version = "0.28.0"
    source  = "github.com/terraform-linters/tflint-ruleset-azurerm"
}

plugin "aws" {
    enabled = true
    version = "0.38.0"
    source  = "github.com/terraform-linters/tflint-ruleset-aws"
}

plugin "google" {
    enabled = true
    version = "0.31.0"
    source  = "github.com/terraform-linters/tflint-ruleset-google"
}

rule "terraform_required_providers" {
  enabled = false
}
