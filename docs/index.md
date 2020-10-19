<!-- markdownlint-disable MD033 MD041 -->
# Mega-Linter

![GitHub release](https://img.shields.io/github/v/release/nvuillam/mega-linter?sort=semver)
[![Docker Pulls](https://img.shields.io/docker/pulls/nvuillam/mega-linter)](https://hub.docker.com/r/nvuillam/mega-linter)
[![Mega-Linter](https://github.com/nvuillam/mega-linter/workflows/Mega-Linter/badge.svg?branch=master)](https://github.com/marketplace/actions/mega-linter)
[![codecov](https://codecov.io/gh/nvuillam/mega-linter/branch/master/graph/badge.svg)](https://codecov.io/gh/nvuillam/mega-linter)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
<!-- [![Github All Releases](https://img.shields.io/github/downloads/nvuillam/mega-linter/total.svg)](https://github.com/users/nvuillam/packages/container/package/mega-linter) -->

Automatically detect all [languages](#languages) and [formats](#formats) in your repository and apply their related linters to ensure sources are clean !

**TLDR;**

- Save [mega-linter.yml](https://raw.githubusercontent.com/nvuillam/mega-linter/master/TEMPLATES/mega-linter.yml) in a folder `.github/workflows` of your repository
- Commit, push, and create a pull request
- Watch !

**The end goal of this tool:**

- Prevent broken code from being uploaded to the default branch (_Usually_ `master`)
- Help establish coding best practices across multiple languages
- Build guidelines for code layout and format
- Automate the process to help streamline code reviews

**Notes**:

- This repo is a hard-fork of GitHub Super-Linter, rewritten in python to add [additional features](#additional-features-compared-to-github-super-linter)
- If you are a Super-Linter user, you can transparently **switch to Mega-Linter and keep the same configuration** (just replace `github/super-linter@v3` by `nvuillam/mega-linter@v4` in your GT Action YML file, [like on this PR](https://github.com/nvuillam/npm-groovy-lint/pull/109))

## Table of Contents

- [Mega-Linter](#mega-linter)
  - [Supported Linters](#supported-linters)
    - [Languages](#languages)
    - [Formats](#formats)
    - [Tooling formats](#tooling-formats)
  - [How it Works](#how-it-works)
  - [Installation](#installation)
    - [Example connecting GitHub Action Workflow](#example-connecting-github-action-workflow)
    - [Add Mega-Linter badge in your repository README](#add-mega-linter-badge-in-your-repository-readme)
  - [Configuration](#configuration)
    - [Activation and deactivation](#activation-and-deactivation)
    - [Shared variables](#shared-variables)
    - [Linter specific variables](#linter-specific-variables)
    - [Filter linted files](#filter-linted-files)
    - [Template rules files](#template-rules-files)
  - [Filter linted files](#filter-linted-files)
  - [Docker Hub](#docker-hub)
  - [Run Mega-Linter outside GitHub Actions](#run-mega-linter-outside-github-actions)
    - [Local (troubleshooting/debugging/enhancements)](#local-troubleshootingdebuggingenhancements)
    - [Azure](#azure)
    - [GitLab](#gitlab)
    - [Visual Studio Code](#visual-studio-code)
  - [Limitations](#limitations)
  - [How to contribute](#how-to-contribute)
    - [License](#license)

## Supported Linters

Developers on **GitHub** can call the **GitHub Action** to lint their code base with the following list of linters:

<!-- linters-table-start -->
### Languages

| <!-- --> | Language / Format | Linter | Configuration key |
| --- | ----------------- | -------------- | ------------ |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/bash.ico" alt="" height="32px"></a> | **BASH** | [bash-exec](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/bash_bash_exec.md#readme)| [BASH_EXEC](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/bash_bash_exec.md#readme) |
| <!-- --> |  | [shellcheck](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/bash_shellcheck.md#readme)| [BASH_SHELLCHECK](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/bash_shellcheck.md#readme) |
| <!-- --> |  | [shfmt](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/bash_shfmt.md#readme)| [BASH_SHFMT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/bash_shfmt.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/c.ico" alt="" height="32px"></a> | **C** | [cpplint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/c_cpplint.md#readme)| [C_CPPLINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/c_cpplint.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/clojure.ico" alt="" height="32px"></a> | **CLOJURE** | [clj-kondo](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/clojure_clj_kondo.md#readme)| [CLOJURE](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/clojure_clj_kondo.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/coffee.ico" alt="" height="32px"></a> | **COFFEE** | [coffeelint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/coffee_coffeelint.md#readme)| [COFFEE](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/coffee_coffeelint.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/cpp.ico" alt="" height="32px"></a> | **C++** (CPP) | [cpplint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/cpp_cpplint.md#readme)| [CPP_CPPLINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/cpp_cpplint.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/csharp.ico" alt="" height="32px"></a> | **C#** (CSHARP) | [dotnet-format](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/csharp_dotnet_format.md#readme)| [CSHARP](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/csharp_dotnet_format.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/dart.ico" alt="" height="32px"></a> | **DART** | [dartanalyzer](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/dart_dartanalyzer.md#readme)| [DART](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/dart_dartanalyzer.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/go.ico" alt="" height="32px"></a> | **GO** | [golangci-lint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/go_golangci_lint.md#readme)| [GO](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/go_golangci_lint.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/groovy.ico" alt="" height="32px"></a> | **GROOVY** | [npm-groovy-lint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/groovy_npm_groovy_lint.md#readme)| [GROOVY](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/groovy_npm_groovy_lint.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/java.ico" alt="" height="32px"></a> | **JAVA** | [checkstyle](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/java_checkstyle.md#readme)| [JAVA](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/java_checkstyle.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/javascript.ico" alt="" height="32px"></a> | **JAVASCRIPT** | [eslint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/javascript_eslint.md#readme)| [JAVASCRIPT_ES](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/javascript_eslint.md#readme) |
| <!-- --> |  | [standard](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/javascript_standard.md#readme)| [JAVASCRIPT_STANDARD](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/javascript_standard.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/jsx.ico" alt="" height="32px"></a> | **JSX** | [eslint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/jsx_eslint.md#readme)| [JSX](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/jsx_eslint.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/kotlin.ico" alt="" height="32px"></a> | **KOTLIN** | [ktlint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/kotlin_ktlint.md#readme)| [KOTLIN](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/kotlin_ktlint.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/lua.ico" alt="" height="32px"></a> | **LUA** | [luacheck](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/lua_luacheck.md#readme)| [LUA](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/lua_luacheck.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/perl.ico" alt="" height="32px"></a> | **PERL** | [perlcritic](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/perl_perlcritic.md#readme)| [PERL](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/perl_perlcritic.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/php.ico" alt="" height="32px"></a> | **PHP** | [php](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/php_php.md#readme)| [PHP_BUILTIN](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/php_php.md#readme) |
| <!-- --> |  | [phpcs](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/php_phpcs.md#readme)| [PHP_PHPCS](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/php_phpcs.md#readme) |
| <!-- --> |  | [phpstan](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/php_phpstan.md#readme)| [PHP_PHPSTAN](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/php_phpstan.md#readme) |
| <!-- --> |  | [psalm](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/php_psalm.md#readme)| [PHP_PSALM](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/php_psalm.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/powershell.ico" alt="" height="32px"></a> | **POWERSHELL** | [powershell](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/powershell_powershell.md#readme)| [POWERSHELL](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/powershell_powershell.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/python.ico" alt="" height="32px"></a> | **PYTHON** | [pylint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/python_pylint.md#readme)| [PYTHON_PYLINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/python_pylint.md#readme) |
| <!-- --> |  | [black](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/python_black.md#readme)| [PYTHON_BLACK](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/python_black.md#readme) |
| <!-- --> |  | [flake8](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/python_flake8.md#readme)| [PYTHON_FLAKE8](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/python_flake8.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/r.ico" alt="" height="32px"></a> | **R** | [lintr](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/r_lintr.md#readme)| [R](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/r_lintr.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/raku.ico" alt="" height="32px"></a> | **RAKU** | [raku](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/raku_raku.md#readme)| [RAKU](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/raku_raku.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/ruby.ico" alt="" height="32px"></a> | **RUBY** | [rubocop](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/ruby_rubocop.md#readme)| [RUBY](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/ruby_rubocop.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/rust.ico" alt="" height="32px"></a> | **RUST** | [clippy](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/rust_clippy.md#readme)| [RUST](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/rust_clippy.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/scala.ico" alt="" height="32px"></a> | **SCALA** | [scalafix](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/scala_scalafix.md#readme)| [SCALA](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/scala_scalafix.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/sql.ico" alt="" height="32px"></a> | **SQL** | [sql-lint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/sql_sql_lint.md#readme)| [SQL](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/sql_sql_lint.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/tsx.ico" alt="" height="32px"></a> | **TSX** | [eslint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/tsx_eslint.md#readme)| [TSX](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/tsx_eslint.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/typescript.ico" alt="" height="32px"></a> | **TYPESCRIPT** | [eslint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/typescript_eslint.md#readme)| [TYPESCRIPT_ES](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/typescript_eslint.md#readme) |
| <!-- --> |  | [standard](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/typescript_standard.md#readme)| [TYPESCRIPT_STANDARD](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/typescript_standard.md#readme) |

### Formats

| <!-- --> | Language / Format | Linter | Configuration key |
| --- | ----------------- | -------------- | ------------ |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/css.ico" alt="" height="32px"></a> | **CSS** | [stylelint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/css_stylelint.md#readme)| [CSS_STYLELINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/css_stylelint.md#readme) |
| <!-- --> |  | [scss-lint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/css_scss_lint.md#readme)| [CSS_SCSS_LINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/css_scss_lint.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/env.ico" alt="" height="32px"></a> | **ENV** | [dotenv-linter](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/env_dotenv_linter.md#readme)| [ENV](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/env_dotenv_linter.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/html.ico" alt="" height="32px"></a> | **HTML** | [htmlhint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/html_htmlhint.md#readme)| [HTML](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/html_htmlhint.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/json.ico" alt="" height="32px"></a> | **JSON** | [jsonlint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/json_jsonlint.md#readme)| [JSON](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/json_jsonlint.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/latex.ico" alt="" height="32px"></a> | **LATEX** | [chktex](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/latex_chktex.md#readme)| [LATEX](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/latex_chktex.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/markdown.ico" alt="" height="32px"></a> | **MARKDOWN** | [markdownlint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/markdown_markdownlint.md#readme)| [MARKDOWN](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/markdown_markdownlint.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/protobuf.ico" alt="" height="32px"></a> | **PROTOBUF** | [protolint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/protobuf_protolint.md#readme)| [PROTOBUF](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/protobuf_protolint.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/xml.ico" alt="" height="32px"></a> | **XML** | [xmllint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/xml_xmllint.md#readme)| [XML](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/xml_xmllint.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/yaml.ico" alt="" height="32px"></a> | **YAML** | [yamllint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/yaml_yamllint.md#readme)| [YAML](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/yaml_yamllint.md#readme) |

### Tooling formats

| <!-- --> | Language / Format | Linter | Configuration key |
| --- | ----------------- | -------------- | ------------ |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/ansible.ico" alt="" height="32px"></a> | **ANSIBLE** | [ansible-lint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/ansible_ansible_lint.md#readme)| [ANSIBLE](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/ansible_ansible_lint.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/arm.ico" alt="" height="32px"></a> | **ARM** | [arm-ttk](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/arm_arm_ttk.md#readme)| [ARM](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/arm_arm_ttk.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/cloudformation.ico" alt="" height="32px"></a> | **CLOUDFORMATION** | [cfn-lint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/cloudformation_cfn_lint.md#readme)| [CLOUDFORMATION](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/cloudformation_cfn_lint.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/dockerfile.ico" alt="" height="32px"></a> | **DOCKERFILE** | [dockerfilelint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/dockerfile_dockerfilelint.md#readme)| [DOCKERFILE_DOCKERFILELINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/dockerfile_dockerfilelint.md#readme) |
| <!-- --> |  | [hadolint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/dockerfile_hadolint.md#readme)| [DOCKERFILE_HADOLINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/dockerfile_hadolint.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/editorconfig.ico" alt="" height="32px"></a> | **EDITORCONFIG** | [editorconfig-checker](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/editorconfig_editorconfig_checker.md#readme)| [EDITORCONFIG](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/editorconfig_editorconfig_checker.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/kubernetes.ico" alt="" height="32px"></a> | **KUBERNETES** | [kubeval](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/kubernetes_kubeval.md#readme)| [KUBERNETES_KUBEVAL](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/kubernetes_kubeval.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/openapi.ico" alt="" height="32px"></a> | **OPENAPI** | [spectral](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/openapi_spectral.md#readme)| [OPENAPI](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/openapi_spectral.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/puppet.ico" alt="" height="32px"></a> | **PUPPET** | [puppet-lint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/puppet_puppet_lint.md#readme)| [PUPPET](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/puppet_puppet_lint.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/snakemake.ico" alt="" height="32px"></a> | **SNAKEMAKE** | [snakemake](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/snakemake_snakemake.md#readme)| [SNAKEMAKE_LINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/snakemake_snakemake.md#readme) |
| <!-- --> |  | [snakefmt](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/snakemake_snakefmt.md#readme)| [SNAKEMAKE_SNAKEFMT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/snakemake_snakefmt.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/tekton.ico" alt="" height="32px"></a> | **TEKTON** | [tekton-lint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/tekton_tekton_lint.md#readme)| [TEKTON](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/tekton_tekton_lint.md#readme) |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/terraform.ico" alt="" height="32px"></a> | **TERRAFORM** | [tflint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/terraform_tflint.md#readme)| [TERRAFORM_TFLINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/terraform_tflint.md#readme) |
| <!-- --> |  | [terrascan](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/terraform_terrascan.md#readme)| [TERRAFORM_TERRASCAN](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/terraform_terrascan.md#readme) |
| <!-- --> |  | [terragrunt](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/terraform_terragrunt.md#readme)| [TERRAFORM](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/terraform_terragrunt.md#readme) |

<!-- linters-table-end -->

## How it Works

The mega-linter finds issues and reports them to the console output. Fixes are suggested in the console output but not automatically fixed, and a status check will show up as failed on the pull request.

The design of the **Mega-Linter** is currently to allow linting to occur in **GitHub Actions** as a part of continuous integration occurring on pull requests as the commits get pushed. It works best when commits are being pushed early and often to a branch with an open or draft pull request. There is some desire to move this closer to local development for faster feedback on linting errors but this is not yet supported.

## Installation

More in-depth [tutorial](https://www.youtube.com/watch?v=EDAmFKO4Zt0&t=118s) available

To use this **GitHub** Action you will need to complete the following:

1. Create a new file in your repository called `.github/workflows/mega-linter.yml`
2. Copy the example workflow from below into that new file, no extra configuration required
3. Commit that file to a new branch
4. Open up a pull request and observe the action working
5. Enjoy your more _stable_, and _cleaner_ code base

**NOTE:** If you pass the _Environment_ variable `GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}` in your workflow, then the **GitHub Mega-Linter** will mark the status of each individual linter run in the Checks section of a pull request. Without this you will only see the overall status of the full run. There is no need to set the **GitHub** Secret as it is automatically set by GitHub, it only needs to be passed to the action.

### Example connecting GitHub Action Workflow

In your repository you should have a `.github/workflows` folder with **GitHub** Action similar to below:

- `.github/workflows/mega-linter.yml`

This file should have the following code:

```yml
---
# Mega-Linter GitHub Action configuration file
# More info at https://github.com/nvuillam/mega-linter#readme
name: Mega-Linter

on:
  # Trigger mega-linter at every push. Action will also be visible from Pull Requests to master
  push: # Comment this line to trigger action only on pull-requests (not recommended if you don't pay for GH Actions)
  pull_request:
    branches: [master]

jobs:
  build:
    name: Mega-Linter
    runs-on: ubuntu-latest
    steps:
      # Git Checkout
      - name: Checkout Code
        uses: actions/checkout@v2
        with:
          fetch-depth: 0

      # Mega-Linter
      - name: Mega-Linter
        uses: nvuillam/mega-linter@v4
        env:
          # All available variables are described in documentation
          # https://github.com/nvuillam/mega-linter#configuration
          VALIDATE_ALL_CODEBASE: ${{ github.event_name == 'push' && github.ref == 'refs/heads/master' }} # Validates all source when push on master, else just the git diff with master. Override with true if you always want to lint all sources
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      # Upload Mega-Linter artifacts. They will be available on Github action page "Artifacts" section
      - name: Archive production artifacts
        if: ${{ success() }} || ${{ failure() }}
        uses: actions/upload-artifact@v2
        with:
          name: Mega-Linter reports
          path: |
            report
            mega-linter.log

```

### Add Mega-Linter badge in your repository README

You can show Mega-Linter status with a badge in your repository README

[![Mega-Linter](https://github.com/nvuillam/mega-linter/workflows/Mega-Linter/badge.svg?branch=master)](https://github.com/marketplace/actions/mega-linter)

Format:

```markdown
[![Mega-Linter](https://github.com/<OWNER>/<REPOSITORY>/workflows/Mega-Linter/badge.svg?branch=master)](https://github.com/marketplace/actions/mega-linter)
```

Example:

```markdown
[![Mega-Linter](https://github.com/nvuillam/npm-groovy-lint/workflows/Mega-Linter/badge.svg?branch=master)](https://github.com/marketplace/actions/mega-linter)
```

_Note:_ IF you did not use `Mega-Linter` as GitHub Action name, please read [GitHub Actions Badges documentation](https://docs.github.com/en/actions/configuring-and-managing-workflows/configuring-a-workflow#adding-a-workflow-status-badge-to-your-repository)

## Configuration

### Activation and deactivation

The Mega-Linter allows you to pass the following `ENV` variables to be able to trigger different functionality.

_Note:_ All the `ENABLE`, `ENABLE_LINTERS`, `DISABLE`, `DISABLE_LINTERS` variables behave in a very specific way:

- If `ENABLE` is not set, all descriptors are activated by default. If set, all linters of listed descriptors will be activated by default
- If `ENABLE_LINTERS` is set, only listed linters will be processed
- If `DISABLE` is set, the linters in the listed descriptors will be skipped
- If `DISABLE_LINTERS` is set, the listed linters will be skipped

This means that if you run the linter "out of the box", all linters will be checked.
But if you wish to select or exclude specific linters, we give you full control to choose which linters are run, and won't run anything unexpected.

Examples:

- Run all javascript and groovy linters except STANDARD javascript linter

```config
ENABLE = JAVASCRIPT,GROOVY
DISABLE_LINTERS = JAVSCRIPT_STANDARD
```

- Run all linters except PHP linters (PHP_BUILTIN, PHP_PCPCS, PHP_STAN, PHP_PSALM)

```config
DISABLE = PHP
```

- Run all linters except PHP_STAN and PHP_PSALM linters

```config
DISABLE_LINTERS = PHP_STAN,PHP_PSALM
```

### Shared variables

| **ENV VAR**                       | **Default Value**     | **Notes**                                                                                                                                                                        |
| --------------------------------- | --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **DEFAULT_BRANCH**                | `master`              | The name of the repository default branch.                                                                                                                                       |
| **DEFAULT_WORKSPACE**             | `/tmp/lint`           | The location containing files to lint if you are running locally.                                                                                                                |
| **DISABLE_ERRORS**                | `false`               | Flag to have the linter complete with exit code 0 even if errors were detected.                                                                                                  |
| **FILTER_REGEX_EXCLUDE**          | `none`                | Regular expression defining which files will be excluded from linting  (ex: `.*src/test.*`)                                                                                      |
| **FILTER_REGEX_INCLUDE**          | `all`                 | Regular expression defining which files will be processed by linters (ex: `.*src/.*`)                                                                                            |
| **LINTER_RULES_PATH**             | `.github/linters`     | Directory for all linter configuration rules.                                                                                                                                    |
| **LOG_FILE**                      | `mega-linter.log`    | The file name for outputting logs. All output is sent to the log file regardless of `LOG_LEVEL`.                                                                                 |
| **LOG_LEVEL**                     | `VERBOSE`             | How much output the script will generate to the console. One of `VERBOSE`, `DEBUG` or `TRACE`.                                                                                   |
| **MULTI_STATUS**                  | `true`                | A status API is made for each language that is linted to make visual parsing easier.                                                                                             |
| **OUTPUT_FORMAT**                 | `none`                | The report format to be generated, besides the stdout one. Output format of tap is currently using v13 of the specification. Supported formats: tap                              |
| **OUTPUT_FOLDER**                 | `mega-linter.report` | The location where the output reporting will be generated to. Output folder must not previously exist.                                                                           |
| **OUTPUT_DETAILS**                | `simpler`             | What level of details to be reported. Supported formats: simpler or detailed.                                                                                                    |
| **VALIDATE_ALL_CODEBASE**         | `true`                | Will parse the entire repository and find all files to validate across all types. **NOTE:** When set to `false`, only **new** or **edited** files will be parsed for validation. |

### Filter linted files

If you need to lint only a folder or exclude some files from linting, you can use optional environment parameters `FILTER_REGEX_INCLUDE` and `FILTER_REGEX_EXCLUDE`

Examples:

- Lint only src folder: `FILTER_REGEX_INCLUDE: .*src/.*`
- Do not lint files inside test folder: `FILTER_REGEX_EXCLUDE: .*test/.*`
- Do not lint javascript files inside test folder: `FILTER_REGEX_EXCLUDE: .*test/.*.js`

### Linter specific variables

See linters specific variables in their [Mega-Linter documentation](#languages)

### Template rules files

You can use the **Mega-Linter** _with_ or _without_ your own personal rules sets. This allows for greater flexibility for each individual code base. The Template rules all try to follow the standards we believe should be enabled at the basic level.

- Copy **any** or **all** template rules files from `TEMPLATES/` into your repository in the location: `.github/linters/` of your repository
  - If your repository does not have rules files, they will fall back to defaults in [this repository's `TEMPLATE` folder](https://github.com/github/mega-linter/tree/master/TEMPLATES)

## Docker Hub

The **Docker** container that is built from this repository is located at [nvuillam/mega-linter](https://hub.docker.com/r/nvuillam/mega-linter)

## Run Mega-Linter outside GitHub Actions

### Local (troubleshooting/debugging/enhancements)

If you find that you need to run mega-linter locally, you can follow the documentation at [Running mega-linter locally](https://github.com/nvuillam/mega-linter/blob/master/docs/run-linter-locally.md)

Check out the [note](#how-it-works) in **How it Works** to understand more about the **Mega-Linter** linting locally versus via continuous integration.

### Azure

Check out this [article](https://blog.tyang.org/2020/06/27/use-github-super-linter-in-azure-pipelines/)
Follow the same instructions, just replace super-linter by mega-linter

### GitLab

Check out this [snippet](https://gitlab.com/snippets/1988376)

### Visual Studio Code

You can checkout this repository using [Container Remote Development](https://code.visualstudio.com/docs/remote/containers), and debug the linter using the `Test Linter` task.
![Example](https://user-images.githubusercontent.com/15258962/85165778-2d2ce700-b21b-11ea-803e-3f6709d8e609.gif)

We will also support [GitHub Codespaces](https://github.com/features/codespaces/) once it becomes available

## Limitations

Below are a list of the known limitations for the **Mega-Linter**:

- Due to being completely packaged at run time, you will not be able to update dependencies or change versions of the enclosed linters and binaries
- Additional details from `package.json` are not read by the **Mega-Linter**
- Downloading additional codebases as dependencies from private repositories will fail due to lack of permissions

## How to contribute

If you would like to help contribute to this **GitHub** Action, please see [CONTRIBUTING](https://github.com/github/mega-linter/blob/master/.github/CONTRIBUTING.md)

---

### License

- [MIT License](https://github.com/github/mega-linter/blob/master/LICENSE)

## Additional features compared to github super-linter

### More languages and formats linted

- **C**
- **C++**
- **Puppet**
- **Rust**
- **Scala**

### New features & improvements

- **Enhanced performances**
  - **Optimized file listing management**: Collect all linters, then collect all files matching extensions associated with linters, then for each linter set the list of files after applying additional filters (include regex, exclude regex, linter custom filters)
  - Have a centralized exclude list (node_modules,.rbenv, etc...) to **ignore all unwanted folders from the beginning**

- **Enhanced Configuration**
  - Configure **include and exclude regexes** for a **single language or linter**: ex: JAVASCRIPT_FILTER_REGEX_INCLUDE
  - Configure **non blocking errors** for a **single language or linter**: ex: JAVASCRIPT_DISABLE_ERRORS
  - **Simplify languages and linters variables**
    - ENABLE = list of languages and formats to apply lint on codebase (default: all)
    - ENABLE_LINTERS = list of linters to apply lint on codebase (default: all)
    - DISABLE = list of languages and formats to skip (default: none)
    - DISABLE_LINTERS = list of linters to skip (default: none)
    - Variables VALIDATE_XXX are still taken in account (but should not be used in association with ENABLE and DISABLE variables)

- **Enhanced Documentation**
  - **One page per linter documentation** :
    - **All variables** that can be used with this linter
    - List of **file extensions, names and filters** applied by the linter
    - Link to **Mega-Linter default linter configuration**
    - Link to linter Web-Site
    - Link to official page explaining **how to customize the linter rules**
    - Link to official page explaining **how to disable rules from source comments**
    - **Examples** of linter command line calls behind the hood
    - Installation commands
  - README
    - Separate languages, formats and tooling formats in the linters table
    - Add logos for each descriptor

- **Enhanced logging and reports**
  - Show linter version and applied filters for each linter processed
  - Reports stored as artefacts on GitHub Action run
    - General log
    - One report file by linter

### Simplify architecture and evolutive maintenance

- Refactoring runtime in Python, for easier handling than bash thanks to [classes](https://github.com/nvuillam/mega-linter/tree/master/megalinter) and python modules
- Everything related to each linter [in a single descriptor YML file](https://github.com/nvuillam/mega-linter/tree/master/megalinter/descriptors)
  - easier evolutive maintenance
  - less conflicts to manage between PRs.
  - Few special cases require a [python linter class](https://github.com/nvuillam/mega-linter/tree/master/megalinter/descriptors))
- [Default behaviours for all linters](https://github.com/nvuillam/mega-linter/blob/master/megalinter/LinterTemplate.py), with possibility to override part of them for special cases
- Hierarchical architecture: Apply fixes and new behaviours to all linters with a single code update
- **Documentation as code**
  - Generate linters tables (ordered by type: language, format & tooling format) and include it in README. [(see result)](https://github.com/nvuillam/mega-linter/blob/master/README.md#supported-linters)
  - Generate one markdown file per Linter, containing all configuration variables, infos and examples [(See result)](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors)
- **Automatic generation of Dockerfile** using YML descriptors, always using the linter latest version
  - Dockerfile commands (FROM, ARG, ENV, COPY, RUN )
  - APK packages (linux)
  - NPM packages (node)
  - PIP packages (python)
  - GEM packages (ruby)
  - Phive packages (PHP)
- Have a centralized exclude list (node_modules,.rbenv, etc...)

### Improve robustness & stability

- [Test classes](https://github.com/nvuillam/mega-linter/blob/master/megalinter/tests/test_megalinter/MegaLinter_test.py) for each capability
- [Test classes for each linter](https://github.com/nvuillam/mega-linter/tree/master/megalinter/tests/test_megalinter/linters): Automatic generation of test classes using [.automation/build.py](https://github.com/nvuillam/mega-linter/blob/master/.automation/build.py)
- Setup **code coverage** [![codecov](https://codecov.io/gh/nvuillam/mega-linter/branch/master/graph/badge.svg)](https://codecov.io/gh/nvuillam/mega-linter)
- **Development CD / CI**
  - Validate multi-status on PR inside each PR (posted from step "Run against all code base")
  - Run test classes and code coverage with pytest during validation GitHub Action
  - Validate descriptor YML files with json schema during build
