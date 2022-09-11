# Standalone linter docker images

| Linter key               | Docker image                                              |                                                              Size                                                              |
|:-------------------------|:----------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------:|
| ANSIBLE_ANSIBLE_LINT     | oxsecurity/megalinter-only-ansible_ansible_lint:6.9.0     |   ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-ansible_ansible_lint/6.9.0)   |
| BASH_SHELLCHECK          | oxsecurity/megalinter-only-bash_shellcheck:6.9.0          |     ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-bash_shellcheck/6.9.0)      |
| CLOUDFORMATION_CFN_LINT  | oxsecurity/megalinter-only-cloudformation_cfn_lint:6.9.0  | ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-cloudformation_cfn_lint/6.9.0)  |
| DOCKERFILE_HADOLINT      | oxsecurity/megalinter-only-dockerfile_hadolint:6.9.0      |   ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-dockerfile_hadolint/6.9.0)    |
| GO_REVIVE                | oxsecurity/megalinter-only-go_revive:6.9.0                |        ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-go_revive/6.9.0)         |
| GROOVY_NPM_GROOVY_LINT   | oxsecurity/megalinter-only-groovy_npm_groovy_lint:6.9.0   |  ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-groovy_npm_groovy_lint/6.9.0)  |
| JAVA_CHECKSTYLE          | oxsecurity/megalinter-only-java_checkstyle:6.9.0          |     ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-java_checkstyle/6.9.0)      |
| JAVA_PMD                 | oxsecurity/megalinter-only-java_pmd:6.9.0                 |         ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-java_pmd/6.9.0)         |
| JAVASCRIPT_ES            | oxsecurity/megalinter-only-javascript_es:6.9.0            |      ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-javascript_es/6.9.0)       |
| JSON_ESLINT_PLUGIN_JSONC | oxsecurity/megalinter-only-json_eslint_plugin_jsonc:6.9.0 | ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-json_eslint_plugin_jsonc/6.9.0) |
| JSX_ESLINT               | oxsecurity/megalinter-only-jsx_eslint:6.9.0               |        ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-jsx_eslint/6.9.0)        |
| KOTLIN_KTLINT            | oxsecurity/megalinter-only-kotlin_ktlint:6.9.0            |      ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-kotlin_ktlint/6.9.0)       |
| PHP_PSALM                | oxsecurity/megalinter-only-php_psalm:6.9.0                |        ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-php_psalm/6.9.0)         |
| PYTHON_BANDIT            | oxsecurity/megalinter-only-python_bandit:6.9.0            |      ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-python_bandit/6.9.0)       |
| REPOSITORY_CHECKOV       | oxsecurity/megalinter-only-repository_checkov:6.9.0       |    ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-repository_checkov/6.9.0)    |
| REPOSITORY_DEVSKIM       | oxsecurity/megalinter-only-repository_devskim:6.9.0       |    ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-repository_devskim/6.9.0)    |
| REPOSITORY_DUSTILOCK     | oxsecurity/megalinter-only-repository_dustilock:6.9.0     |   ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-repository_dustilock/6.9.0)   |
| REPOSITORY_GITLEAKS      | oxsecurity/megalinter-only-repository_gitleaks:6.9.0      |   ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-repository_gitleaks/6.9.0)    |
| REPOSITORY_SECRETLINT    | oxsecurity/megalinter-only-repository_secretlint:6.9.0    |  ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-repository_secretlint/6.9.0)   |
| REPOSITORY_SEMGREP       | oxsecurity/megalinter-only-repository_semgrep:6.9.0       |    ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-repository_semgrep/6.9.0)    |
| REPOSITORY_SYFT          | oxsecurity/megalinter-only-repository_syft:6.9.0          |     ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-repository_syft/6.9.0)      |
| REPOSITORY_TRIVY         | oxsecurity/megalinter-only-repository_trivy:6.9.0         |     ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-repository_trivy/6.9.0)     |
| TERRAFORM_TFLINT         | oxsecurity/megalinter-only-terraform_tflint:6.9.0         |     ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-terraform_tflint/6.9.0)     |
| TERRAFORM_TERRASCAN      | oxsecurity/megalinter-only-terraform_terrascan:6.9.0      |   ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-terraform_terrascan/6.9.0)    |
| TERRAFORM_CHECKOV        | oxsecurity/megalinter-only-terraform_checkov:6.9.0        |    ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-terraform_checkov/6.9.0)     |
| TSX_ESLINT               | oxsecurity/megalinter-only-tsx_eslint:6.9.0               |        ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-tsx_eslint/6.9.0)        |
| TYPESCRIPT_ES            | oxsecurity/megalinter-only-typescript_es:6.9.0            |      ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-only-typescript_es/6.9.0)       |

