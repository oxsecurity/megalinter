# ci_light MegaLinter Flavor

![Docker Image Size (tag)](https://img.shields.io/docker/image-size/megalinter/megalinter-ci_light/v6-alpha)
![Docker Pulls](https://img.shields.io/docker/pulls/megalinter/megalinter-ci_light)

## Description

Optimized for CI items (Dockerfile, Jenkinsfile, JSON/YAML schemas,XML

## Usage

- [GitHub Action](https://megalinter.github.io/v6-alpha/installation/#github-action): **megalinter/megalinter/flavors/ci_light@v6-alpha**
- Docker image: **megalinter/megalinter-ci_light:v6-alpha**
- [mega-linter-runner](https://megalinter.github.io/v6-alpha/mega-linter-runner/): `mega-linter-runner --flavor ci_light`

## Embedded linters

### Languages

| <!-- --> | Language | Linter | Configuration key | Additional  |
| :---: | ----------------- | -------------- | ------------ | :-----:  |
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/groovy.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**GROOVY**](https://megalinter.github.io/v6-alpha/descriptors/groovy/) | [npm-groovy-lint](https://megalinter.github.io/v6-alpha/descriptors/groovy_npm_groovy_lint/)| [GROOVY_NPM_GROOVY_LINT](https://megalinter.github.io/v6-alpha/descriptors/groovy_npm_groovy_lint/)| [![GitHub stars](https://img.shields.io/github/stars/nvuillam/npm-groovy-lint?cacheSeconds=3600)](https://github.com/nvuillam/npm-groovy-lint) ![autofix](https://shields.io/badge/-autofix-green)

### Formats

| <!-- --> | Format | Linter | Configuration key | Additional  |
| :---: | ----------------- | -------------- | ------------ | :-----:  |
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/env.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**ENV**](https://megalinter.github.io/v6-alpha/descriptors/env/) | [dotenv-linter](https://megalinter.github.io/v6-alpha/descriptors/env_dotenv_linter/)| [ENV_DOTENV_LINTER](https://megalinter.github.io/v6-alpha/descriptors/env_dotenv_linter/)| [![GitHub stars](https://img.shields.io/github/stars/dotenv-linter/dotenv-linter?cacheSeconds=3600)](https://github.com/dotenv-linter/dotenv-linter) ![autofix](https://shields.io/badge/-autofix-green)
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/json.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**JSON**](https://megalinter.github.io/v6-alpha/descriptors/json/) | [jsonlint](https://megalinter.github.io/v6-alpha/descriptors/json_jsonlint/)| [JSON_JSONLINT](https://megalinter.github.io/v6-alpha/descriptors/json_jsonlint/)| [![GitHub stars](https://img.shields.io/github/stars/zaach/jsonlint?cacheSeconds=3600)](https://github.com/zaach/jsonlint)
| <!-- --> <!-- linter-icon --> |  | [eslint-plugin-jsonc](https://megalinter.github.io/v6-alpha/descriptors/json_eslint_plugin_jsonc/)| [JSON_ESLINT_PLUGIN_JSONC](https://megalinter.github.io/v6-alpha/descriptors/json_eslint_plugin_jsonc/)| [![GitHub stars](https://img.shields.io/github/stars/ota-meshi/eslint-plugin-jsonc?cacheSeconds=3600)](https://github.com/ota-meshi/eslint-plugin-jsonc) ![autofix](https://shields.io/badge/-autofix-green) ![sarif](https://shields.io/badge/-SARIF-orange)
| <!-- --> <!-- linter-icon --> |  | [v8r](https://megalinter.github.io/v6-alpha/descriptors/json_v8r/)| [JSON_V8R](https://megalinter.github.io/v6-alpha/descriptors/json_v8r/)| [![GitHub stars](https://img.shields.io/github/stars/chris48s/v8r?cacheSeconds=3600)](https://github.com/chris48s/v8r)
| <!-- --> <!-- linter-icon --> |  | [prettier](https://megalinter.github.io/v6-alpha/descriptors/json_prettier/)| [JSON_PRETTIER](https://megalinter.github.io/v6-alpha/descriptors/json_prettier/)| [![GitHub stars](https://img.shields.io/github/stars/prettier/prettier?cacheSeconds=3600)](https://github.com/prettier/prettier) ![formatter](https://shields.io/badge/-format-yellow)
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/xml.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**XML**](https://megalinter.github.io/v6-alpha/descriptors/xml/) | [xmllint](https://megalinter.github.io/v6-alpha/descriptors/xml_xmllint/)| [XML_XMLLINT](https://megalinter.github.io/v6-alpha/descriptors/xml_xmllint/)| 
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/yaml.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**YAML**](https://megalinter.github.io/v6-alpha/descriptors/yaml/) | [prettier](https://megalinter.github.io/v6-alpha/descriptors/yaml_prettier/)| [YAML_PRETTIER](https://megalinter.github.io/v6-alpha/descriptors/yaml_prettier/)| [![GitHub stars](https://img.shields.io/github/stars/prettier/prettier?cacheSeconds=3600)](https://github.com/prettier/prettier) ![formatter](https://shields.io/badge/-format-yellow)
| <!-- --> <!-- linter-icon --> |  | [yamllint](https://megalinter.github.io/v6-alpha/descriptors/yaml_yamllint/)| [YAML_YAMLLINT](https://megalinter.github.io/v6-alpha/descriptors/yaml_yamllint/)| [![GitHub stars](https://img.shields.io/github/stars/adrienverge/yamllint?cacheSeconds=3600)](https://github.com/adrienverge/yamllint)
| <!-- --> <!-- linter-icon --> |  | [v8r](https://megalinter.github.io/v6-alpha/descriptors/yaml_v8r/)| [YAML_V8R](https://megalinter.github.io/v6-alpha/descriptors/yaml_v8r/)| [![GitHub stars](https://img.shields.io/github/stars/chris48s/v8r?cacheSeconds=3600)](https://github.com/chris48s/v8r)

### Tooling formats

| <!-- --> | Tooling format | Linter | Configuration key | Additional  |
| :---: | ----------------- | -------------- | ------------ | :-----:  |
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/dockerfile.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**DOCKERFILE**](https://megalinter.github.io/v6-alpha/descriptors/dockerfile/) | [hadolint](https://megalinter.github.io/v6-alpha/descriptors/dockerfile_hadolint/)| [DOCKERFILE_HADOLINT](https://megalinter.github.io/v6-alpha/descriptors/dockerfile_hadolint/)| [![GitHub stars](https://img.shields.io/github/stars/hadolint/hadolint?cacheSeconds=3600)](https://github.com/hadolint/hadolint) ![sarif](https://shields.io/badge/-SARIF-orange)

### Other

| <!-- --> | Code quality checker | Linter | Configuration key | Additional  |
| :---: | ----------------- | -------------- | ------------ | :-----:  |
| <!-- --> <!-- linter-icon --> |  | [git_diff](https://megalinter.github.io/v6-alpha/descriptors/repository_git_diff/)| [REPOSITORY_GIT_DIFF](https://megalinter.github.io/v6-alpha/descriptors/repository_git_diff/)| [![GitHub stars](https://img.shields.io/github/stars/git/git?cacheSeconds=3600)](https://github.com/git/git)
| <!-- --> <!-- linter-icon --> |  | [gitleaks](https://megalinter.github.io/v6-alpha/descriptors/repository_gitleaks/)| [REPOSITORY_GITLEAKS](https://megalinter.github.io/v6-alpha/descriptors/repository_gitleaks/)| [![GitHub stars](https://img.shields.io/github/stars/zricethezav/gitleaks?cacheSeconds=3600)](https://github.com/zricethezav/gitleaks) ![sarif](https://shields.io/badge/-SARIF-orange)
| <!-- --> <!-- linter-icon --> |  | [goodcheck](https://megalinter.github.io/v6-alpha/descriptors/repository_goodcheck/)| [REPOSITORY_GOODCHECK](https://megalinter.github.io/v6-alpha/descriptors/repository_goodcheck/)| [![GitHub stars](https://img.shields.io/github/stars/sider/goodcheck?cacheSeconds=3600)](https://github.com/sider/goodcheck)
| <!-- --> <!-- linter-icon --> |  | [secretlint](https://megalinter.github.io/v6-alpha/descriptors/repository_secretlint/)| [REPOSITORY_SECRETLINT](https://megalinter.github.io/v6-alpha/descriptors/repository_secretlint/)| [![GitHub stars](https://img.shields.io/github/stars/secretlint/secretlint?cacheSeconds=3600)](https://github.com/secretlint/secretlint)
| <!-- --> <!-- linter-icon --> |  | [trivy](https://megalinter.github.io/v6-alpha/descriptors/repository_trivy/)| [REPOSITORY_TRIVY](https://megalinter.github.io/v6-alpha/descriptors/repository_trivy/)| [![GitHub stars](https://img.shields.io/github/stars/aquasecurity/trivy?cacheSeconds=3600)](https://github.com/aquasecurity/trivy) ![sarif](https://shields.io/badge/-SARIF-orange)

