<!-- markdownlint-disable MD013 MD033 MD041 -->

<!-- header-logo-start -->
<div align="center">
  <a href="https://nvuillam.github.io/mega-linter" target="blank" title="Visit Mega-Linter Web Site">
    <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/images/mega-linter-logo.png" alt="Mega-Linter" height="300px">
  </a>
</div>
<!-- header-logo-end -->

# Mega-Linter Runner
<!-- readme-header-start -->
[![Version](https://img.shields.io/npm/v/mega-linter-runner.svg)](https://npmjs.org/package/mega-linter-runner)
[![Docker Pulls](https://img.shields.io/docker/pulls/nvuillam/mega-linter)](https://hub.docker.com/r/nvuillam/mega-linter)
[![Mega-Linter](https://github.com/nvuillam/mega-linter/workflows/Mega-Linter/badge.svg?branch=master)](https://nvuillam.github.io/mega-linter)
[![codecov](https://codecov.io/gh/nvuillam/mega-linter/branch/master/graph/badge.svg)](https://codecov.io/gh/nvuillam/mega-linter)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

<!-- welcome-phrase-start -->
**Mega-Linter** analyzes [**37 languages**](#languages), [**15 formats**](#formats), [**16 tooling formats**](#tooling-formats) , [**copy-pastes**](#other) and [**spell**](#other) in your repository sources, generate [**reports in several formats**](#reports), and can even [**apply formatting and auto-fixes**](#apply-fixes) with **auto-generated commit or PR**, to ensure all your projects are clean, whatever IDE/toolbox are used by their developers !
<!-- welcome-phrase-end -->

<!-- online-doc-start -->
See [**Mega-Linter Online Documentation Web Site**](https://nvuillam.github.io/mega-linter/)
<!-- online-doc-end -->

<!-- readme-header-end -->

This package allows to run [Mega-Linter](https://nvuillam.github.io/mega-linter/) locally before running it in your CD/CI workflow, or simply to locally apply reformatting and fixes without having to install up to date linters for your files

## Installation

### Pre-requisites

You need to have [NodeJS](https://nodejs.org/en/) and [Docker](https://www.docker.com/) installed on your computer to run Mega-Linter locally with Mega-Linter Runner

### Global installation

```shell
npm install mega-linter-runner -g
```

### Local installation

```shell
npm install mega-linter-runner --save-dev
```

### No installation

You can run mega-linter-runner without installation by using `npx`

Example:

```shell
npx mega-linter-runner -r insiders -e 'ENABLE=MARKDOWN,YAML' -e 'SHOW_ELAPSED_TIME=true'
```

## Usage

```shell
mega-linter-runner [OPTIONS]
```

The options are only related to mega-linter-runner. For Mega-Linter options, please use a `.mega-linter.yml` [configuration file](#configuration)

| Option             | Description                                               |
|--------------------|-----------------------------------------------------------|
| `-p` `--path`      | Directory containing the files to lint (default: current directory)    |
| `-e` `--env`      | Environment variables for Mega-Linter, following format **'ENV_VAR_NAME=VALUE'** (Warning: Quotes are mandatory)    |
| `--fix`            | Automatically apply formatting and fixes in your files    |
| `-r` `--release`    | Allows to override Mega-Linter version used (default: v4 stable)  |
| `-h` `--help`      | Show mega-linter-runner help    |
| `-v` `--version`   | Show mega-linter-runner version    |

_You can also use `npx mega-linter-runner` if you do not want to install the package_

### Examples

```shell
mega-linter-runner
```

```shell
mega-linter-runner -p myFolder --fix
```

```shell
mega-linter-runner -r insiders -e 'ENABLE=MARKDOWN,YAML' -e 'SHOW_ELAPSED_TIME=true'
```

## Configuration

Default configuration is ready out of the box

You can define a [.mega-linter.yml](https://nvuillam.github.io/mega-linter/configuration/) configuration file at the root of your repository to customize or deactivate the included linters
<!-- linters-section-start -->
## Linters

<!-- linters-table-start -->
### Languages

| <!-- --> | Language / Format | Linter | Configuration key | Fix |
| --- | ----------------- | -------------- | ------------ | ------- |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/bash.ico" alt="" height="32px" class="megalinter-icon"></a> | [**BASH**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/bash.md#readme) | [bash-exec](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/bash_bash_exec.md#readme)| [BASH_EXEC](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/bash_bash_exec.md#readme)|  |
| <!-- --> |  | [shellcheck](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/bash_shellcheck.md#readme)| [BASH_SHELLCHECK](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/bash_shellcheck.md#readme)|  |
| <!-- --> |  | [shfmt](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/bash_shfmt.md#readme)| [BASH_SHFMT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/bash_shfmt.md#readme)| :heavy_check_mark: |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/c.ico" alt="" height="32px" class="megalinter-icon"></a> | [**C**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/c.md#readme) | [cpplint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/c_cpplint.md#readme)| [C_CPPLINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/c_cpplint.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/clojure.ico" alt="" height="32px" class="megalinter-icon"></a> | [**CLOJURE**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/clojure.md#readme) | [clj-kondo](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/clojure_clj_kondo.md#readme)| [CLOJURE_CLJ_KONDO](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/clojure_clj_kondo.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/coffee.ico" alt="" height="32px" class="megalinter-icon"></a> | [**COFFEE**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/coffee.md#readme) | [coffeelint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/coffee_coffeelint.md#readme)| [COFFEE_COFFEELINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/coffee_coffeelint.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/cpp.ico" alt="" height="32px" class="megalinter-icon"></a> | [**C++** (CPP)](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/cpp.md#readme) | [cpplint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/cpp_cpplint.md#readme)| [CPP_CPPLINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/cpp_cpplint.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/csharp.ico" alt="" height="32px" class="megalinter-icon"></a> | [**C#** (CSHARP)](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/csharp.md#readme) | [dotnet-format](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/csharp_dotnet_format.md#readme)| [CSHARP_DOTNET_FORMAT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/csharp_dotnet_format.md#readme)| :heavy_check_mark: |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/dart.ico" alt="" height="32px" class="megalinter-icon"></a> | [**DART**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/dart.md#readme) | [dartanalyzer](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/dart_dartanalyzer.md#readme)| [DART_DARTANALYZER](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/dart_dartanalyzer.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/go.ico" alt="" height="32px" class="megalinter-icon"></a> | [**GO**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/go.md#readme) | [golangci-lint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/go_golangci_lint.md#readme)| [GO_GOLANGCI_LINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/go_golangci_lint.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/groovy.ico" alt="" height="32px" class="megalinter-icon"></a> | [**GROOVY**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/groovy.md#readme) | [npm-groovy-lint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/groovy_npm_groovy_lint.md#readme)| [GROOVY_NPM_GROOVY_LINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/groovy_npm_groovy_lint.md#readme)| :heavy_check_mark: |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/java.ico" alt="" height="32px" class="megalinter-icon"></a> | [**JAVA**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/java.md#readme) | [checkstyle](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/java_checkstyle.md#readme)| [JAVA_CHECKSTYLE](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/java_checkstyle.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/javascript.ico" alt="" height="32px" class="megalinter-icon"></a> | [**JAVASCRIPT**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/javascript.md#readme) | [eslint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/javascript_eslint.md#readme)| [JAVASCRIPT_ES](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/javascript_eslint.md#readme)| :heavy_check_mark: |
| <!-- --> |  | [standard](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/javascript_standard.md#readme)| [JAVASCRIPT_STANDARD](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/javascript_standard.md#readme)| :heavy_check_mark: |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/jsx.ico" alt="" height="32px" class="megalinter-icon"></a> | [**JSX**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/jsx.md#readme) | [eslint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/jsx_eslint.md#readme)| [JSX_ESLINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/jsx_eslint.md#readme)| :heavy_check_mark: |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/kotlin.ico" alt="" height="32px" class="megalinter-icon"></a> | [**KOTLIN**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/kotlin.md#readme) | [ktlint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/kotlin_ktlint.md#readme)| [KOTLIN_KTLINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/kotlin_ktlint.md#readme)| :heavy_check_mark: |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/lua.ico" alt="" height="32px" class="megalinter-icon"></a> | [**LUA**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/lua.md#readme) | [luacheck](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/lua_luacheck.md#readme)| [LUA_LUACHECK](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/lua_luacheck.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/perl.ico" alt="" height="32px" class="megalinter-icon"></a> | [**PERL**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/perl.md#readme) | [perlcritic](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/perl_perlcritic.md#readme)| [PERL_PERLCRITIC](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/perl_perlcritic.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/php.ico" alt="" height="32px" class="megalinter-icon"></a> | [**PHP**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/php.md#readme) | [php](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/php_php.md#readme)| [PHP_BUILTIN](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/php_php.md#readme)|  |
| <!-- --> |  | [phpcs](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/php_phpcs.md#readme)| [PHP_PHPCS](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/php_phpcs.md#readme)|  |
| <!-- --> |  | [phpstan](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/php_phpstan.md#readme)| [PHP_PHPSTAN](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/php_phpstan.md#readme)|  |
| <!-- --> |  | [psalm](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/php_psalm.md#readme)| [PHP_PSALM](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/php_psalm.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/powershell.ico" alt="" height="32px" class="megalinter-icon"></a> | [**POWERSHELL**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/powershell.md#readme) | [powershell](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/powershell_powershell.md#readme)| [POWERSHELL_POWERSHELL](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/powershell_powershell.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/python.ico" alt="" height="32px" class="megalinter-icon"></a> | [**PYTHON**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/python.md#readme) | [pylint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/python_pylint.md#readme)| [PYTHON_PYLINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/python_pylint.md#readme)|  |
| <!-- --> |  | [black](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/python_black.md#readme)| [PYTHON_BLACK](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/python_black.md#readme)| :heavy_check_mark: |
| <!-- --> |  | [flake8](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/python_flake8.md#readme)| [PYTHON_FLAKE8](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/python_flake8.md#readme)|  |
| <!-- --> |  | [isort](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/python_isort.md#readme)| [PYTHON_ISORT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/python_isort.md#readme)| :heavy_check_mark: |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/r.ico" alt="" height="32px" class="megalinter-icon"></a> | [**R**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/r.md#readme) | [lintr](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/r_lintr.md#readme)| [R_LINTR](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/r_lintr.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/raku.ico" alt="" height="32px" class="megalinter-icon"></a> | [**RAKU**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/raku.md#readme) | [raku](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/raku_raku.md#readme)| [RAKU_RAKU](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/raku_raku.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/ruby.ico" alt="" height="32px" class="megalinter-icon"></a> | [**RUBY**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/ruby.md#readme) | [rubocop](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/ruby_rubocop.md#readme)| [RUBY_RUBOCOP](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/ruby_rubocop.md#readme)| :heavy_check_mark: |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/rust.ico" alt="" height="32px" class="megalinter-icon"></a> | [**RUST**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/rust.md#readme) | [clippy](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/rust_clippy.md#readme)| [RUST_CLIPPY](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/rust_clippy.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/default.ico" alt="" height="32px" class="megalinter-icon"></a> | [**SALESFORCE**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/salesforce.md#readme) | [sfdx-scanner](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/salesforce_sfdx_scanner.md#readme)| [SALESFORCE_SFDX_SCANNER](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/salesforce_sfdx_scanner.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/scala.ico" alt="" height="32px" class="megalinter-icon"></a> | [**SCALA**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/scala.md#readme) | [scalafix](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/scala_scalafix.md#readme)| [SCALA_SCALAFIX](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/scala_scalafix.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/sql.ico" alt="" height="32px" class="megalinter-icon"></a> | [**SQL**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/sql.md#readme) | [sql-lint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/sql_sql_lint.md#readme)| [SQL_SQL_LINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/sql_sql_lint.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/tsx.ico" alt="" height="32px" class="megalinter-icon"></a> | [**TSX**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/tsx.md#readme) | [eslint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/tsx_eslint.md#readme)| [TSX_ESLINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/tsx_eslint.md#readme)| :heavy_check_mark: |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/typescript.ico" alt="" height="32px" class="megalinter-icon"></a> | [**TYPESCRIPT**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/typescript.md#readme) | [eslint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/typescript_eslint.md#readme)| [TYPESCRIPT_ES](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/typescript_eslint.md#readme)| :heavy_check_mark: |
| <!-- --> |  | [standard](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/typescript_standard.md#readme)| [TYPESCRIPT_STANDARD](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/typescript_standard.md#readme)| :heavy_check_mark: |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/default.ico" alt="" height="32px" class="megalinter-icon"></a> | [**Visual Basic .NET** (VBDOTNET)](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/vbdotnet.md#readme) | [dotnet-format](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/vbdotnet_dotnet_format.md#readme)| [VBDOTNET_DOTNET_FORMAT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/vbdotnet_dotnet_format.md#readme)| :heavy_check_mark: |

### Formats

| <!-- --> | Language / Format | Linter | Configuration key | Fix |
| --- | ----------------- | -------------- | ------------ | ------- |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/css.ico" alt="" height="32px" class="megalinter-icon"></a> | [**CSS**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/css.md#readme) | [stylelint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/css_stylelint.md#readme)| [CSS_STYLELINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/css_stylelint.md#readme)| :heavy_check_mark: |
| <!-- --> |  | [scss-lint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/css_scss_lint.md#readme)| [CSS_SCSS_LINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/css_scss_lint.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/env.ico" alt="" height="32px" class="megalinter-icon"></a> | [**ENV**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/env.md#readme) | [dotenv-linter](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/env_dotenv_linter.md#readme)| [ENV_DOTENV_LINTER](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/env_dotenv_linter.md#readme)| :heavy_check_mark: |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/graphql.ico" alt="" height="32px" class="megalinter-icon"></a> | [**GRAPHQL**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/graphql.md#readme) | [graphql-schema-linter](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/graphql_graphql_schema_linter.md#readme)| [GRAPHQL_GRAPHQL_SCHEMA_LINTER](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/graphql_graphql_schema_linter.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/html.ico" alt="" height="32px" class="megalinter-icon"></a> | [**HTML**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/html.md#readme) | [htmlhint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/html_htmlhint.md#readme)| [HTML_HTMLHINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/html_htmlhint.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/json.ico" alt="" height="32px" class="megalinter-icon"></a> | [**JSON**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/json.md#readme) | [jsonlint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/json_jsonlint.md#readme)| [JSON_JSONLINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/json_jsonlint.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/latex.ico" alt="" height="32px" class="megalinter-icon"></a> | [**LATEX**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/latex.md#readme) | [chktex](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/latex_chktex.md#readme)| [LATEX_CHKTEX](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/latex_chktex.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/markdown.ico" alt="" height="32px" class="megalinter-icon"></a> | [**MARKDOWN**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/markdown.md#readme) | [markdownlint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/markdown_markdownlint.md#readme)| [MARKDOWN_MARKDOWNLINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/markdown_markdownlint.md#readme)| :heavy_check_mark: |
| <!-- --> |  | [markdown-link-check](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/markdown_markdown_link_check.md#readme)| [MARKDOWN_MARKDOWN_LINK_CHECK](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/markdown_markdown_link_check.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/protobuf.ico" alt="" height="32px" class="megalinter-icon"></a> | [**PROTOBUF**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/protobuf.md#readme) | [protolint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/protobuf_protolint.md#readme)| [PROTOBUF_PROTOLINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/protobuf_protolint.md#readme)| :heavy_check_mark: |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/rst.ico" alt="" height="32px" class="megalinter-icon"></a> | [**RST**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/rst.md#readme) | [rst-lint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/rst_rst_lint.md#readme)| [RST_RST_LINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/rst_rst_lint.md#readme)|  |
| <!-- --> |  | [rstcheck](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/rst_rstcheck.md#readme)| [RST_RSTCHECK](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/rst_rstcheck.md#readme)|  |
| <!-- --> |  | [rstfmt](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/rst_rstfmt.md#readme)| [RST_RSTFMT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/rst_rstfmt.md#readme)| :heavy_check_mark: |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/xml.ico" alt="" height="32px" class="megalinter-icon"></a> | [**XML**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/xml.md#readme) | [xmllint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/xml_xmllint.md#readme)| [XML_XMLLINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/xml_xmllint.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/yaml.ico" alt="" height="32px" class="megalinter-icon"></a> | [**YAML**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/yaml.md#readme) | [yamllint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/yaml_yamllint.md#readme)| [YAML_YAMLLINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/yaml_yamllint.md#readme)|  |

### Tooling formats

| <!-- --> | Language / Format | Linter | Configuration key | Fix |
| --- | ----------------- | -------------- | ------------ | ------- |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/ansible.ico" alt="" height="32px" class="megalinter-icon"></a> | [**ANSIBLE**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/ansible.md#readme) | [ansible-lint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/ansible_ansible_lint.md#readme)| [ANSIBLE_ANSIBLE_LINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/ansible_ansible_lint.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/arm.ico" alt="" height="32px" class="megalinter-icon"></a> | [**ARM**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/arm.md#readme) | [arm-ttk](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/arm_arm_ttk.md#readme)| [ARM_ARM_TTK](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/arm_arm_ttk.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/cloudformation.ico" alt="" height="32px" class="megalinter-icon"></a> | [**CLOUDFORMATION**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/cloudformation.md#readme) | [cfn-lint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/cloudformation_cfn_lint.md#readme)| [CLOUDFORMATION_CFN_LINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/cloudformation_cfn_lint.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/dockerfile.ico" alt="" height="32px" class="megalinter-icon"></a> | [**DOCKERFILE**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/dockerfile.md#readme) | [dockerfilelint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/dockerfile_dockerfilelint.md#readme)| [DOCKERFILE_DOCKERFILELINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/dockerfile_dockerfilelint.md#readme)|  |
| <!-- --> |  | [hadolint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/dockerfile_hadolint.md#readme)| [DOCKERFILE_HADOLINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/dockerfile_hadolint.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/editorconfig.ico" alt="" height="32px" class="megalinter-icon"></a> | [**EDITORCONFIG**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/editorconfig.md#readme) | [editorconfig-checker](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/editorconfig_editorconfig_checker.md#readme)| [EDITORCONFIG_EDITORCONFIG_CHECKER](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/editorconfig_editorconfig_checker.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/gherkin.ico" alt="" height="32px" class="megalinter-icon"></a> | [**GHERKIN**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/gherkin.md#readme) | [gherkin-lint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/gherkin_gherkin_lint.md#readme)| [GHERKIN_GHERKIN_LINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/gherkin_gherkin_lint.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/kubernetes.ico" alt="" height="32px" class="megalinter-icon"></a> | [**KUBERNETES**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/kubernetes.md#readme) | [kubeval](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/kubernetes_kubeval.md#readme)| [KUBERNETES_KUBEVAL](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/kubernetes_kubeval.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/openapi.ico" alt="" height="32px" class="megalinter-icon"></a> | [**OPENAPI**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/openapi.md#readme) | [spectral](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/openapi_spectral.md#readme)| [OPENAPI_SPECTRAL](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/openapi_spectral.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/puppet.ico" alt="" height="32px" class="megalinter-icon"></a> | [**PUPPET**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/puppet.md#readme) | [puppet-lint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/puppet_puppet_lint.md#readme)| [PUPPET_PUPPET_LINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/puppet_puppet_lint.md#readme)| :heavy_check_mark: |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/snakemake.ico" alt="" height="32px" class="megalinter-icon"></a> | [**SNAKEMAKE**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/snakemake.md#readme) | [snakemake](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/snakemake_snakemake.md#readme)| [SNAKEMAKE_LINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/snakemake_snakemake.md#readme)|  |
| <!-- --> |  | [snakefmt](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/snakemake_snakefmt.md#readme)| [SNAKEMAKE_SNAKEFMT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/snakemake_snakefmt.md#readme)| :heavy_check_mark: |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/tekton.ico" alt="" height="32px" class="megalinter-icon"></a> | [**TEKTON**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/tekton.md#readme) | [tekton-lint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/tekton_tekton_lint.md#readme)| [TEKTON_TEKTON_LINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/tekton_tekton_lint.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/terraform.ico" alt="" height="32px" class="megalinter-icon"></a> | [**TERRAFORM**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/terraform.md#readme) | [tflint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/terraform_tflint.md#readme)| [TERRAFORM_TFLINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/terraform_tflint.md#readme)|  |
| <!-- --> |  | [terrascan](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/terraform_terrascan.md#readme)| [TERRAFORM_TERRASCAN](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/terraform_terrascan.md#readme)|  |
| <!-- --> |  | [terragrunt](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/terraform_terragrunt.md#readme)| [TERRAFORM_TERRAGRUNT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/terraform_terragrunt.md#readme)|  |

### Other

| <!-- --> | Language / Format | Linter | Configuration key | Fix |
| --- | ----------------- | -------------- | ------------ | ------- |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/copypaste.ico" alt="" height="32px" class="megalinter-icon"></a> | [**COPYPASTE**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/copypaste.md#readme) | [jscpd](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/copypaste_jscpd.md#readme)| [COPYPASTE_JSCPD](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/copypaste_jscpd.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/spell.ico" alt="" height="32px" class="megalinter-icon"></a> | [**SPELL**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/spell.md#readme) | [cspell](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/spell_cspell.md#readme)| [SPELL_CSPELL](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/spell_cspell.md#readme)|  |

<!-- linters-table-end -->

<!-- linters-section-end -->
