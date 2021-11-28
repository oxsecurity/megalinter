# security MegaLinter Flavor

![Docker Image Size (tag)](https://img.shields.io/docker/image-size/megalinter/megalinter-security/v5)
![Docker Pulls](https://img.shields.io/docker/pulls/megalinter/megalinter-security)

## Description

Optimized for security

## Usage

- [GitHub Action](https://megalinter.github.io/installation/#github-action): **megalinter/megalinter/flavors/security@v5**
- Docker image: **megalinter/megalinter-security:v5**
- [mega-linter-runner](https://megalinter.github.io/mega-linter-runner/): `mega-linter-runner --flavor security`

## Embedded linters

### Languages

|                                                                            <!-- -->                                                                            | Language                                                   | Linter                                                                  | Configuration key                                                            | Format/Fix |
|:--------------------------------------------------------------------------------------------------------------------------------------------------------------:|------------------------------------------------------------|-------------------------------------------------------------------------|------------------------------------------------------------------------------|:----------:|
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/bash.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**BASH**](https://megalinter.github.io/descriptors/bash/) | [bash-exec](https://megalinter.github.io/descriptors/bash_bash_exec/)   | [BASH_EXEC](https://megalinter.github.io/descriptors/bash_bash_exec/)        |            |
|                                                                 <!-- --> <!-- linter-icon -->                                                                  |                                                            | [shellcheck](https://megalinter.github.io/descriptors/bash_shellcheck/) | [BASH_SHELLCHECK](https://megalinter.github.io/descriptors/bash_shellcheck/) |            |
|                                                                 <!-- --> <!-- linter-icon -->                                                                  |                                                            | [bandit](https://megalinter.github.io/descriptors/python_bandit/)       | [PYTHON_BANDIT](https://megalinter.github.io/descriptors/python_bandit/)     |            |

### Formats

| <!-- --> | Format | Linter | Configuration key | Format/Fix |
| :---: | ----------------- | -------------- | ------------ | :-----: |

### Tooling formats

|                                                                              <!-- -->                                                                               | Tooling format                                                       | Linter                                                                         | Configuration key                                                                      |     Format/Fix     |
|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------:|----------------------------------------------------------------------|--------------------------------------------------------------------------------|----------------------------------------------------------------------------------------|:------------------:|
|  <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/ansible.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->  | [**ANSIBLE**](https://megalinter.github.io/descriptors/ansible/)     | [ansible-lint](https://megalinter.github.io/descriptors/ansible_ansible_lint/) | [ANSIBLE_ANSIBLE_LINT](https://megalinter.github.io/descriptors/ansible_ansible_lint/) |                    |
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/terraform.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**TERRAFORM**](https://megalinter.github.io/descriptors/terraform/) | [tflint](https://megalinter.github.io/descriptors/terraform_tflint/)           | [TERRAFORM_TFLINT](https://megalinter.github.io/descriptors/terraform_tflint/)         |                    |
|                                                                    <!-- --> <!-- linter-icon -->                                                                    |                                                                      | [terrascan](https://megalinter.github.io/descriptors/terraform_terrascan/)     | [TERRAFORM_TERRASCAN](https://megalinter.github.io/descriptors/terraform_terrascan/)   |                    |
|                                                                    <!-- --> <!-- linter-icon -->                                                                    |                                                                      | [terragrunt](https://megalinter.github.io/descriptors/terraform_terragrunt/)   | [TERRAFORM_TERRAGRUNT](https://megalinter.github.io/descriptors/terraform_terragrunt/) | :heavy_check_mark: |
|                                                                    <!-- --> <!-- linter-icon -->                                                                    |                                                                      | [checkov](https://megalinter.github.io/descriptors/terraform_checkov/)         | [TERRAFORM_CHECKOV](https://megalinter.github.io/descriptors/terraform_checkov/)       |                    |
|                                                                    <!-- --> <!-- linter-icon -->                                                                    |                                                                      | [kics](https://megalinter.github.io/descriptors/terraform_kics/)               | [TERRAFORM_KICS](https://megalinter.github.io/descriptors/terraform_kics/)             |                    |

### Other

|                                                                             <!-- -->                                                                              | Code quality checker                                                   | Linter                                                                        | Configuration key                                                                        | Format/Fix |
|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------:|------------------------------------------------------------------------|-------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|:----------:|
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/default.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**REPOSITORY**](https://megalinter.github.io/descriptors/repository/) | [git_diff](https://megalinter.github.io/descriptors/repository_git_diff/)     | [REPOSITORY_GIT_DIFF](https://megalinter.github.io/descriptors/repository_git_diff/)     |            |
|                                                                   <!-- --> <!-- linter-icon -->                                                                   |                                                                        | [secretlint](https://megalinter.github.io/descriptors/repository_secretlint/) | [REPOSITORY_SECRETLINT](https://megalinter.github.io/descriptors/repository_secretlint/) |            |
|                                                                   <!-- --> <!-- linter-icon -->                                                                   |                                                                        | [gitleaks](https://megalinter.github.io/descriptors/repository_gitleaks/)     | [REPOSITORY_GITLEAKS](https://megalinter.github.io/descriptors/repository_gitleaks/)     |            |
|                                                                   <!-- --> <!-- linter-icon -->                                                                   |                                                                        | [goodcheck](https://megalinter.github.io/descriptors/repository_goodcheck/)   | [REPOSITORY_GOODCHECK](https://megalinter.github.io/descriptors/repository_goodcheck/)   |            |
|                                                                   <!-- --> <!-- linter-icon -->                                                                   |                                                                        | [trivy](https://megalinter.github.io/descriptors/repository_trivy/)           | [REPOSITORY_TRIVY](https://megalinter.github.io/descriptors/repository_trivy/)           |            |

