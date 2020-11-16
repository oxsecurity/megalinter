<!-- markdownlint-disable MD013 MD033 MD041 -->

<div align="center">
  <a href="https://nvuillam.github.io/mega-linter" target="blank" title="Visit Mega-Linter Web Site">
    <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/images/mega-linter-square-small.png" alt="Mega-Linter" height="100px">
  </a>
</div>

![GitHub release](https://img.shields.io/github/v/release/nvuillam/mega-linter?sort=semver)
[![Docker Pulls](https://img.shields.io/docker/pulls/nvuillam/mega-linter)](https://hub.docker.com/r/nvuillam/mega-linter)
[![Mega-Linter](https://github.com/nvuillam/mega-linter/workflows/Mega-Linter/badge.svg?branch=master)](https://nvuillam.github.io/mega-linter)
[![codecov](https://codecov.io/gh/nvuillam/mega-linter/branch/master/graph/badge.svg)](https://codecov.io/gh/nvuillam/mega-linter)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
<!-- [![Github All Releases](https://img.shields.io/github/downloads/nvuillam/mega-linter/total.svg)](https://github.com/users/nvuillam/packages/container/package/mega-linter) -->

<!-- welcome-phrase-start -->
**Mega-Linter** analyzes [**37 languages**](#languages), [**12 formats**](#formats), [**15 tooling formats**](#tooling-formats) , [**copy-pastes**](#other) and [**spell**](#other) in your repository sources, generate **reports in several formats**, and can even [**apply auto-fixes**](#apply-fixes) with **auto-generated commit or PR**, to ensure all your projects are clean, whatever IDE/toolbox are used by their developers !
<!-- welcome-phrase-end -->

![Screenshot](https://github.com/nvuillam/mega-linter/blob/master/docs/assets/images/GitHubCommentReporter.jpg?raw=true>)

<!-- table-of-contents-start -->
## Table of Contents

- [Mega-Linter](#mega-linter)
  - [Quick start](#quick-start)
  - [Demo](#demo)
  - [Supported Linters](#supported-linters)
    - [Languages](#languages)
    - [Formats](#formats)
    - [Tooling formats](#tooling-formats)
    - [Other](#other)
  - [Installation](#installation)
    - [GitHub Action](#github-action)
    - [Azure](#azure)
    - [GitLab](#gitlab)
    - [Visual Studio Code](#visual-studio-code)
    - [Local](#local)
    - [Add Mega-Linter badge in your repository README](#add-mega-linter-badge-in-your-repository-readme)
  - [Configuration](#configuration)
    - [Activation and deactivation](#activation-and-deactivation)
    - [Apply fixes](#apply-fixes)
    - [Shared variables](#shared-variables)
    - [Linter specific variables](#linter-specific-variables)
    - [Filter linted files](#filter-linted-files)
    - [Template rules files](#template-rules-files)
  - [Reporters](#reporters)
  - [Docker Hub](#docker-hub)
  - [Limitations](#limitations)
  - [How to contribute](#how-to-contribute)
  - [License](#license)
  - [Mega-Linter vs Super-Linter](#mega-linter-vs-super-linter)
<!-- table-of-contents-end -->

## Quick Start

- Save [mega-linter.yml](https://raw.githubusercontent.com/nvuillam/mega-linter/master/TEMPLATES/mega-linter.yml) in a folder `.github/workflows` of your repository
- If you want to **apply formatters and auto-fixers** in a new commit/PR, uncomment [**APPLY_FIXES** variables](#apply-fixes)
- If you do not want to check copy-pastes and spell, uncomment `# DISABLE: COPYPASTE,SPELL` in `mega-linter.yml`
- Commit, push, and create a pull request
- Watch !

**Notes**:

- This repo is a hard-fork of GitHub Super-Linter, rewritten in python to add [lots of additional features](#mega-linter-vs-super-linter)
- If you are a Super-Linter user, you can transparently **switch to Mega-Linter and keep the same configuration** (just replace `github/super-linter@v3` by `nvuillam/mega-linter@v4` in your GT Action YML file, [like on this PR](https://github.com/nvuillam/npm-groovy-lint/pull/109))
- If you want to use some advanced additional features like **applying fixes during CI**, please take 5 minutes to define [mega-linter.yml](https://raw.githubusercontent.com/nvuillam/mega-linter/master/TEMPLATES/mega-linter.yml) :)

## Demo

![Demo Gif](https://github.com/nvuillam/mega-linter/blob/master/docs/assets/images/demo_with_comments.gif?raw=true)

## Supported Linters

Developers on **GitHub** can call the **GitHub Action** to lint their code base with the following list of linters:

<!-- linters-table-start -->
### Languages

| <!-- --> | Language / Format | Linter | Configuration key | Fix |
| --- | ----------------- | -------------- | ------------ | ------- |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/bash.ico" alt="" height="32px" class="megalinter-icon"></a> | [**BASH**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/bash.md#readme) | [bash-exec](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/bash_bash_exec.md#readme)| [BASH_EXEC](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/bash_bash_exec.md#readme)|  |
| <!-- --> |  | [shellcheck](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/bash_shellcheck.md#readme)| [BASH_SHELLCHECK](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/bash_shellcheck.md#readme)|  |
| <!-- --> |  | [shfmt](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/bash_shfmt.md#readme)| [BASH_SHFMT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/bash_shfmt.md#readme)|  |
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
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/kubernetes.ico" alt="" height="32px" class="megalinter-icon"></a> | [**KUBERNETES**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/kubernetes.md#readme) | [kubeval](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/kubernetes_kubeval.md#readme)| [KUBERNETES_KUBEVAL](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/kubernetes_kubeval.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/openapi.ico" alt="" height="32px" class="megalinter-icon"></a> | [**OPENAPI**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/openapi.md#readme) | [spectral](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/openapi_spectral.md#readme)| [OPENAPI_SPECTRAL](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/openapi_spectral.md#readme)|  |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/puppet.ico" alt="" height="32px" class="megalinter-icon"></a> | [**PUPPET**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/puppet.md#readme) | [puppet-lint](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/puppet_puppet_lint.md#readme)| [PUPPET_PUPPET_LINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/puppet_puppet_lint.md#readme)| :heavy_check_mark: |
| <img src="https://github.com/nvuillam/mega-linter/raw/master/docs/assets/icons/snakemake.ico" alt="" height="32px" class="megalinter-icon"></a> | [**SNAKEMAKE**](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/snakemake.md#readme) | [snakemake](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/snakemake_snakemake.md#readme)| [SNAKEMAKE_LINT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/snakemake_snakemake.md#readme)|  |
| <!-- --> |  | [snakefmt](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/snakemake_snakefmt.md#readme)| [SNAKEMAKE_SNAKEFMT](https://github.com/nvuillam/mega-linter/tree/master/docs/descriptors/snakemake_snakefmt.md#readme)|  |
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

## Installation

### GitHub Action

1. Create a new file in your repository called `.github/workflows/mega-linter.yml`
2. Copy the [example workflow from below](https://raw.githubusercontent.com/nvuillam/mega-linter/master/TEMPLATES/mega-linter.yml) into that new file, no extra configuration required
3. Commit that file to a new branch
4. Open up a pull request and observe the action working
5. Enjoy your more _stable_, and _cleaner_ code base

**NOTES:**

- If you pass the _Environment_ variable `GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}` in your workflow, then the **GitHub Mega-Linter** will mark the status of each individual linter run in the Checks section of a pull request. Without this you will only see the overall status of the full run. There is no need to set the **GitHub** Secret as it is automatically set by GitHub, it only needs to be passed to the action.
- You can also use it [outside of GitHub Actions](#run-mega-linter-outside-github-actions) (CircleCI, Azure Pipelines, Jenkins, or even locally with a docker run)

In your repository you should have a `.github/workflows` folder with **GitHub** Action similar to below:

- `.github/workflows/mega-linter.yml`

This file should have the following code:

```yml
---
# Mega-Linter GitHub Action configuration file
# More info at https://nvuillam.github.io/mega-linter
name: Mega-Linter

on:
  # Trigger mega-linter at every push. Action will also be visible from Pull Requests to master
  push: # Comment this line to trigger action only on pull-requests (not recommended if you don't pay for GH Actions)
  pull_request:
    branches: [master]

# env: #Uncomment to activate variables below
  # Apply linter fixes configuration
  # APPLY_FIXES: all # Uncomment to apply fixes provided by linters. You can also specify the list of fixing linters
  # APPLY_FIXES_EVENT: pull_request # Decide which event triggers application of fixes in a commit or a PR (pull_request (default), push, all)
  # APPLY_FIXES_MODE: commit # If APPLY_FIXES is used, defines if the fixes are directly committed (commit) or posted in a PR (pull_request)

jobs:
  build:
    name: Mega-Linter
    runs-on: ubuntu-latest
    steps:
      # Git Checkout
      - name: Checkout Code
        uses: actions/checkout@v2
        with:
          token: ${{ secrets.PAT || secrets.GITHUB_TOKEN }}
          fetch-depth: 0

      # Mega-Linter
      - name: Mega-Linter
        uses: nvuillam/mega-linter@v4
        env:
          # All available variables are described in documentation
          # https://nvuillam.github.io/mega-linter/#configuration
          VALIDATE_ALL_CODEBASE: ${{ github.event_name == 'push' && github.ref == 'refs/heads/master' }} # Validates all source when push on master, else just the git diff with master. Override with true if you always want to lint all sources
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          # DISABLE: COPYPASTE,SPELL # Uncomment to disable copy-paste and spell checks
          # ADD YOUR CUSTOM ENV VARIABLES HERE

      # Upload Mega-Linter artifacts
      - name: Archive production artifacts
        if: ${{ success() }} || ${{ failure() }}
        uses: actions/upload-artifact@v2
        with:
          name: Mega-Linter reports
          path: |
            report
            mega-linter.log

      # This step will evaluate the repo status and report the change
      - name: Check if there are changes
        id: changes
        if: ${{ success() }} || ${{ failure() }}
        uses: UnicornGlobal/has-changes-action@v1.0.11

      # Create pull request if applicable
      - name: Create Pull Request with applied fixes
        id: cpr
        if: steps.changes.outputs.changed == 1 && (env.APPLY_FIXES_EVENT == 'all' || env.APPLY_FIXES_EVENT == github.event_name) && env.APPLY_FIXES_MODE == 'pull_request'
        uses: peter-evans/create-pull-request@v3
        with:
          token: ${{ secrets.PAT || secrets.GITHUB_TOKEN }}
          commit-message: "[Mega-Linter] Apply linters automatic fixes"
          title: "[Mega-Linter] Apply linters automatic fixes"
          labels: bot
      - name: Create PR output
        if: steps.changes.outputs.changed == 1 && (env.APPLY_FIXES_EVENT == 'all' || env.APPLY_FIXES_EVENT == github.event_name) && env.APPLY_FIXES_MODE == 'pull_request'
        run: |
          echo "Pull Request Number - ${{ steps.cpr.outputs.pull-request-number }}"
          echo "Pull Request URL - ${{ steps.cpr.outputs.pull-request-url }}"

      # Push new commit if applicable
      - name: Prepare commit
        if: steps.changes.outputs.changed == 1 && (env.APPLY_FIXES_EVENT == 'all' || env.APPLY_FIXES_EVENT == github.event_name) && env.APPLY_FIXES_MODE == 'commit' && github.ref != 'refs/heads/master'
        run: sudo chown -Rc $UID .git/
      - name: Commit and push applied linter fixes
        if: steps.changes.outputs.changed == 1 && (env.APPLY_FIXES_EVENT == 'all' || env.APPLY_FIXES_EVENT == github.event_name) && env.APPLY_FIXES_MODE == 'commit' && github.ref != 'refs/heads/master'
        uses: stefanzweifel/git-auto-commit-action@v4
        with:
          branch: ${{ github.event.pull_request.head.ref || github.head_ref || github.ref }}
          commit_message: "[Mega-Linter] Apply linters fixes"
```

### Azure

```yaml
  - job: megalinter
    displayName: Mega-Linter
    pool:
      vmImage: ubuntu-latest
    steps:
    - script: |
        docker pull nvuillam/mega-linter:latest
        docker run -v $(System.DefaultWorkingDirectory):/tmp/lint nvuillam/mega-linter
      displayName: 'Code Scan using  Mega-Linter'
```

### GitLab

```yaml
megalinter:
  stage: linting
  image: nvuillam/mega-linter:v4
  script: [ "true" ]
  variables:
    DEFAULT_WORKSPACE: $CI_BUILDS_DIR
    ANSIBLE_DIRECTORY: $CI_PROJECT_PATH
    LINTER_RULES_PATH: $CI_PROJECT_PATH/.github/linters
```

### Visual Studio Code

You can checkout this repository using [Container Remote Development](https://code.visualstudio.com/docs/remote/containers), and debug the linter using the `Test Linter` task.
![Example](https://user-images.githubusercontent.com/15258962/85165778-2d2ce700-b21b-11ea-803e-3f6709d8e609.gif)

We will also support [GitHub Codespaces](https://github.com/features/codespaces/) once it becomes available

### Local

If you find that you need to run mega-linter locally, you can follow the documentation at [Running mega-linter locally](https://github.com/nvuillam/mega-linter/blob/master/docs/run-linter-locally.md)

### Add Mega-Linter badge in your repository README

You can show Mega-Linter status with a badge in your repository README

[![Mega-Linter](https://github.com/nvuillam/mega-linter/workflows/Mega-Linter/badge.svg?branch=master)](https://nvuillam.github.io/mega-linter)

Format:

```markdown
[![Mega-Linter](https://github.com/<OWNER>/<REPOSITORY>/workflows/Mega-Linter/badge.svg?branch=master)](https://nvuillam.github.io/mega-linter)
```

Example:

```markdown
[![Mega-Linter](https://github.com/nvuillam/npm-groovy-lint/workflows/Mega-Linter/badge.svg?branch=master)](https://nvuillam.github.io/mega-linter)
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

### Apply fixes

Mega-linter is able to apply fixes provided by linters. To use this capability, you need 3 env variables defined at top level

- **APPLY_FIXES**: `all` to apply fixes of all linters, or a list of linter keys (ex: `JAVASCRIPT_ES`,`MARKDOWN_MARKDOWNLINT`)
- **APPLY_FIXES_EVENT**: `all`, `push`, `pull_request`
- **APPLY_FIXES_MODE**: `commit` to create a new commit and push it on the same branch, or `pull_request` to create a new PR targeting the branch.

If you use **apply fixes**, add the following lines in your `.gitignore file`

```shell
*.log
report/
```

You may see github permission errors, or workflows not run on the new commit. To solve these issues:

- [Create Personal Access Token](https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/creating-a-personal-access-token#creating-a-token), then copy the PAT value
- [Define secret variable](https://docs.github.com/en/free-pro-team@latest/actions/reference/encrypted-secrets#creating-encrypted-secrets-for-a-repository) named **PAT** on your repository, and paste the PAT value

### Shared variables

| **ENV VAR**                       | **Default Value**     | **Notes**                                                                                                                                                                        |
| --------------------------------- | --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **DEFAULT_BRANCH**                | `master`              | The name of the repository default branch.                                                                                                                                       |
| **DEFAULT_WORKSPACE**             | `/tmp/lint`           | The location containing files to lint if you are running locally.                                                                                                                |
| **DISABLE_ERRORS**                | `false`               | Flag to have the linter complete with exit code 0 even if errors were detected.                                                                                                  |
| **FILTER_REGEX_EXCLUDE**          | `none`                | Regular expression defining which files will be excluded from linting  (ex: `.*src/test.*`)                                                                                      |
| **FILTER_REGEX_INCLUDE**          | `all`                 | Regular expression defining which files will be processed by linters (ex: `.*src/.*`)                                                                                            |
| **LINTER_RULES_PATH**             | `.github/linters`     | Directory for all linter configuration rules.                                                                                                                                    |
| **LOG_FILE**                      | `mega-linter.log`     | The file name for outputting logs. All output is sent to the log file regardless of `LOG_LEVEL`.                                                                                 |
| **LOG_LEVEL**                     | `INFO`                | How much output the script will generate to the console. One of `INFO`, `DEBUG`, `WARNING` or `ERROR`.                                                                           |
| **MULTI_STATUS**                  | `true`                | A status API is made for each language that is linted to make visual parsing easier.                                                                                             |
| **OUTPUT_FORMAT**                 | `none`                | The report format to be generated, besides the stdout one. Output format of tap is currently using v13 of the specification. Supported formats: tap                              |
| **OUTPUT_FOLDER**                 | `mega-linter.report`  | The location where the output reporting will be generated to. Output folder must not previously exist.                                                                           |
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
  - If your repository does not have rules files, they will fall back to defaults in [this repository's `TEMPLATE` folder](https://github.com/nvuillam/mega-linter/tree/master/TEMPLATES)

## Reporters

Mega-Linter can generate various reports that you can activate / deactivate and customize

- [Text files](https://github.com/nvuillam/mega-linter/tree/master/docs/reporters/TextReporter.md)
- [Pull Request comments](https://github.com/nvuillam/mega-linter/tree/master/docs/reporters/GitHubCommentReporter.md)
- [GitHub Status](https://github.com/nvuillam/mega-linter/tree/master/docs/reporters/GitHubStatusReporter.md)
- [TAP files](https://github.com/nvuillam/mega-linter/tree/master/docs/reporters/TapReporter.md)
- [Console](https://github.com/nvuillam/mega-linter/tree/master/docs/reporters/ConsoleReporter.md)

## Docker Hub

The **Docker** container that is built from this repository is located at [nvuillam/mega-linter](https://hub.docker.com/r/nvuillam/mega-linter)

## Limitations

Below are a list of the known limitations for the **Mega-Linter**:

- Due to being completely packaged at run time, you will not be able to update dependencies or change versions of the enclosed linters and binaries
- Additional details from `package.json` are not read by the **Mega-Linter**
- Downloading additional codebases as dependencies from private repositories will fail due to lack of permissions

## How to contribute

If you would like to help contribute to this repository, please see [CONTRIBUTING](https://github.com/nvuillam/mega-linter/blob/master/.github/CONTRIBUTING.md)

---

## License

- [MIT License](https://github.com/nvuillam/mega-linter/blob/master/LICENSE)

## Mega-Linter vs Super-Linter

### More languages and formats linted

- **C**, **C++**, **Copy-Paste detection**, **GraphQL**, **Puppet**, **Rust**, **Scala**, **Spell checker**, **Visual Basic .NET**

### More reporters

- [Text files](https://github.com/nvuillam/mega-linter/tree/master/docs/reporters/TextReporter.md)
- [Pull Request comments](https://github.com/nvuillam/mega-linter/tree/master/docs/reporters/GitHubCommentReporter.md)

### Automatically apply fixes

Mega-Linter can [**automatically apply fixes performed by linters**](#apply-fixes), and **push them to the same branch**, or **create a Pull Request** that you can validate

This is pretty handy, especially for linter errors related to formatting (in that case, you don't have any manual update to perform)

### New features & improvements

- **Enhanced performances**
  - **Optimized file listing management**: Collect all linters, then collect all files matching extensions associated with linters, then for each linter set the list of files after applying additional filters (include regex, exclude regex, linter custom filters)
  - Have a centralized exclude list (node_modules,.rbenv, etc...) to **ignore all unwanted folders from the beginning**

- **Enhanced Configuration**
  - Configure **include and exclude regexes** for a **single language or linter**: ex: `JAVASCRIPT_FILTER_REGEX_INCLUDE (src)`
  - Configure **additional CLI arguments** for a linter: ex: `JAVASCRIPT_ES_ARGUMENTS "--debug --env-info"`
  - Configure **non blocking errors** for a **single language or linter**: ex: `JAVASCRIPT_DISABLE_ERRORS`
  - **Simplify languages and linters variables**
    - ENABLE = list of languages and formats to apply lint on codebase (default: all)
    - ENABLE_LINTERS = list of linters to apply lint on codebase (default: all)
    - DISABLE = list of languages and formats to skip (default: none)
    - DISABLE_LINTERS = list of linters to skip (default: none)
    - Variables VALIDATE_XXX are still taken in account (but should not be used in association with ENABLE and DISABLE variables)

- **Enhanced Documentation**
  - [**HTML documentation**](https://nvuillam.github.io/mega-linter/)
  - **One page per linter documentation** :
    - **All variables** that can be used with this linter
    - List of **file extensions, names and filters** applied by the linter
    - Link to **Mega-Linter default linter configuration**
    - Link to linter Web-Site
    - Link to official page explaining **how to customize the linter rules**
    - Link to official page explaining **how to disable rules from source comments**
    - **Examples** of linter command line calls behind the hood
    - **Help** command text
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
- [Default behaviours for all linters](https://github.com/nvuillam/mega-linter/blob/master/megalinter/Linter.py), with possibility to override part of them for special cases
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

- [Test classes](https://github.com/nvuillam/mega-linter/blob/master/megalinter/tests/test_megalinter) for each capability
- [Test classes for each linter](https://github.com/nvuillam/mega-linter/tree/master/megalinter/tests/test_megalinter/linters): Automatic generation of test classes using [.automation/build.py](https://github.com/nvuillam/mega-linter/blob/master/.automation/build.py)
- Setup **code coverage** [![codecov](https://codecov.io/gh/nvuillam/mega-linter/branch/master/graph/badge.svg)](https://codecov.io/gh/nvuillam/mega-linter)
- **Development CD / CI**
  - Validate multi-status on PR inside each PR (posted from step "Run against all code base")
  - Run test classes and code coverage with pytest during validation GitHub Action
  - Validate descriptor YML files with json schema during build
  - Automated job to upgrade linters to their latest stable version
