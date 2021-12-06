# security MegaLinter Flavor

![Docker Image Size (tag)](https://img.shields.io/docker/image-size/megalinter/megalinter-security/v6-alpha)
![Docker Pulls](https://img.shields.io/docker/pulls/megalinter/megalinter-security)

## Description

Optimized for security

## Usage

- [GitHub Action](https://megalinter.github.io/v6-alpha/installation/#github-action): **megalinter/megalinter/flavors/security@v6-alpha**
- Docker image: **megalinter/megalinter-security:v6-alpha**
- [mega-linter-runner](https://megalinter.github.io/v6-alpha/mega-linter-runner/): `mega-linter-runner --flavor security`

## Embedded linters

### Languages

| <!-- --> | Language | Linter | Configuration key | Additional  |
| :---: | ----------------- | -------------- | ------------ | :-----:  |
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/bash.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**BASH**](https://megalinter.github.io/v6-alpha/descriptors/bash/) | [bash-exec](https://megalinter.github.io/v6-alpha/descriptors/bash_bash_exec/)| [BASH_EXEC](https://megalinter.github.io/v6-alpha/descriptors/bash_bash_exec/)| 
| <!-- --> <!-- linter-icon --> |  | [shellcheck](https://megalinter.github.io/v6-alpha/descriptors/bash_shellcheck/)| [BASH_SHELLCHECK](https://megalinter.github.io/v6-alpha/descriptors/bash_shellcheck/)| [![GitHub stars](https://img.shields.io/github/stars/koalaman/shellcheck?cacheSeconds=3600)](https://github.com/koalaman/shellcheck)
| <!-- --> <!-- linter-icon --> |  | [bandit](https://megalinter.github.io/v6-alpha/descriptors/python_bandit/)| [PYTHON_BANDIT](https://megalinter.github.io/v6-alpha/descriptors/python_bandit/)| [![GitHub stars](https://img.shields.io/github/stars/PyCQA/bandit?cacheSeconds=3600)](https://github.com/PyCQA/bandit) ![sarif](https://shields.io/badge/-SARIF-orange)

### Formats

| <!-- --> | Format | Linter | Configuration key | Additional  |
| :---: | ----------------- | -------------- | ------------ | :-----:  |

### Tooling formats

| <!-- --> | Tooling format | Linter | Configuration key | Additional  |
| :---: | ----------------- | -------------- | ------------ | :-----:  |
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/ansible.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**ANSIBLE**](https://megalinter.github.io/v6-alpha/descriptors/ansible/) | [ansible-lint](https://megalinter.github.io/v6-alpha/descriptors/ansible_ansible_lint/)| [ANSIBLE_ANSIBLE_LINT](https://megalinter.github.io/v6-alpha/descriptors/ansible_ansible_lint/)| [![GitHub stars](https://img.shields.io/github/stars/ansible/ansible-lint?cacheSeconds=3600)](https://github.com/ansible/ansible-lint)
| <!-- --> <!-- linter-icon --> |  | [hadolint](https://megalinter.github.io/v6-alpha/descriptors/dockerfile_hadolint/)| [DOCKERFILE_HADOLINT](https://megalinter.github.io/v6-alpha/descriptors/dockerfile_hadolint/)| [![GitHub stars](https://img.shields.io/github/stars/hadolint/hadolint?cacheSeconds=3600)](https://github.com/hadolint/hadolint)
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/kubernetes.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**KUBERNETES**](https://megalinter.github.io/v6-alpha/descriptors/kubernetes/) | [kubeval](https://megalinter.github.io/v6-alpha/descriptors/kubernetes_kubeval/)| [KUBERNETES_KUBEVAL](https://megalinter.github.io/v6-alpha/descriptors/kubernetes_kubeval/)| [![GitHub stars](https://img.shields.io/github/stars/instrumenta/kubeval?cacheSeconds=3600)](https://github.com/instrumenta/kubeval)
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/terraform.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**TERRAFORM**](https://megalinter.github.io/v6-alpha/descriptors/terraform/) | [tflint](https://megalinter.github.io/v6-alpha/descriptors/terraform_tflint/)| [TERRAFORM_TFLINT](https://megalinter.github.io/v6-alpha/descriptors/terraform_tflint/)| [![GitHub stars](https://img.shields.io/github/stars/terraform-linters/tflint?cacheSeconds=3600)](https://github.com/terraform-linters/tflint)
| <!-- --> <!-- linter-icon --> |  | [terrascan](https://megalinter.github.io/v6-alpha/descriptors/terraform_terrascan/)| [TERRAFORM_TERRASCAN](https://megalinter.github.io/v6-alpha/descriptors/terraform_terrascan/)| [![GitHub stars](https://img.shields.io/github/stars/accurics/terrascan?cacheSeconds=3600)](https://github.com/accurics/terrascan)
| <!-- --> <!-- linter-icon --> |  | [terragrunt](https://megalinter.github.io/v6-alpha/descriptors/terraform_terragrunt/)| [TERRAFORM_TERRAGRUNT](https://megalinter.github.io/v6-alpha/descriptors/terraform_terragrunt/)| [![GitHub stars](https://img.shields.io/github/stars/gruntwork-io/terragrunt?cacheSeconds=3600)](https://github.com/gruntwork-io/terragrunt) ![autofix](https://shields.io/badge/-autofix-green)
| <!-- --> <!-- linter-icon --> |  | [checkov](https://megalinter.github.io/v6-alpha/descriptors/terraform_checkov/)| [TERRAFORM_CHECKOV](https://megalinter.github.io/v6-alpha/descriptors/terraform_checkov/)| [![GitHub stars](https://img.shields.io/github/stars/bridgecrewio/checkov?cacheSeconds=3600)](https://github.com/bridgecrewio/checkov) ![sarif](https://shields.io/badge/-SARIF-orange)
| <!-- --> <!-- linter-icon --> |  | [kics](https://megalinter.github.io/v6-alpha/descriptors/terraform_kics/)| [TERRAFORM_KICS](https://megalinter.github.io/v6-alpha/descriptors/terraform_kics/)| [![GitHub stars](https://img.shields.io/github/stars/checkmarx/kics?cacheSeconds=3600)](https://github.com/checkmarx/kics)

### Other

| <!-- --> | Code quality checker | Linter | Configuration key | Additional  |
| :---: | ----------------- | -------------- | ------------ | :-----:  |
| <!-- --> <!-- linter-icon --> |  | [secretlint](https://megalinter.github.io/v6-alpha/descriptors/repository_secretlint/)| [REPOSITORY_SECRETLINT](https://megalinter.github.io/v6-alpha/descriptors/repository_secretlint/)| [![GitHub stars](https://img.shields.io/github/stars/secretlint/secretlint?cacheSeconds=3600)](https://github.com/secretlint/secretlint)
| <!-- --> <!-- linter-icon --> |  | [gitleaks](https://megalinter.github.io/v6-alpha/descriptors/repository_gitleaks/)| [REPOSITORY_GITLEAKS](https://megalinter.github.io/v6-alpha/descriptors/repository_gitleaks/)| [![GitHub stars](https://img.shields.io/github/stars/zricethezav/gitleaks?cacheSeconds=3600)](https://github.com/zricethezav/gitleaks) ![sarif](https://shields.io/badge/-SARIF-orange)
| <!-- --> <!-- linter-icon --> |  | [goodcheck](https://megalinter.github.io/v6-alpha/descriptors/repository_goodcheck/)| [REPOSITORY_GOODCHECK](https://megalinter.github.io/v6-alpha/descriptors/repository_goodcheck/)| [![GitHub stars](https://img.shields.io/github/stars/sider/goodcheck?cacheSeconds=3600)](https://github.com/sider/goodcheck)
| <!-- --> <!-- linter-icon --> |  | [trivy](https://megalinter.github.io/v6-alpha/descriptors/repository_trivy/)| [REPOSITORY_TRIVY](https://megalinter.github.io/v6-alpha/descriptors/repository_trivy/)| [![GitHub stars](https://img.shields.io/github/stars/aquasecurity/trivy?cacheSeconds=3600)](https://github.com/aquasecurity/trivy) ![sarif](https://shields.io/badge/-SARIF-orange)

