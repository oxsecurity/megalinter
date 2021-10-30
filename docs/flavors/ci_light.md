# ci_light Mega-Linter Flavor

![Docker Image Size (tag)](https://img.shields.io/docker/image-size/megalinter/megalinter-ci_light/v5)
![Docker Pulls](https://img.shields.io/docker/pulls/megalinter/megalinter-ci_light)

## Description

Optimized for CI items (Dockerfile, Jenkinsfile, JSON/YAML schemas,XML

## Usage

- [GitHub Action](https://megalinter.github.io/installation/#github-action): **megalinter/megalinter/flavors/ci_light@v5**
- Docker image: **megalinter/megalinter-ci_light:v5**
- [mega-linter-runner](https://megalinter.github.io/mega-linter-runner/): `mega-linter-runner --flavor ci_light`

## Embedded linters

### Languages

|                                                                              <!-- -->                                                                              | Language                                                       | Linter                                                                              | Configuration key                                                                          |     Format/Fix     |
|:------------------------------------------------------------------------------------------------------------------------------------------------------------------:|----------------------------------------------------------------|-------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|:------------------:|
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/groovy.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**GROOVY**](https://megalinter.github.io/descriptors/groovy/) | [npm-groovy-lint](https://megalinter.github.io/descriptors/groovy_npm_groovy_lint/) | [GROOVY_NPM_GROOVY_LINT](https://megalinter.github.io/descriptors/groovy_npm_groovy_lint/) | :heavy_check_mark: |

### Formats

|                                                                             <!-- -->                                                                             | Format                                                     | Linter                                                                                    | Configuration key                                                                              |     Format/Fix     |
|:----------------------------------------------------------------------------------------------------------------------------------------------------------------:|------------------------------------------------------------|-------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|:------------------:|
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/env.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->  | [**ENV**](https://megalinter.github.io/descriptors/env/)   | [dotenv-linter](https://megalinter.github.io/descriptors/env_dotenv_linter/)              | [ENV_DOTENV_LINTER](https://megalinter.github.io/descriptors/env_dotenv_linter/)               | :heavy_check_mark: |
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/json.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**JSON**](https://megalinter.github.io/descriptors/json/) | [jsonlint](https://megalinter.github.io/descriptors/json_jsonlint/)                       | [JSON_JSONLINT](https://megalinter.github.io/descriptors/json_jsonlint/)                       |                    |
|                                                                  <!-- --> <!-- linter-icon -->                                                                   |                                                            | [eslint-plugin-jsonc](https://megalinter.github.io/descriptors/json_eslint_plugin_jsonc/) | [JSON_ESLINT_PLUGIN_JSONC](https://megalinter.github.io/descriptors/json_eslint_plugin_jsonc/) | :heavy_check_mark: |
|                                                                  <!-- --> <!-- linter-icon -->                                                                   |                                                            | [v8r](https://megalinter.github.io/descriptors/json_v8r/)                                 | [JSON_V8R](https://megalinter.github.io/descriptors/json_v8r/)                                 |                    |
|                                                                  <!-- --> <!-- linter-icon -->                                                                   |                                                            | [prettier](https://megalinter.github.io/descriptors/json_prettier/)                       | [JSON_PRETTIER](https://megalinter.github.io/descriptors/json_prettier/)                       | :heavy_check_mark: |
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/xml.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->  | [**XML**](https://megalinter.github.io/descriptors/xml/)   | [xmllint](https://megalinter.github.io/descriptors/xml_xmllint/)                          | [XML_XMLLINT](https://megalinter.github.io/descriptors/xml_xmllint/)                           |                    |
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/yaml.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**YAML**](https://megalinter.github.io/descriptors/yaml/) | [prettier](https://megalinter.github.io/descriptors/yaml_prettier/)                       | [YAML_PRETTIER](https://megalinter.github.io/descriptors/yaml_prettier/)                       | :heavy_check_mark: |
|                                                                  <!-- --> <!-- linter-icon -->                                                                   |                                                            | [yamllint](https://megalinter.github.io/descriptors/yaml_yamllint/)                       | [YAML_YAMLLINT](https://megalinter.github.io/descriptors/yaml_yamllint/)                       |                    |
|                                                                  <!-- --> <!-- linter-icon -->                                                                   |                                                            | [v8r](https://megalinter.github.io/descriptors/yaml_v8r/)                                 | [YAML_V8R](https://megalinter.github.io/descriptors/yaml_v8r/)                                 |                    |

### Tooling formats

|                                                                                <!-- -->                                                                                | Tooling format                                                         | Linter                                                                                | Configuration key                                                                                | Format/Fix |
|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------:|------------------------------------------------------------------------|---------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|:----------:|
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/dockerfile.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**DOCKERFILE**](https://megalinter.github.io/descriptors/dockerfile/) | [dockerfilelint](https://megalinter.github.io/descriptors/dockerfile_dockerfilelint/) | [DOCKERFILE_DOCKERFILELINT](https://megalinter.github.io/descriptors/dockerfile_dockerfilelint/) |            |
|                                                                     <!-- --> <!-- linter-icon -->                                                                      |                                                                        | [hadolint](https://megalinter.github.io/descriptors/dockerfile_hadolint/)             | [DOCKERFILE_HADOLINT](https://megalinter.github.io/descriptors/dockerfile_hadolint/)             |            |

### Other

|                                                                            <!-- -->                                                                             | Code quality checker                                     | Linter                                                             | Configuration key                                                      | Format/Fix |
|:---------------------------------------------------------------------------------------------------------------------------------------------------------------:|----------------------------------------------------------|--------------------------------------------------------------------|------------------------------------------------------------------------|:----------:|
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/git.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**GIT**](https://megalinter.github.io/descriptors/git/) | [git_diff](https://megalinter.github.io/descriptors/git_git_diff/) | [GIT_GIT_DIFF](https://megalinter.github.io/descriptors/git_git_diff/) |            |

