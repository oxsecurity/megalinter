<!-- markdownlint-disable MD013 MD033 MD041 -->

<!-- header-logo-start -->
<div align="center">
  <a href="https://megalinter.github.io" target="blank" title="Visit Mega-Linter Web Site">
    <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/images/mega-linter-logo.png" alt="Mega-Linter" height="200px">
  </a>
</div>
<!-- header-logo-end -->
<!-- mega-linter-title-start -->

## Mega-Linter 

<!-- mega-linter-title-end -->
**(V5 work in progress, please keep using [V4](https://github.com/nvuillam/mega-linter) for now)**
**To test V5 as alpha, you can use docker image megalinter/megalinter@alpha at your own risk :)**

![GitHub release](https://img.shields.io/github/v/release/megalinter/megalinter?sort=semver)
[![Docker Pulls](https://img.shields.io/badge/docker%20pulls-485.0-blue)](https://megalinter.github.io/flavors/)
[![Downloads/week](https://img.shields.io/npm/dw/mega-linter-runner.svg)](https://npmjs.org/package/mega-linter-runner)
[![GitHub stars](https://img.shields.io/github/stars/megalinter/megalinter?maxAge=2592000)](https://GitHub.com/megalinter/megalinter/stargazers/)
[![Mega-Linter](https://github.com/megalinter/megalinter/workflows/Mega-Linter/badge.svg?branch=main)](https://github.com/megalinter/megalinter/actions?query=workflow%3AMega-Linter+branch%3Amain)
[![codecov](https://codecov.io/gh/megalinter/megalinter/branch/main/graph/badge.svg)](https://codecov.io/gh/megalinter/megalinter)
[![Secured with Trivy](https://img.shields.io/badge/Trivy-secured-green?logo=docker)](https://github.com/aquasecurity/trivy)
[![GitHub contributors](https://img.shields.io/github/contributors/megalinter/megalinter.svg)](https://gitHub.com/megalinter/megalinter/graphs/contributors/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/nvuillam)](https://github.com/sponsors/nvuillam)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![Tweet](https://img.shields.io/twitter/url/http/shields.io.svg?style=social)](https://twitter.com/intent/tweet?text=Check+Mega-Linter+to+say+goodbye+to+dirty+code+in+your+projects+%3A%29+100%25+free+and+open+source+for+all+uses&url=https://megalinter.github.io/&via=NicolasVuillamy&hashtags=linters,code,quality,ci,python,java,golang,c,dotnet,kotlin,rust,scala,salesforce,terraform)

<!-- welcome-phrase-start -->
Mega-Linter is an **100% Open-Source tool for CI/CD workflows** that **analyzes consistency and quality** of [**48** languages](#languages), [**22** formats](#formats), [**19** tooling formats](#tooling-formats) , [**abusive copy-pastes**](#other) and [**spelling mistakes**](#other) in your repository sources, generates [**various reports**](#reporters), and can even [apply **formatting** and **auto-fixes**](#apply-fixes), to **ensure all your projects sources are clean**, whatever IDE/toolbox are used by their developers.

Ready to use [out of the box](#installation) as a **GitHub Action** or **any CI system**, [**highly configurable**](#configuration) and **free for all uses**

<!-- welcome-phrase-end -->

<!-- online-doc-start -->
See [**Online Documentation Web Site which has a much easier user navigation than this README**](https://megalinter.github.io/)
<!-- online-doc-end -->

![Screenshot](https://github.com/megalinter/megalinter/blob/main/docs/assets/images/ConsoleReporter.jpg?raw=true>)
![Screenshot](https://github.com/megalinter/megalinter/blob/main/docs/assets/images/GitHubCommentReporter.jpg?raw=true>)

<!-- table-of-contents-start -->
## Table of Contents

- [Mega-Linter](#mega-linter)
  - [Table of Contents](#table-of-contents)
  - [Why Mega-Linter](#why-mega-linter)
  - [Quick Start](#quick-start)
  - [Supported Linters](#supported-linters)
    - [Languages](#languages)
    - [Formats](#formats)
    - [Tooling formats](#tooling-formats)
    - [Other](#other)
  - [Installation](#installation)
    - [Assisted installation](#assisted-installation)
    - [Manual installation](#manual-installation)
    - [GitHub Action](#github-action)
    - [Azure](#azure)
    - [Jenkins](#jenkins)
    - [GitLab](#gitlab)
    - [Concourse](#concourse)
      - [Pipeline step](#pipeline-step)
      - [Use it as reusable task](#use-it-as-reusable-task)
    - [Run Mega-Linter locally](#run-mega-linter-locally)
  - [Configuration](#configuration)
    - [Common variables](#common-variables)
    - [Activation and deactivation](#activation-and-deactivation)
    - [Filter linted files](#filter-linted-files)
    - [Apply fixes](#apply-fixes)
    - [Linter specific variables](#linter-specific-variables)
    - [Pre-commands](#pre-commands)
    - [Post-commands](#post-commands)
  - [Reporters](#reporters)
  - [Flavors](#flavors)
  - [Badge](#badge)
    - [Markdown](#markdown)
    - [reStructuredText](#restructuredtext)
  - [Plugins](#plugins)
    - [Use plugins](#use-plugins)
      - [Example](#example)
    - [Create plugins](#create-plugins)
      - [Limitations](#limitations)
  - [Frequently Asked Questions](#frequently-asked-questions)
  - [How to contribute](#how-to-contribute)
  - [Special thanks](#special-thanks)
    - [Contributors](#contributors)
    - [Sites referring to Mega-Linter](#sites-referring-to-mega-linter)
      - [Global](#global)
      - [Articles](#articles)
      - [Linters](#linters)
    - [Open-source teams](#open-source-teams)
    - [Super-Linter team](#super-linter-team)
  - [License](#license)
  - [Mega-Linter vs Super-Linter](#mega-linter-vs-super-linter)
    - [Performances](#performances)
    - [More languages and formats linted](#more-languages-and-formats-linted)
    - [Automatically apply formatting and fixes](#automatically-apply-formatting-and-fixes)
    - [Run locally](#run-locally)
    - [Reports](#reports)
      - [Capabilities](#capabilities)
      - [Additional Reporters](#additional-reporters)
    - [Enhanced Configuration](#enhanced-configuration)
    - [Enhanced Documentation](#enhanced-documentation)
    - [Plugins management](#plugins-management)
    - [Simplify architecture and evolutive maintenance](#simplify-architecture-and-evolutive-maintenance)
    - [Improve robustness & stability](#improve-robustness--stability)
  - [v4 vs v5](#v4-vs-v5)
<!-- table-of-contents-end -->

## Why Mega-Linter

Projects need to contain clean code, in order to **avoid technical debt**, that makes **evolutive maintenance harder and time consuming**.

By using [**code formatters and code linters**](#supported-linters), you ensure that your code base is **easier to read** and **respects best practices**, from the kick-off to each step of the project lifecycle

Not all developers have the good habit to use linters in their IDEs, making code reviews harder and longer to process

By using **Mega-Linter**, you'll enjoy the following benefits for you and your team:

- At **each pull request** it will **automatically analyze all updated code in all languages**
- Reading error logs, **developers learn best practices** of the language they are using
- [**Mega-Linter documentation**](https://megalinter.github.io/) provides the **list of IDE plugins integrating each linter**, so developers know which linter and plugins to install
- Mega-Linter is **ready out of the box** after a [**quick setup**](#quick-start)
- **Formatting and fixes** can be automatically [**applied on the git branch**](#apply-fixes) or [**provided in reports**](https://github.com/megalinter/megalinter/tree/main/docs/reporters/UpdatedSourcesReporter.md)
- This tool is **100% open-source** and **free for all uses** (personal, professional, public and private repositories)
- Mega-Linter can run on [**any CI tool**](#installation) and be [**run locally**](https://megalinter.github.io/mega-linter-runner/): **no need to authorize an external application**, and **your code base never leaves your tooling ecosystem**

<!-- quick-start-section-start -->
## Quick Start

- Run `npx mega-linter-runner --install` to generate configuration files
- Commit, push, and create a pull request
- Watch !

![Runner Install](https://github.com/megalinter/megalinter/blob/main/docs/assets/images/mega-linter-runner-generator.jpg?raw=true)

**Notes**:

- This repo is a hard-fork of [GitHub Super-Linter](https://github.com/github/super-linter), rewritten in python to add [lots of additional features](#mega-linter-vs-super-linter)
- If you are a Super-Linter user, you can transparently **switch to Mega-Linter and keep the same configuration** (just replace `github/super-linter@v3` by `megalinter/megalinter@v4` in your GitHub Action YML file, [like on this PR](https://github.com/nvuillam/npm-groovy-lint/pull/109))
- If you want to use Mega-Linter extra features (recommended), please take 5 minutes to use [Mega-Linter assisted installation](#installation)
- For a hand-holdy example of getting started with mega-linter check out [this blog post](https://ayyjohn.com/posts/linting-a-jekyll-blog-with-mega-linter) by Alec Johnson
<!-- quick-start-section-end -->

<!-- supported-linters-section-start -->
## Supported Linters

All linters are integrated in the [Mega-Linter docker image](https://hub.docker.com/r/megalinter/megalinter), which is frequently upgraded with their latest versions

<!-- languages-section-start-->
<!-- linters-table-start -->
### Languages

|                                                                                <!-- -->                                                                                | Language                                                                                                                     | Linter                                                                                                                            | Configuration key                                                                                                                            |     Format/Fix     |
|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------:|------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|:------------------:|
|    <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/bash.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->    | [**BASH**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/bash.md#readme)                             | [bash-exec](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/bash_bash_exec.md#readme)                       | [BASH_EXEC](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/bash_bash_exec.md#readme)                                  |                    |
|                                                                     <!-- --> <!-- linter-icon -->                                                                      |                                                                                                                              | [shellcheck](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/bash_shellcheck.md#readme)                     | [BASH_SHELLCHECK](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/bash_shellcheck.md#readme)                           |                    |
|                                                                     <!-- --> <!-- linter-icon -->                                                                      |                                                                                                                              | [shfmt](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/bash_shfmt.md#readme)                               | [BASH_SHFMT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/bash_shfmt.md#readme)                                     | :heavy_check_mark: |
|     <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/c.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->      | [**C**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/c.md#readme)                                   | [cpplint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/c_cpplint.md#readme)                              | [C_CPPLINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/c_cpplint.md#readme)                                       |                    |
|  <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/clojure.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->   | [**CLOJURE**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/clojure.md#readme)                       | [clj-kondo](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/clojure_clj_kondo.md#readme)                    | [CLOJURE_CLJ_KONDO](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/clojure_clj_kondo.md#readme)                       |                    |
|   <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/coffee.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->   | [**COFFEE**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/coffee.md#readme)                         | [coffeelint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/coffee_coffeelint.md#readme)                   | [COFFEE_COFFEELINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/coffee_coffeelint.md#readme)                       |                    |
|    <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/cpp.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->     | [**C++** (CPP)](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/cpp.md#readme)                         | [cpplint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/cpp_cpplint.md#readme)                            | [CPP_CPPLINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/cpp_cpplint.md#readme)                                   |                    |
|   <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/csharp.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->   | [**C#** (CSHARP)](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/csharp.md#readme)                    | [dotnet-format](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/csharp_dotnet_format.md#readme)             | [CSHARP_DOTNET_FORMAT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/csharp_dotnet_format.md#readme)                 | :heavy_check_mark: |
|    <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/dart.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->    | [**DART**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/dart.md#readme)                             | [dartanalyzer](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/dart_dartanalyzer.md#readme)                 | [DART_DARTANALYZER](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/dart_dartanalyzer.md#readme)                       |                    |
|     <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/go.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->     | [**GO**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/go.md#readme)                                 | [golangci-lint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/go_golangci_lint.md#readme)                 | [GO_GOLANGCI_LINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/go_golangci_lint.md#readme)                         |                    |
|                                                                     <!-- --> <!-- linter-icon -->                                                                      |                                                                                                                              | [revive](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/go_revive.md#readme)                               | [GO_REVIVE](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/go_revive.md#readme)                                       |                    |
|   <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/groovy.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->   | [**GROOVY**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/groovy.md#readme)                         | [npm-groovy-lint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/groovy_npm_groovy_lint.md#readme)         | [GROOVY_NPM_GROOVY_LINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/groovy_npm_groovy_lint.md#readme)             | :heavy_check_mark: |
|    <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/java.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->    | [**JAVA**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/java.md#readme)                             | [checkstyle](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/java_checkstyle.md#readme)                     | [JAVA_CHECKSTYLE](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/java_checkstyle.md#readme)                           |                    |
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/javascript.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**JAVASCRIPT**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/javascript.md#readme)                 | [eslint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/javascript_eslint.md#readme)                       | [JAVASCRIPT_ES](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/javascript_eslint.md#readme)                           | :heavy_check_mark: |
|                                                                     <!-- --> <!-- linter-icon -->                                                                      |                                                                                                                              | [standard](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/javascript_standard.md#readme)                   | [JAVASCRIPT_STANDARD](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/javascript_standard.md#readme)                   | :heavy_check_mark: |
|                                                                     <!-- --> <!-- linter-icon -->                                                                      |                                                                                                                              | [prettier](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/javascript_prettier.md#readme)                   | [JAVASCRIPT_PRETTIER](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/javascript_prettier.md#readme)                   | :heavy_check_mark: |
|    <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/jsx.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->     | [**JSX**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/jsx.md#readme)                               | [eslint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/jsx_eslint.md#readme)                              | [JSX_ESLINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/jsx_eslint.md#readme)                                     | :heavy_check_mark: |
|   <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/kotlin.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->   | [**KOTLIN**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/kotlin.md#readme)                         | [ktlint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/kotlin_ktlint.md#readme)                           | [KOTLIN_KTLINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/kotlin_ktlint.md#readme)                               | :heavy_check_mark: |
|    <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/lua.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->     | [**LUA**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/lua.md#readme)                               | [luacheck](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/lua_luacheck.md#readme)                          | [LUA_LUACHECK](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/lua_luacheck.md#readme)                                 |                    |
|    <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/perl.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->    | [**PERL**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/perl.md#readme)                             | [perlcritic](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/perl_perlcritic.md#readme)                     | [PERL_PERLCRITIC](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/perl_perlcritic.md#readme)                           |                    |
|    <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/php.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->     | [**PHP**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/php.md#readme)                               | [php](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/php_php.md#readme)                                    | [PHP_BUILTIN](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/php_php.md#readme)                                       |                    |
|                                                                     <!-- --> <!-- linter-icon -->                                                                      |                                                                                                                              | [phpcs](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/php_phpcs.md#readme)                                | [PHP_PHPCS](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/php_phpcs.md#readme)                                       |                    |
|                                                                     <!-- --> <!-- linter-icon -->                                                                      |                                                                                                                              | [phpstan](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/php_phpstan.md#readme)                            | [PHP_PHPSTAN](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/php_phpstan.md#readme)                                   |                    |
|                                                                     <!-- --> <!-- linter-icon -->                                                                      |                                                                                                                              | [psalm](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/php_psalm.md#readme)                                | [PHP_PSALM](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/php_psalm.md#readme)                                       |                    |
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/powershell.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**POWERSHELL**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/powershell.md#readme)                 | [powershell](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/powershell_powershell.md#readme)               | [POWERSHELL_POWERSHELL](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/powershell_powershell.md#readme)               |                    |
|   <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/python.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->   | [**PYTHON**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/python.md#readme)                         | [pylint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/python_pylint.md#readme)                           | [PYTHON_PYLINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/python_pylint.md#readme)                               |                    |
|                                                                     <!-- --> <!-- linter-icon -->                                                                      |                                                                                                                              | [black](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/python_black.md#readme)                             | [PYTHON_BLACK](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/python_black.md#readme)                                 | :heavy_check_mark: |
|                                                                     <!-- --> <!-- linter-icon -->                                                                      |                                                                                                                              | [flake8](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/python_flake8.md#readme)                           | [PYTHON_FLAKE8](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/python_flake8.md#readme)                               |                    |
|                                                                     <!-- --> <!-- linter-icon -->                                                                      |                                                                                                                              | [isort](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/python_isort.md#readme)                             | [PYTHON_ISORT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/python_isort.md#readme)                                 | :heavy_check_mark: |
|                                                                     <!-- --> <!-- linter-icon -->                                                                      |                                                                                                                              | [bandit](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/python_bandit.md#readme)                           | [PYTHON_BANDIT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/python_bandit.md#readme)                               |                    |
|                                                                     <!-- --> <!-- linter-icon -->                                                                      |                                                                                                                              | [mypy](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/python_mypy.md#readme)                               | [PYTHON_MYPY](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/python_mypy.md#readme)                                   |                    |
|     <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/r.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->      | [**R**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/r.md#readme)                                   | [lintr](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/r_lintr.md#readme)                                  | [R_LINTR](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/r_lintr.md#readme)                                           |                    |
|    <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/raku.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->    | [**RAKU**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/raku.md#readme)                             | [raku](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/raku_raku.md#readme)                                 | [RAKU_RAKU](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/raku_raku.md#readme)                                       |                    |
|    <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/ruby.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->    | [**RUBY**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/ruby.md#readme)                             | [rubocop](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/ruby_rubocop.md#readme)                           | [RUBY_RUBOCOP](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/ruby_rubocop.md#readme)                                 | :heavy_check_mark: |
|    <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/rust.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->    | [**RUST**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/rust.md#readme)                             | [clippy](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/rust_clippy.md#readme)                             | [RUST_CLIPPY](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/rust_clippy.md#readme)                                   |                    |
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/salesforce.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**SALESFORCE**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/salesforce.md#readme)                 | [sfdx-scanner-apex](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/salesforce_sfdx_scanner_apex.md#readme) | [SALESFORCE_SFDX_SCANNER_APEX](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/salesforce_sfdx_scanner_apex.md#readme) |                    |
|                                                                     <!-- --> <!-- linter-icon -->                                                                      |                                                                                                                              | [sfdx-scanner-aura](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/salesforce_sfdx_scanner_aura.md#readme) | [SALESFORCE_SFDX_SCANNER_AURA](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/salesforce_sfdx_scanner_aura.md#readme) |                    |
|                                                                     <!-- --> <!-- linter-icon -->                                                                      |                                                                                                                              | [sfdx-scanner-lwc](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/salesforce_sfdx_scanner_lwc.md#readme)   | [SALESFORCE_SFDX_SCANNER_LWC](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/salesforce_sfdx_scanner_lwc.md#readme)   |                    |
|   <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/scala.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->    | [**SCALA**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/scala.md#readme)                           | [scalafix](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/scala_scalafix.md#readme)                        | [SCALA_SCALAFIX](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/scala_scalafix.md#readme)                             |                    |
|    <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/sql.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->     | [**SQL**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/sql.md#readme)                               | [sql-lint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/sql_sql_lint.md#readme)                          | [SQL_SQL_LINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/sql_sql_lint.md#readme)                                 |                    |
|                                                                     <!-- --> <!-- linter-icon -->                                                                      |                                                                                                                              | [sqlfluff](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/sql_sqlfluff.md#readme)                          | [SQL_SQLFLUFF](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/sql_sqlfluff.md#readme)                                 |                    |
|                                                                     <!-- --> <!-- linter-icon -->                                                                      |                                                                                                                              | [tsqllint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/sql_tsqllint.md#readme)                          | [SQL_TSQLLINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/sql_tsqllint.md#readme)                                 |                    |
|  <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/default.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->   | [**SWIFT**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/swift.md#readme)                           | [swiftlint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/swift_swiftlint.md#readme)                      | [SWIFT_SWIFTLINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/swift_swiftlint.md#readme)                           | :heavy_check_mark: |
|    <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/tsx.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->     | [**TSX**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/tsx.md#readme)                               | [eslint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/tsx_eslint.md#readme)                              | [TSX_ESLINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/tsx_eslint.md#readme)                                     | :heavy_check_mark: |
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/typescript.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**TYPESCRIPT**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/typescript.md#readme)                 | [eslint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/typescript_eslint.md#readme)                       | [TYPESCRIPT_ES](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/typescript_eslint.md#readme)                           | :heavy_check_mark: |
|                                                                     <!-- --> <!-- linter-icon -->                                                                      |                                                                                                                              | [standard](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/typescript_standard.md#readme)                   | [TYPESCRIPT_STANDARD](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/typescript_standard.md#readme)                   | :heavy_check_mark: |
|                                                                     <!-- --> <!-- linter-icon -->                                                                      |                                                                                                                              | [prettier](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/typescript_prettier.md#readme)                   | [TYPESCRIPT_PRETTIER](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/typescript_prettier.md#readme)                   | :heavy_check_mark: |
|  <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/vbdotnet.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->  | [**Visual Basic .NET** (VBDOTNET)](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/vbdotnet.md#readme) | [dotnet-format](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/vbdotnet_dotnet_format.md#readme)           | [VBDOTNET_DOTNET_FORMAT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/vbdotnet_dotnet_format.md#readme)             | :heavy_check_mark: |

### Formats

|                                                                               <!-- -->                                                                               | Format                                                                                                   | Linter                                                                                                                                        | Configuration key                                                                                                                                      |     Format/Fix     |
|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------:|----------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------:|
|   <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/css.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->    | [**CSS**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/css.md#readme)           | [stylelint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/css_stylelint.md#readme)                                    | [CSS_STYLELINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/css_stylelint.md#readme)                                         | :heavy_check_mark: |
|                                                                    <!-- --> <!-- linter-icon -->                                                                     |                                                                                                          | [scss-lint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/css_scss_lint.md#readme)                                    | [CSS_SCSS_LINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/css_scss_lint.md#readme)                                         |                    |
|   <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/env.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->    | [**ENV**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/env.md#readme)           | [dotenv-linter](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/env_dotenv_linter.md#readme)                            | [ENV_DOTENV_LINTER](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/env_dotenv_linter.md#readme)                                 | :heavy_check_mark: |
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/graphql.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->  | [**GRAPHQL**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/graphql.md#readme)   | [graphql-schema-linter](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/graphql_graphql_schema_linter.md#readme)        | [GRAPHQL_GRAPHQL_SCHEMA_LINTER](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/graphql_graphql_schema_linter.md#readme)         |                    |
|   <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/html.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->   | [**HTML**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/html.md#readme)         | [htmlhint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/html_htmlhint.md#readme)                                     | [HTML_HTMLHINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/html_htmlhint.md#readme)                                         |                    |
|   <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/json.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->   | [**JSON**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/json.md#readme)         | [jsonlint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/json_jsonlint.md#readme)                                     | [JSON_JSONLINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/json_jsonlint.md#readme)                                         |                    |
|                                                                    <!-- --> <!-- linter-icon -->                                                                     |                                                                                                          | [eslint-plugin-jsonc](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/json_eslint_plugin_jsonc.md#readme)               | [JSON_ESLINT_PLUGIN_JSONC](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/json_eslint_plugin_jsonc.md#readme)                   | :heavy_check_mark: |
|                                                                    <!-- --> <!-- linter-icon -->                                                                     |                                                                                                          | [v8r](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/json_v8r.md#readme)                                               | [JSON_V8R](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/json_v8r.md#readme)                                                   |                    |
|                                                                    <!-- --> <!-- linter-icon -->                                                                     |                                                                                                          | [prettier](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/json_prettier.md#readme)                                     | [JSON_PRETTIER](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/json_prettier.md#readme)                                         | :heavy_check_mark: |
|  <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/latex.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->   | [**LATEX**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/latex.md#readme)       | [chktex](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/latex_chktex.md#readme)                                        | [LATEX_CHKTEX](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/latex_chktex.md#readme)                                           |                    |
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/markdown.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**MARKDOWN**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/markdown.md#readme) | [markdownlint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/markdown_markdownlint.md#readme)                         | [MARKDOWN_MARKDOWNLINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/markdown_markdownlint.md#readme)                         | :heavy_check_mark: |
|                                                                    <!-- --> <!-- linter-icon -->                                                                     |                                                                                                          | [remark-lint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/markdown_remark_lint.md#readme)                           | [MARKDOWN_REMARK_LINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/markdown_remark_lint.md#readme)                           | :heavy_check_mark: |
|                                                                    <!-- --> <!-- linter-icon -->                                                                     |                                                                                                          | [markdown-link-check](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/markdown_markdown_link_check.md#readme)           | [MARKDOWN_MARKDOWN_LINK_CHECK](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/markdown_markdown_link_check.md#readme)           |                    |
|                                                                    <!-- --> <!-- linter-icon -->                                                                     |                                                                                                          | [markdown-table-formatter](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/markdown_markdown_table_formatter.md#readme) | [MARKDOWN_MARKDOWN_TABLE_FORMATTER](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/markdown_markdown_table_formatter.md#readme) | :heavy_check_mark: |
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/protobuf.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**PROTOBUF**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/protobuf.md#readme) | [protolint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/protobuf_protolint.md#readme)                               | [PROTOBUF_PROTOLINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/protobuf_protolint.md#readme)                               | :heavy_check_mark: |
|   <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/rst.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->    | [**RST**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/rst.md#readme)           | [rst-lint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/rst_rst_lint.md#readme)                                      | [RST_RST_LINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/rst_rst_lint.md#readme)                                           |                    |
|                                                                    <!-- --> <!-- linter-icon -->                                                                     |                                                                                                          | [rstcheck](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/rst_rstcheck.md#readme)                                      | [RST_RSTCHECK](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/rst_rstcheck.md#readme)                                           |                    |
|                                                                    <!-- --> <!-- linter-icon -->                                                                     |                                                                                                          | [rstfmt](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/rst_rstfmt.md#readme)                                          | [RST_RSTFMT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/rst_rstfmt.md#readme)                                               | :heavy_check_mark: |
|   <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/xml.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->    | [**XML**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/xml.md#readme)           | [xmllint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/xml_xmllint.md#readme)                                        | [XML_XMLLINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/xml_xmllint.md#readme)                                             |                    |
|   <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/yaml.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->   | [**YAML**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/yaml.md#readme)         | [prettier](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/yaml_prettier.md#readme)                                     | [YAML_PRETTIER](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/yaml_prettier.md#readme)                                         | :heavy_check_mark: |
|                                                                    <!-- --> <!-- linter-icon -->                                                                     |                                                                                                          | [yamllint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/yaml_yamllint.md#readme)                                     | [YAML_YAMLLINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/yaml_yamllint.md#readme)                                         |                    |
|                                                                    <!-- --> <!-- linter-icon -->                                                                     |                                                                                                          | [v8r](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/yaml_v8r.md#readme)                                               | [YAML_V8R](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/yaml_v8r.md#readme)                                                   |                    |

### Tooling formats

|                                                                                  <!-- -->                                                                                  | Tooling format                                                                                                       | Linter                                                                                                                                    | Configuration key                                                                                                                                      |     Format/Fix     |
|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|----------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------:|
|    <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/default.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->     | [**ACTION**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/action.md#readme)                 | [actionlint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/action_actionlint.md#readme)                           | [ACTION_ACTIONLINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/action_actionlint.md#readme)                                 |                    |
|    <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/ansible.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->     | [**ANSIBLE**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/ansible.md#readme)               | [ansible-lint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/ansible_ansible_lint.md#readme)                      | [ANSIBLE_ANSIBLE_LINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/ansible_ansible_lint.md#readme)                           |                    |
|      <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/arm.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->       | [**ARM**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/arm.md#readme)                       | [arm-ttk](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/arm_arm_ttk.md#readme)                                    | [ARM_ARM_TTK](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/arm_arm_ttk.md#readme)                                             |                    |
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/cloudformation.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**CLOUDFORMATION**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/cloudformation.md#readme) | [cfn-lint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/cloudformation_cfn_lint.md#readme)                       | [CLOUDFORMATION_CFN_LINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/cloudformation_cfn_lint.md#readme)                     |                    |
|   <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/dockerfile.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->   | [**DOCKERFILE**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/dockerfile.md#readme)         | [dockerfilelint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/dockerfile_dockerfilelint.md#readme)               | [DOCKERFILE_DOCKERFILELINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/dockerfile_dockerfilelint.md#readme)                 |                    |
|                                                                       <!-- --> <!-- linter-icon -->                                                                        |                                                                                                                      | [hadolint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/dockerfile_hadolint.md#readme)                           | [DOCKERFILE_HADOLINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/dockerfile_hadolint.md#readme)                             |                    |
|  <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/editorconfig.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->  | [**EDITORCONFIG**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/editorconfig.md#readme)     | [editorconfig-checker](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/editorconfig_editorconfig_checker.md#readme) | [EDITORCONFIG_EDITORCONFIG_CHECKER](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/editorconfig_editorconfig_checker.md#readme) |                    |
|    <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/gherkin.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->     | [**GHERKIN**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/gherkin.md#readme)               | [gherkin-lint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/gherkin_gherkin_lint.md#readme)                      | [GHERKIN_GHERKIN_LINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/gherkin_gherkin_lint.md#readme)                           |                    |
|   <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/kubernetes.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->   | [**KUBERNETES**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/kubernetes.md#readme)         | [kubeval](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/kubernetes_kubeval.md#readme)                             | [KUBERNETES_KUBEVAL](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/kubernetes_kubeval.md#readme)                               |                    |
|    <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/openapi.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->     | [**OPENAPI**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/openapi.md#readme)               | [spectral](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/openapi_spectral.md#readme)                              | [OPENAPI_SPECTRAL](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/openapi_spectral.md#readme)                                   |                    |
|     <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/puppet.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->     | [**PUPPET**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/puppet.md#readme)                 | [puppet-lint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/puppet_puppet_lint.md#readme)                         | [PUPPET_PUPPET_LINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/puppet_puppet_lint.md#readme)                               | :heavy_check_mark: |
|   <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/snakemake.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->    | [**SNAKEMAKE**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/snakemake.md#readme)           | [snakemake](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/snakemake_snakemake.md#readme)                          | [SNAKEMAKE_LINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/snakemake_snakemake.md#readme)                                  |                    |
|                                                                       <!-- --> <!-- linter-icon -->                                                                        |                                                                                                                      | [snakefmt](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/snakemake_snakefmt.md#readme)                            | [SNAKEMAKE_SNAKEFMT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/snakemake_snakefmt.md#readme)                               | :heavy_check_mark: |
|     <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/tekton.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->     | [**TEKTON**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/tekton.md#readme)                 | [tekton-lint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/tekton_tekton_lint.md#readme)                         | [TEKTON_TEKTON_LINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/tekton_tekton_lint.md#readme)                               |                    |
|   <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/terraform.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->    | [**TERRAFORM**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/terraform.md#readme)           | [tflint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/terraform_tflint.md#readme)                                | [TERRAFORM_TFLINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/terraform_tflint.md#readme)                                   |                    |
|                                                                       <!-- --> <!-- linter-icon -->                                                                        |                                                                                                                      | [terrascan](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/terraform_terrascan.md#readme)                          | [TERRAFORM_TERRASCAN](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/terraform_terrascan.md#readme)                             |                    |
|                                                                       <!-- --> <!-- linter-icon -->                                                                        |                                                                                                                      | [terragrunt](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/terraform_terragrunt.md#readme)                        | [TERRAFORM_TERRAGRUNT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/terraform_terragrunt.md#readme)                           | :heavy_check_mark: |
|                                                                       <!-- --> <!-- linter-icon -->                                                                        |                                                                                                                      | [terraform-fmt](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/terraform_terraform_fmt.md#readme)                  | [TERRAFORM_TERRAFORM_FMT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/terraform_terraform_fmt.md#readme)                     | :heavy_check_mark: |
|                                                                       <!-- --> <!-- linter-icon -->                                                                        |                                                                                                                      | [checkov](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/terraform_checkov.md#readme)                              | [TERRAFORM_CHECKOV](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/terraform_checkov.md#readme)                                 |                    |

### Other

|                                                                               <!-- -->                                                                                | Code quality checker                                                                                           | Linter                                                                                                               | Configuration key                                                                                                                |     Format/Fix     |
|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------:|----------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|:------------------:|
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/copypaste.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon --> | [**COPYPASTE**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/copypaste.md#readme)     | [jscpd](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/copypaste_jscpd.md#readme)             | [COPYPASTE_JSCPD](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/copypaste_jscpd.md#readme)               |                    |
|  <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/default.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->  | [**CREDENTIALS**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/credentials.md#readme) | [secretlint](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/credentials_secretlint.md#readme) | [CREDENTIALS_SECRETLINT](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/credentials_secretlint.md#readme) |                    |
|    <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/git.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->    | [**GIT**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/git.md#readme)                 | [git_diff](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/git_git_diff.md#readme)             | [GIT_GIT_DIFF](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/git_git_diff.md#readme)                     |                    |
|   <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/spell.ico" alt="" height="32px" class="megalinter-icon"></a> <!-- linter-icon -->   | [**SPELL**](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/spell.md#readme)             | [misspell](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/spell_misspell.md#readme)           | [SPELL_MISSPELL](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/spell_misspell.md#readme)                 | :heavy_check_mark: |
|                                                                     <!-- --> <!-- linter-icon -->                                                                     |                                                                                                                | [cspell](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/spell_cspell.md#readme)               | [SPELL_CSPELL](https://github.com/megalinter/megalinter/tree/main/docs/descriptors/spell_cspell.md#readme)                     |                    |

<!-- linters-table-end -->
<!-- supported-linters-section-end -->

<!-- installation-section-start -->
## Installation

### Assisted installation

Just run `npx mega-linter-runner --install` at the root of your repository and answer questions, it will generate ready to use configuration files for Mega-Linter :)

![Runner Install](https://github.com/megalinter/megalinter/blob/main/docs/assets/images/mega-linter-runner-generator.jpg?raw=true)

### Upgrade from Mega-Linter v4

- Run `npx mega-linter-runner --upgrade` to automatically upgrade your configuration to v5 :)

### Manual installation

The following instructions examples are using to latest Mega-Linter stable version (**V4** , always corresponding to the [latest release](https://github.com/megalinter/megalinter/releases))

- GitHub Action: megalinter/megalinter@v4
- Docker image: megalinter/megalinter:v4

You can also use **beta** version (corresponding to the content of main branch)

- GitHub Action: megalinter/megalinter@beta
- Docker image: megalinter/megalinter:beta

### GitHub Action

1. Create a new file in your repository called `.github/workflows/mega-linter.yml`
2. Copy the [example workflow from below](https://raw.githubusercontent.com/megalinter/megalinter/main/TEMPLATES/mega-linter.yml) into that new file, no extra configuration required
3. Commit that file to a new branch
4. Open up a pull request and observe the action working
5. Enjoy your more _stable_, and _cleaner_ code base

**NOTES:**

- If you pass the _Environment_ variable `GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}` in your workflow, then the **GitHub Mega-Linter** will mark the status of each individual linter run in the Checks section of a pull request. Without this you will only see the overall status of the full run. There is no need to set the **GitHub** Secret as it is automatically set by GitHub, it only needs to be passed to the action.
- You can also **use it outside of GitHub Actions** (CircleCI, Azure Pipelines, Jenkins, GitLab, or even locally with a docker run)

In your repository you should have a `.github/workflows` folder with **GitHub** Action similar to below:

- `.github/workflows/mega-linter.yml`

<details>
<summary>This file should have this code</summary>

```yml
---
# Mega-Linter GitHub Action configuration file
# More info at https://megalinter.github.io/
name: Mega-Linter

on:
  # Trigger mega-linter at every push. Action will also be visible from Pull Requests to main
  push: # Comment this line to trigger action only on pull-requests (not recommended if you don't pay for GH Actions)
  pull_request:
    branches: [main, main]

env: # Comment env block if you do not want to apply fixes
  # Apply linter fixes configuration
  APPLY_FIXES: all # When active, APPLY_FIXES must also be defined as environment variable (in github/workflows/mega-linter.yml or other CI tool)
  APPLY_FIXES_EVENT: pull_request # Decide which event triggers application of fixes in a commit or a PR (pull_request, push, all)
  APPLY_FIXES_MODE: commit # If APPLY_FIXES is used, defines if the fixes are directly committed (commit) or posted in a PR (pull_request)

jobs:
  # Cancel duplicate jobs: https://github.com/fkirc/skip-duplicate-actions#option-3-cancellation-only
  cancel_duplicates:
    name: Cancel duplicate jobs
    runs-on: ubuntu-latest
    steps:
      - uses: fkirc/skip-duplicate-actions@main
        with:
          github_token: ${{ secrets.PAT || secrets.GITHUB_TOKEN }}

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
        id: ml
        # You can override Mega-Linter flavor used to have faster performances
        # More info at https://megalinter.github.io/flavors/
        uses: megalinter/megalinter@v4
        env:
          # All available variables are described in documentation
          # https://megalinter.github.io/configuration/
          VALIDATE_ALL_CODEBASE: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }} # Validates all source when push on main, else just the git diff with main. Override with true if you always want to lint all sources
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          # ADD YOUR CUSTOM ENV VARIABLES HERE OR DEFINE THEM IN A FILE .mega-linter.yml AT THE ROOT OF YOUR REPOSITORY
          # DISABLE: COPYPASTE,SPELL # Uncomment to disable copy-paste and spell checks

      # Upload Mega-Linter artifacts
      - name: Archive production artifacts
        if: ${{ success() }} || ${{ failure() }}
        uses: actions/upload-artifact@v2
        with:
          name: Mega-Linter reports
          path: |
            report
            mega-linter.log

      # Create pull request if applicable (for now works only on PR from same repository, not from forks)
      - name: Create Pull Request with applied fixes
        id: cpr
        if: steps.ml.outputs.has_updated_sources == 1 && (env.APPLY_FIXES_EVENT == 'all' || env.APPLY_FIXES_EVENT == github.event_name) && env.APPLY_FIXES_MODE == 'pull_request' && (github.event_name == 'push' || github.event.pull_request.head.repo.full_name == github.repository) && !contains(github.event.head_commit.message, 'skip fix')
        uses: peter-evans/create-pull-request@v3
        with:
          token: ${{ secrets.PAT || secrets.GITHUB_TOKEN }}
          commit-message: "[Mega-Linter] Apply linters automatic fixes"
          title: "[Mega-Linter] Apply linters automatic fixes"
          labels: bot
      - name: Create PR output
        if: steps.ml.outputs.has_updated_sources == 1 && (env.APPLY_FIXES_EVENT == 'all' || env.APPLY_FIXES_EVENT == github.event_name) && env.APPLY_FIXES_MODE == 'pull_request' && (github.event_name == 'push' || github.event.pull_request.head.repo.full_name == github.repository) && !contains(github.event.head_commit.message, 'skip fix')
        run: |
          echo "Pull Request Number - ${{ steps.cpr.outputs.pull-request-number }}"
          echo "Pull Request URL - ${{ steps.cpr.outputs.pull-request-url }}"

      # Push new commit if applicable (for now works only on PR from same repository, not from forks)
      - name: Prepare commit
        if: steps.ml.outputs.has_updated_sources == 1 && (env.APPLY_FIXES_EVENT == 'all' || env.APPLY_FIXES_EVENT == github.event_name) && env.APPLY_FIXES_MODE == 'commit' && github.ref != 'refs/heads/main' && (github.event_name == 'push' || github.event.pull_request.head.repo.full_name == github.repository) && !contains(github.event.head_commit.message, 'skip fix')
        run: sudo chown -Rc $UID .git/
      - name: Commit and push applied linter fixes
        if: steps.ml.outputs.has_updated_sources == 1 && (env.APPLY_FIXES_EVENT == 'all' || env.APPLY_FIXES_EVENT == github.event_name) && env.APPLY_FIXES_MODE == 'commit' && github.ref != 'refs/heads/main' && (github.event_name == 'push' || github.event.pull_request.head.repo.full_name == github.repository) && !contains(github.event.head_commit.message, 'skip fix')
        uses: stefanzweifel/git-auto-commit-action@v4
        with:
          branch: ${{ github.event.pull_request.head.ref || github.head_ref || github.ref }}
          commit_message: "[Mega-Linter] Apply linters fixes"
```

</details>

### Azure

Use the following Azure workflow template

You may activate [File.io reporter](https://megalinter.github.io/reporters/FileIoReporter/) or [E-mail reporter](https://megalinter.github.io/reporters/EmailReporter/) to access detailed logs and fixed source

```yaml
  - job: megalinter
    displayName: Mega-Linter
    pool:
      vmImage: ubuntu-latest
    steps:
    - script: |
        docker pull megalinter/megalinter:v4
        docker run -v $(System.DefaultWorkingDirectory):/tmp/lint megalinter/megalinter
      displayName: 'Code Scan using Mega-Linter'
```

### Jenkins

Add the following stage in your Jenkinsfile

You may activate [File.io reporter](https://megalinter.github.io/reporters/FileIoReporter/) or [E-mail reporter](https://megalinter.github.io/reporters/EmailReporter/) to access detailed logs and fixed source

```groovy
// Lint with Mega-Linter: https://megalinter.github.io/
stage('Mega-Linter') {
    agent {
        docker {
            image 'megalinter/megalinter:v4'
            args "-e VALIDATE_ALL_CODEBASE=true -v ${WORKSPACE}:/tmp/lint --entrypoint=''"
            reuseNode true
        }
    }
    steps {
        sh '/entrypoint.sh'
    }
}
```

### GitLab

Create or update `.gitlab-ci.yml` file at the root of your repository

```yaml
# Mega-Linter GitLab CI job configuration file
# More info at https://megalinter.github.io/

mega-linter:
  stage: test
  # You can override Mega-Linter flavor used to have faster performances
  # More info at https://megalinter.github.io/flavors/
  image: megalinter/megalinter-python:v4
  script: [ "true" ]
  variables:
    # All available variables are described in documentation
    # https://megalinter.github.io/configuration/
    DEFAULT_WORKSPACE: $CI_PROJECT_DIR
    DEFAULT_BRANCH: main
    # ADD YOUR CUSTOM ENV VARIABLES HERE TO OVERRIDE VALUES OF .mega-linter.yml AT THE ROOT OF YOUR REPOSITORY
  artifacts:
    when: always
    paths:
      - report
    expire_in: 1 week
```

![Screenshot](https://github.com/megalinter/megalinter/blob/main/docs/assets/images/TextReporter_gitlab_1.jpg?raw=true>)

### Concourse

#### Pipeline step

Use the following `job.step` in your pipeline template

Note: make sure you have `job.plan.get` step which gets `repo` containing your repository as shown in example

```yaml
---

  - name: linting
    plan:
      - get: repo
      - task: linting
        config:
          platform: linux
          image_resource:
            type: docker-image
            source:
              repository: megalinter/megalinter
              tag: v4
          inputs:
            - name: repo
          run:
            path: bash
            args:
            - -cxe
            - |
              cd repo
              export DEFAULT_WORKSPACE=$(pwd)
              bash -ex /entrypoint.sh
              ## doing this because concourse does not work as other CI systems
          # params:
            # PARALLEL: true
            # DISABLE: SPELL
            # APPLY_FIXES: all
            # DISABLE_ERRORS: true
            # VALIDATE_ALL_CODEBASE: true
            # DEFAULT_BRANCH: main

```

OR

#### Use it as reusable task

Create reusable concourse task which can be used with multiple pipelines

1. Create task file `task-linting.yaml`

```yaml
---
platform: linux
image_resource:
  type: docker-image
  source:
    repository: megalinter/megalinter
    tag: v4

inputs:
- name: repo

## uncomment this if you want reports as task output
# output:
# - name: reports
#   path: repo/report

run:
  path: bash
  args:
  - -cxe
  - |
    cd repo
    export DEFAULT_WORKSPACE=$(pwd)
    bash -ex /entrypoint.sh
```

2. Use that `task-linting.yaml` task in pipeline

Note:

  1. make sure `task-linting.yaml` is available in that `repo` input at root

  2. task `output` is **not** shown here

```yaml
resources:

  - name: linting
    plan:
      - get: repo
      - task: linting
        file: repo/task-linting.yaml
        # params:
        #   PARALLEL: true
        #   DISABLE: SPELL
        #   APPLY_FIXES: all
        #   DISABLE_ERRORS: true
        #   VALIDATE_ALL_CODEBASE: true
        #   DEFAULT_BRANCH: main
```

### Run Mega-Linter locally

[![Version](https://img.shields.io/npm/v/mega-linter-runner.svg)](https://npmjs.org/package/mega-linter-runner)
[![Downloads/week](https://img.shields.io/npm/dw/mega-linter-runner.svg)](https://npmjs.org/package/mega-linter-runner)
[![Downloads/total](https://img.shields.io/npm/dt/mega-linter-runner.svg)](https://npmjs.org/package/mega-linter-runner)

You can use [mega-linter-runner](https://megalinter.github.io/mega-linter-runner/) to locally run Mega-Linter with the same configuration defined in [.mega-linter.yml](#configuration) file

See [mega-linter-runner installation instructions](https://megalinter.github.io/mega-linter-runner/#installation)

Example

```shell
npx mega-linter-runner --flavor salesforce -e 'ENABLE=,DOCKERFILE,MARKDOWN,YAML' -e 'SHOW_ELAPSED_TIME=true'
```

Note: You can also use such command line from your custom CI/CD pipelines

<!-- installation-section-end -->

<!-- configuration-section-start -->
## Configuration

Mega-Linter configuration variables can be defined in a **.mega-linter.yml** file at the root of the repository or with **environment variables**.
You can see an example config file in this repo: [**.mega-linter.yml**](https://github.com/megalinter/megalinter/blob/main/.mega-linter.yml)

Configuration is assisted with auto-completion and validation in most commonly used IDEs, thanks to [JSON schema](https://megalinter.github.io/json-schemas/configuration.html) stored on [schemastore.org](https://www.schemastore.org/)

- VsCode: You need a VsCode extension like [Red Hat YAML](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml)
- IDEA family: Auto-completion natively supported

![Assisted configuration](https://github.com/megalinter/megalinter/raw/main/docs/assets/images/assisted-configuration.jpg)

### Common variables

| **ENV VAR**                                         | **Default Value**            | **Notes**                                                                                                                                                                                                   |
|-----------------------------------------------------|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **ADDITIONAL_EXCLUDED_DIRECTORIES**                 | \[\]                         | List of additional excluded directory basenames. They are excluded at any nested level.                                                                                                                     |
| [**APPLY_FIXES**](#apply-fixes)                     | `none`                       | Activates formatting and auto-fixing [(more info)](#apply-fixes)                                                                                                                                            |
| **DEFAULT_BRANCH**                                  | `main`                     | The name of the repository default branch. Warning: In new github repositories, main branch is named `main`, so you need to override this value with `main`                                               |
| **DEFAULT_WORKSPACE**                               | `/tmp/lint`                  | The location containing files to lint if you are running locally.                                                                                                                                           |
| **DISABLE_ERRORS**                                  | `false`                      | Flag to have the linter complete with exit code 0 even if errors were detected.                                                                                                                             |
| [**DISABLE**](#activation-and-deactivation)         | <!-- -->                     | List of disabled descriptors keys [(more info)](#activation-and-deactivation)                                                                                                                               |
| [**DISABLE_LINTERS**](#activation-and-deactivation) | <!-- -->                     | List of disabled linters keys [(more info)](#activation-and-deactivation)                                                                                                                                   |
| [**ENABLE**](#activation-and-deactivation)          | <!-- -->                     | List of enabled descriptors keys [(more info)](#activation-and-deactivation)                                                                                                                                |
| [**ENABLE_LINTERS**](#activation-and-deactivation)  | <!-- -->                     | List of enabled linters keys [(more info)](#activation-and-deactivation)                                                                                                                                    |
| **EXCLUDED_DIRECTORIES**                            | \[...many values...\]        | List of excluded directory basenames. They are excluded at any nested level.                                                                                                                                |
| **EXTENDS**                                         | <!-- -->                     | Base `mega-linter.yml` config file(s) to extend local configuration from. Can be a single URL or a list of `.mega-linter.yml` config files URLs                                                             |
| **FAIL_IF_MISSING_LINTER_IN_FLAVOR**                | `false`                      | If set to `true`, Mega-Linter fails if a linter is missing in the selected flavor                                                                                                                           |
| [**FILTER_REGEX_EXCLUDE**](#filter-linted-files)    | `none`                       | Regular expression defining which files will be excluded from linting [(more info)](#filter-linted-files) .ex: `.*src/test.*`)                                                                              |
| [**FILTER_REGEX_INCLUDE**](#filter-linted-files)    | `all`                        | Regular expression defining which files will be processed by linters [(more info)](#filter-linted-files) .ex: `.*src/.*`)                                                                                   |
| **FLAVOR_SUGGESTIONS**                              | `true`                       | Provides suggestions about different Mega-Linter flavors to use to improve runtime performances                                                                                                             |
| **FORMATTERS_DISABLE_ERRORS**                       | `true`                       | Formatter errors will be reported as errors (and not warnings) if this variable is set to `false`                                                                                                           |
| **GITHUB_WORKSPACE**                                | ``                           | Base directory for `REPORT_OUTPUT_FOLDER`, for user-defined linter rules location, for location of linted files if `DEFAULT_WORKSPACE` is not set                                                           |
| **IGNORE_GENERATED_FILES**                          | `false`                      | If set to `true`, Mega-Linter will skip files containing `@generated` marker but without `@not-generated` marker (more info at [https://generated.at](https://generated.at/))                               |
| **IGNORE_GITIGNORED_FILES**                         | `true`                       | If set to `true`, Mega-Linter will skip files ignored by git using `.gitignore` file                                                                                                                        |
| **JAVASCRIPT_DEFAULT_STYLE**                        | `standard`                   | Javascript default style to check/apply. `standard`,`prettier`                                                                                                                                              |
| **LINTER_RULES_PATH**                               | `.github/linters`            | Directory for all linter configuration rules.<br/> Can be a local folder or a remote URL (ex: `https://raw.githubusercontent.com/some_org/some_repo/mega-linter-rules` )                                    |
| **LOG_FILE**                                        | `mega-linter.log`            | The file name for outputting logs. All output is sent to the log file regardless of `LOG_LEVEL`.                                                                                                            |
| **LOG_LEVEL**                                       | `INFO`                       | How much output the script will generate to the console. One of `INFO`, `DEBUG`, `WARNING` or `ERROR`.                                                                                                      |
| **MARKDOWN_DEFAULT_STYLE**                          | `markdownlint`               | Markdown default style to check/apply. `markdownlint`,`remark-lint`                                                                                                                                         |
| **MEGALINTER_CONFIG**                               | `.mega-linter.yml`           | Name of Mega-Linter configuration file. Can be defined remotely, in that case set this environment variable with the remote URL of `.mega-linter.yml` config file                                           |
| **PARALLEL**                                        | `true`                       | Process linters in parallel to improve overall Mega-Linter performance. If true, linters of same language or formats are grouped in the same parallel process to avoid lock issues if fixing the same files |
| [**PLUGINS**](#plugins)                             | \[\]                         | List of plugin urls to install and run during Mega-Linter run                                                                                                                                               |
| [**POST_COMMANDS**](#post-commands)                 | \[\]                         | Custom bash commands to run after linters                                                                                                                                                                   |
| [**PRE_COMMANDS**](#pre-commands)                   | \[\]                         | Custom bash commands to run before linters                                                                                                                                                                  |
| **PRINT_ALPACA**                                    | `true`                       | Enable printing alpaca image to console                                                                                                                                                                     |
| **REPORT_OUTPUT_FOLDER**                            | `${GITHUB_WORKSPACE}/report` | Directory for generating report files                                                                                                                                                                       |
| **SHOW_ELAPSED_TIME**                               | `false`                      | Displays elapsed time in reports                                                                                                                                                                            |
| **SHOW_SKIPPED_LINTERS**                            | `true`                       | Displays all disabled linters mega-linter could have run                                                                                                                                                    |
| **TYPESCRIPT_DEFAULT_STYLE**                        | `standard`                   | Typescript default style to check/apply. `standard`,`prettier`                                                                                                                                              |
| **VALIDATE_ALL_CODEBASE**                           | `true`                       | Will parse the entire repository and find all files to validate across all types. **NOTE:** When set to `false`, only **new** or **edited** files will be parsed for validation.                            |

### Activation and deactivation

Mega-Linter have all linters enabled by default, but allows to enable only some, or disable only some

- If `ENABLE` is not set, all descriptors are activated by default. If set, all linters of listed descriptors will be activated by default
- If `ENABLE_LINTERS` is set, only listed linters will be processed
- If `DISABLE` is set, the linters in the listed descriptors will be skipped
- If `DISABLE_LINTERS` is set, the listed linters will be skipped

Examples:

- Run all javascript and groovy linters except STANDARD javascript linter

```yaml
ENABLE: JAVASCRIPT,GROOVY
DISABLE_LINTERS: JAVASCRIPT_STANDARD
```

- Run all linters except PHP linters (PHP_BUILTIN, PHP_PHPCS, PHP_PHPSTAN, PHP_PSALM)

```yaml
DISABLE: PHP
```

- Run all linters except PHP_PHPSTAN and PHP_PSALM linters

```yaml
DISABLE_LINTERS: PHP_PHPSTAN,PHP_PSALM
```

### Filter linted files

If you need to lint only a folder or exclude some files from linting, you can use optional environment parameters `FILTER_REGEX_INCLUDE` and `FILTER_REGEX_EXCLUDE`
You can apply filters to a single linter by defining variable `<LINTER_KEY>_FILTER_REGEX_INCLUDE` and `<LINTER_KEY>_FILTER_REGEX_EXCLUDE`

Examples:

- Lint only src folder: `FILTER_REGEX_INCLUDE: (src/)`
- Do not lint files inside test and example folders: `FILTER_REGEX_EXCLUDE: (test/|examples/)`
- Do not lint javascript files inside test folder: `FILTER_REGEX_EXCLUDE: (test/.*\.js)`

### Apply fixes

Mega-linter is able to apply fixes provided by linters. To use this capability, you need 3 **env variables** defined at top level

- **APPLY_FIXES**: `all` to apply fixes of all linters, or a list of linter keys (ex: `JAVASCRIPT_ES`,`MARKDOWN_MARKDOWNLINT`)

Only for GitHub Action Workflow file if you use it:

- **APPLY_FIXES_EVENT**: `all`, `push`, `pull_request`, `none` _(use none in case of use of [Updated sources reporter](https://github.com/megalinter/megalinter/tree/main/docs/reporters/UpdatedSourcesReporter.md))_
- **APPLY_FIXES_MODE**: `commit` to create a new commit and push it on the same branch, or `pull_request` to create a new PR targeting the branch.

Notes:

- You can use [**Updated sources reporter**](https://github.com/megalinter/megalinter/tree/main/docs/reporters/UpdatedSourcesReporter.md) if you do not want fixes to be automatically applied on git branch, but **download them in a zipped file** and manually **extract them in your project**
- If used, **APPLY_FIXES_EVENT** and **APPLY_FIXES_MODE** can not be defined in `.mega-linter.yml`config file, they must be set as environment variables

- If you use **APPLY_FIXES**, add the following line in your `.gitignore file`

```shell
report/
```

- You may see **github permission errors**, or workflows not run on the new commit. To solve these issues:
  - [Create Personal Access Token](https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/creating-a-personal-access-token#creating-a-token), then copy the PAT value
  - [Define secret variable](https://docs.github.com/en/free-pro-team@latest/actions/reference/encrypted-secrets#creating-encrypted-secrets-for-a-repository) named **PAT** on your repository, and paste the PAT value

### Linter specific variables

See variables related to a single linter behavior in [linters documentations](#supported-linters)

### Pre-commands

Mega-Linter can run custom commands before running linters (for example, installing an plugin required by one of the linters you use)

Example in `.mega-linter.yml` config file

```yaml
PRE_COMMANDS:
  - command: npm install eslint-plugin-whatever
    cwd: "root"        # Will be run at the root of Mega-Linter docker image
  - command: echo "pre-test command has been called"
    cwd: "workspace"   # Will be run at the root of the workspace (usually your repository root)
```

### Post-commands

Mega-Linter can run custom commands after running linters (for example, running additional tests)

Example in `.mega-linter.yml` config file

```yaml
POST_COMMANDS:
  - command: npm run test
    cwd: "workspace"   # Will be run at the root of the workspace (usually your repository root)
```

<!-- configuration-section-end -->

<!-- reporters-section-start -->
## Reporters

Mega-Linter can generate various reports that you can activate / deactivate and customize

| Reporter                                                                                                              | Description                                                                                                   | Default                 |
|-----------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|-------------------------|
| [Text files](https://github.com/megalinter/megalinter/tree/main/docs/reporters/TextReporter.md)                     | Generates **One log file by linter** + suggestions for fixes that can not be automated                        | Active                  |
| [Pull Request comments](https://github.com/megalinter/megalinter/tree/main/docs/reporters/GitHubCommentReporter.md) | Mega-Linter posts a comment on the PR with a summary of lint results, and links to detailed logs              | Active if GitHub Action |
| [Updated sources](https://github.com/megalinter/megalinter/tree/main/docs/reporters/UpdatedSourcesReporter.md)      | Zip containing **all formatted and auto-fixed sources** so you can extract them in your repository            | Active                  |
| [IDE Configuration](https://github.com/megalinter/megalinter/tree/main/docs/reporters/ConfigReporter.md)            | Apply Mega-Linter configuration in your local IDE with linter config files and IDE extensions                 | Active                  |
| [GitHub Status](https://github.com/megalinter/megalinter/tree/main/docs/reporters/GitHubStatusReporter.md)          | One GitHub status by linter on the PR, with links to detailed logs                                            | Active if GitHub Action |
| [File.io](https://github.com/megalinter/megalinter/tree/main/docs/reporters/FileIoReporter.md)                      | **Send reports on file.io** so you can access them with a simple hyperlink provided at the end of console log | Inactive                |
| [JSON](https://github.com/megalinter/megalinter/tree/main/docs/reporters/JsonReporter.md)                           | Generates a JSON output report file                                                                           | Inactive                |
| [Email](https://github.com/megalinter/megalinter/tree/main/docs/reporters/EmailReporter.md)                         | Receive **all reports on your e-mail**, if you can not use artifacts                                          | Active                  |
| [TAP files](https://github.com/megalinter/megalinter/tree/main/docs/reporters/TapReporter.md)                       | One file by linter following [**Test Anything Protocol**](https://testanything.org/) format                   | Active                  |
| [Console](https://github.com/megalinter/megalinter/tree/main/docs/reporters/ConsoleReporter.md)                     | **Execution logs** visible in **console** with **summary table** and **links to other reports** at the end    | Active                  |
<!-- reporters-section-end -->

<!-- flavors-section-start -->
## Flavors

To improve run performances, we generate **Flavored Mega-Linter images** containing only the list of linters related to a project type

- When using default Mega-Linter, if a Mega-Linter Flavor would cover all your project requirements, a message is added in the logs
- If your project uses a Mega-Linter Flavor not covering linter requirements, an error message will be thrown with instructions about how to solve the issue

<!-- flavors-table-start -->
|                                                                          <!-- -->                                                                          | Flavor                                                                                                     | Description                                                            | Embedded linters |                                                                                                                                                                                                 Info |
|:----------------------------------------------------------------------------------------------------------------------------------------------------------:|:-----------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------|:----------------:|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/images/mega-linter-square.png" alt="" height="32px" class="megalinter-icon"></a> | [all](https://megalinter.github.io/supported-linters/)                                                     | Default Mega-Linter Flavor                                             |        94        |                             ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/megalinter/megalinter/v5) ![Docker Pulls](https://img.shields.io/docker/pulls/megalinter/megalinter) |
|      <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/ci_light.ico" alt="" height="32px" class="megalinter-icon"></a>       | [ci_light](https://github.com/megalinter/megalinter/tree/main/docs/flavors/ci_light.md#readme)           | Optimized for CI items (Dockerfile, Jenkinsfile, JSON/YAML schemas,XML |        13        |           ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/megalinter/megalinter-ci_light/v5) ![Docker Pulls](https://img.shields.io/docker/pulls/megalinter/megalinter-ci_light) |
|        <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/dart.ico" alt="" height="32px" class="megalinter-icon"></a>         | [dart](https://github.com/megalinter/megalinter/tree/main/docs/flavors/dart.md#readme)                   | Optimized for DART based projects                                      |        41        |                   ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/megalinter/megalinter-dart/v5) ![Docker Pulls](https://img.shields.io/docker/pulls/megalinter/megalinter-dart) |
|    <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/documentation.ico" alt="" height="32px" class="megalinter-icon"></a>    | [documentation](https://github.com/megalinter/megalinter/tree/main/docs/flavors/documentation.md#readme) | Mega-Linter for documentation projects                                 |        40        | ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/megalinter/megalinter-documentation/v5) ![Docker Pulls](https://img.shields.io/docker/pulls/megalinter/megalinter-documentation) |
|       <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/dotnet.ico" alt="" height="32px" class="megalinter-icon"></a>        | [dotnet](https://github.com/megalinter/megalinter/tree/main/docs/flavors/dotnet.md#readme)               | Optimized for C, C++, C# or VB based projects                          |        47        |               ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/megalinter/megalinter-dotnet/v5) ![Docker Pulls](https://img.shields.io/docker/pulls/megalinter/megalinter-dotnet) |
|         <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/go.ico" alt="" height="32px" class="megalinter-icon"></a>          | [go](https://github.com/megalinter/megalinter/tree/main/docs/flavors/go.md#readme)                       | Optimized for GO based projects                                        |        42        |                       ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/megalinter/megalinter-go/v5) ![Docker Pulls](https://img.shields.io/docker/pulls/megalinter/megalinter-go) |
|        <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/java.ico" alt="" height="32px" class="megalinter-icon"></a>         | [java](https://github.com/megalinter/megalinter/tree/main/docs/flavors/java.md#readme)                   | Optimized for JAVA based projects                                      |        42        |                   ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/megalinter/megalinter-java/v5) ![Docker Pulls](https://img.shields.io/docker/pulls/megalinter/megalinter-java) |
|     <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/javascript.ico" alt="" height="32px" class="megalinter-icon"></a>      | [javascript](https://github.com/megalinter/megalinter/tree/main/docs/flavors/javascript.md#readme)       | Optimized for JAVASCRIPT or TYPESCRIPT based projects                  |        49        |       ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/megalinter/megalinter-javascript/v5) ![Docker Pulls](https://img.shields.io/docker/pulls/megalinter/megalinter-javascript) |
|         <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/php.ico" alt="" height="32px" class="megalinter-icon"></a>         | [php](https://github.com/megalinter/megalinter/tree/main/docs/flavors/php.md#readme)                     | Optimized for PHP based projects                                       |        44        |                     ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/megalinter/megalinter-php/v5) ![Docker Pulls](https://img.shields.io/docker/pulls/megalinter/megalinter-php) |
|       <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/python.ico" alt="" height="32px" class="megalinter-icon"></a>        | [python](https://github.com/megalinter/megalinter/tree/main/docs/flavors/python.md#readme)               | Optimized for PYTHON based projects                                    |        49        |               ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/megalinter/megalinter-python/v5) ![Docker Pulls](https://img.shields.io/docker/pulls/megalinter/megalinter-python) |
|        <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/ruby.ico" alt="" height="32px" class="megalinter-icon"></a>         | [ruby](https://github.com/megalinter/megalinter/tree/main/docs/flavors/ruby.md#readme)                   | Optimized for RUBY based projects                                      |        41        |                   ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/megalinter/megalinter-ruby/v5) ![Docker Pulls](https://img.shields.io/docker/pulls/megalinter/megalinter-ruby) |
|        <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/rust.ico" alt="" height="32px" class="megalinter-icon"></a>         | [rust](https://github.com/megalinter/megalinter/tree/main/docs/flavors/rust.md#readme)                   | Optimized for RUST based projects                                      |        41        |                   ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/megalinter/megalinter-rust/v5) ![Docker Pulls](https://img.shields.io/docker/pulls/megalinter/megalinter-rust) |
|     <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/salesforce.ico" alt="" height="32px" class="megalinter-icon"></a>      | [salesforce](https://github.com/megalinter/megalinter/tree/main/docs/flavors/salesforce.md#readme)       | Optimized for Salesforce based projects                                |        43        |       ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/megalinter/megalinter-salesforce/v5) ![Docker Pulls](https://img.shields.io/docker/pulls/megalinter/megalinter-salesforce) |
|        <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/scala.ico" alt="" height="32px" class="megalinter-icon"></a>        | [scala](https://github.com/megalinter/megalinter/tree/main/docs/flavors/scala.md#readme)                 | Optimized for SCALA based projects                                     |        41        |                 ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/megalinter/megalinter-scala/v5) ![Docker Pulls](https://img.shields.io/docker/pulls/megalinter/megalinter-scala) |
|        <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/swift.ico" alt="" height="32px" class="megalinter-icon"></a>        | [swift](https://github.com/megalinter/megalinter/tree/main/docs/flavors/swift.md#readme)                 | Optimized for SWIFT based projects                                     |        41        |                 ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/megalinter/megalinter-swift/v5) ![Docker Pulls](https://img.shields.io/docker/pulls/megalinter/megalinter-swift) |
|      <img src="https://github.com/megalinter/megalinter/raw/main/docs/assets/icons/terraform.ico" alt="" height="32px" class="megalinter-icon"></a>      | [terraform](https://github.com/megalinter/megalinter/tree/main/docs/flavors/terraform.md#readme)         | Optimized for TERRAFORM based projects                                 |        45        |         ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/megalinter/megalinter-terraform/v5) ![Docker Pulls](https://img.shields.io/docker/pulls/megalinter/megalinter-terraform) |
<!-- flavors-table-end -->

If you need a new flavor, [post an issue](https://github.com/megalinter/megalinter/issues) :wink:

<!-- flavors-section-end -->

<!-- badge-section-start -->
## Badge

You can show Mega-Linter status with a badge in your repository README

[![Mega-Linter](https://github.com/megalinter/megalinter/workflows/Mega-Linter/badge.svg?branch=main)](https://github.com/megalinter/megalinter/actions?query=workflow%3AMega-Linter+branch%3Amain)

If your main branch is **main** , replace **main** by **main** in URLs

### Markdown

- Format

```markdown
[![Mega-Linter](https://github.com/<OWNER>/<REPOSITORY>/workflows/Mega-Linter/badge.svg?branch=main)](https://github.com/<OWNER>/<REPOSITORY>/actions?query=workflow%3AMega-Linter+branch%3Amain)
```

- Example

```markdown
[![Mega-Linter](https://github.com/nvuillam/npm-groovy-lint/workflows/Mega-Linter/badge.svg?branch=main)](https://github.com/nvuillam/npm-groovy-lint/actions?query=workflow%3AMega-Linter+branch%3Amain)
```

### reStructuredText

- Format

```markdown
.. |Mega-Linter yes| image:: https://github.com/<OWNER>/<REPOSITORY>/workflows/Mega-Linter/badge.svg?branch=main
   :target: https://github.com/<OWNER>/<REPOSITORY>/actions?query=workflow%3AMega-Linter+branch%3Amain
```

- Example

```markdown
.. |Mega-Linter yes| image:: https://github.com/nvuillam/npm-groovy-lint/workflows/Mega-Linter/badge.svg?branch=main
   :target: https://github.com/nvuillam/npm-groovy-lint/actions?query=workflow%3AMega-Linter+branch%3Amain
```

_Note:_ IF you did not use `Mega-Linter` as GitHub Action name, please read [GitHub Actions Badges documentation](https://docs.github.com/en/actions/configuring-and-managing-workflows/configuring-a-workflow#adding-a-workflow-status-badge-to-your-repository){target=_blank}
<!-- badge-section-end -->

<!-- plugins-section-start -->
## Plugins

### Use plugins

Just add plugin URLs in `PLUGINS` property of `.mega-linter.yml`

#### Example

```yaml
PLUGINS:
  - https://raw.githubusercontent.com/megalinter/megalinter/main/.automation/test/mega-linter-plugin-test/test.megalinter-descriptor.yml
  - https://raw.githubusercontent.com/cookiejar/mega-linter-plugin-cookietemple/main/cookietemple.megalinter-descriptor.yml
```

### Create plugins

You can implement your own descriptors and load them as plugins during Mega-Linter runtime

- Plugins descriptor files must be named **\*\*.megalinter-descriptor.yml** and respect [Mega-Linter Json Schema](https://github.com/megalinter/megalinter/blob/main/megalinter/descriptors/schemas/megalinter-descriptor.jsonschema.json)
- Descriptor format is exactly the same than [Mega-Linter embedded ones](https://github.com/megalinter/megalinter/tree/main/megalinter/descriptors) ([see json schema documentation](https://megalinter.github.io/json-schemas/descriptor.html))
- Plugins must be hosted in a url containing **\*\*/mega-linter-plugin-\*\*/**

#### Limitations

- For now, the only `install` attributes managed are `dockerfile` instructions starting by `RUN`
<!-- plugins-section-end -->

<!-- frequently-asked-questions-section-start -->
## Frequently Asked Questions

> My repo CI already have linters and they are perfectly working, so why do I need Mega-Linter ?

You can perfectly **continue using your installed linters** and deactivate them in `.mega-linter.yml`. For example, in a javascript project using eslint, you can configure Mega-Linter with `DISABLE: JAVASCRIPT`. That way, you will benefit from both your installed linters but also from other Mega-Linter linters checking JSON, YAML, Markdown, Dockerfile, Bash, spelling mistakes, dead URLs...

> Ok but... how does it work ?

Mega-Linter is based on Docker images containing either all linters, or just a selection of linters if you are using a Mega-Linter flavor for a project using a specific language / format

The core architecture does the following:

- **Initialization**
  - **List all project files**:
    - except files in ignored folders (`node_modules`, etc...)
    - except files not matching `FILTER_REGEX_INCLUDE` (if defined by user)
    - except files matching `FILTER_REGEX_EXCLUDE` (if defined by user)
  - **Collect files for each activated linter**, matching their **own filtering criteria**:
    - file extensions
    - file names
    - file content
    - `<descriptor_or_linter_key>_FILTER_REGEX_INCLUDE` (if defined by user)
    - `<descriptor_or_linter_key>_FILTER_REGEX_EXCLUDE` (if defined by user)
- **Linting**
  - **Parallelly**, for **each linter** with matching files:
    - **Call the linter** on matching files (or the whole project for some linters like copy-paste detector)
    - Call activated **linter-level reporters** (GitHub Status Reporter...)
- **Finalization**
  - Call activated **global level reporters** (GitHub Pull Request Comment Reporter, File.io Reporter, Email Reporter...)
  - Manage return code:
    - **0** if no error (or only non blocking errors if user defined `DISABLE_ERRORS` or `<descriptor_or_linter_key>_DISABLE_ERRORS`)
    - **1** if errors

<!-- frequently-asked-questions-section-end -->

<!-- how-to-contribute-section-start -->
## How to contribute

Contributions to Mega-Linter are very welcome, the more we are, the stronger Mega-Linter is !
Please follow [Contributing Guide](https://megalinter.github.io/contributing/)

To help, you can also:

- [:star: star the repository](https://github.com/megalinter/megalinter/stargazers)
- [:beer: offer a beer !](https://github.com/sponsors/nvuillam)
- [report problems and request new features](https://github.com/megalinter/megalinter/issues)
- [share on twitter](http://twitter.com/intent/tweet/?text=Mega-Linter:%2070%20linters%20aggregator%20easy%20to%20use%20for%20all%20your%20projects&url=http://megalinter.github.io/&via=nvuillam){target=_blank}
<!-- how-to-contribute-section-end -->

<!-- special-thanks-section-start -->
## Special thanks

### Contributors

<a href="https://github.com/megalinter/megalinter/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=megalinter/megalinter" />
</a>

### Sites referring to Mega-Linter

#### Global

- [analysis-tools.dev](https://analysis-tools.dev/tool/mega-linter){target=_blank}
- [awesome-linters](https://github.com/caramelomartins/awesome-linters#language-agnostic){target=_blank}
- [schemastore.org](https://www.schemastore.org/json/){target=_blank}

#### Articles
- [Linting a Jekyll blog with Mega-Linter](https://www.ayyjohn.com/posts/linting-a-jekyll-blog-with-mega-linter), by [Alec Johnson](https://www.linkedin.com/in/ayyjohn/){target=_blank}
- [Open-source linters landscape in 2021](https://promyze.com/open-source-linters-2021/), by [Cédric Teyton](https://www.linkedin.com/in/cedricteyton/){target=_blank}

#### Linters

<!-- referring-linters-start -->
- [checkstyle](https://checkstyle.sourceforge.io/index.html#Related_Tools_Active_Tools){target=_blank}
- [clj-kondo](https://github.com/borkdude/clj-kondo/blob/main/doc/ci-integration.md#github){target=_blank}
- [cspell](https://github.com/streetsidesoftware/cspell/tree/main/packages/cspell#mega-linter){target=_blank}
- [dotenv-linter](https://dotenv-linter.github.io/#/integrations/mega_linter){target=_blank}
- [editorconfig-checker](https://github.com/editorconfig-checker/editorconfig-checker#mega-linter){target=_blank}
- [eslint](https://eslint.org/docs/user-guide/integrations#source-control){target=_blank}
- [eslint-plugin-jsonc](https://eslint.org/docs/user-guide/integrations#source-control){target=_blank}
- [hadolint](https://github.com/hadolint/hadolint/blob/main/docs/INTEGRATION.md#mega-linter){target=_blank}
- [jscpd](https://github.com/kucherenko/jscpd#who-uses-jscpd){target=_blank}
- [ktlint](https://github.com/pinterest/ktlint#-with-continuous-integration){target=_blank}
- [markdown-link-check](https://github.com/tcort/markdown-link-check#run-in-other-tools){target=_blank}
- [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/#mega-linter){target=_blank}
- [rst-lint](https://github.com/twolfson/restructuredtext-lint/wiki/Integration-in-other-tools#integration-in-other-tools){target=_blank}
- [rubocop](https://docs.rubocop.org/rubocop/integration_with_other_tools.html#mega-linter-integration){target=_blank}
- [scalafix](https://scalacenter.github.io/scalafix/docs/users/installation.html#plugins-for-other-build-tools){target=_blank}
- [secretlint](https://github.com/secretlint/secretlint#mega-linter){target=_blank}
- [stylelint](https://stylelint.io/user-guide/integrations/other#analysis-platform-engines){target=_blank}
<!-- referring-linters-end -->

### Open-source teams

Mega-Linter obviously would not exist without its linters and libraries, so many thanks to all the dedicated Open-Source teams maintaining all these awesome linters !

### Super-Linter team

Mega-Linter has been built on the ashes of a [rejected Pull Request](https://github.com/github/super-linter/pull/791){target=_blank} on [GitHub Super-Linter](https://github.com/github/super-linter){target=_blank}.

Even if I disagree with their decision to remain in bash, the core team has always been nice and supporting [during the time I was a Super-Linter contributor](https://github.com/github/super-linter/pulls?q=is%3Apr+is%3Aclosed+author%3Anvuillam+review%3Aapproved){target=_blank} :)
<!-- special-thanks-section-end -->

<!-- license-section-start -->
## License

- [GNU Affero General Public License](https://github.com/megalinter/megalinter/blob/main/LICENSE)
<!-- license-section-end -->

<!-- mega-linter-vs-super-linter-section-start -->
## Mega-Linter vs Super-Linter

The hard-fork of Super-Linter to be rewritten in Python is not just a language switch: use of python flexibility and libraries allowed to define lots of additional functions described below

### Performances

- [Mega-Linter Flavors](#flavors) allow to use **smaller docker images**, so the pull time is reduced
- Thanks to python multiprocessing capabilities, **linters are run in parallel**, which is way faster than Super-Linter bash script who runs all linters in sequence
- When the linter allows it, call it **1 time with N files**, instead of calling **N times with one file**

### More languages and formats linted

- **C**, **C++**, **Copy-Paste detection**, **GraphQL**, **JSON & YAML with JSON schemas**, **Markdown tables formatting**, **Puppet**, **reStructuredText**, **Rust**, **Scala**, **Spell checker**, **Swift**, **Visual Basic .NET** ...

### Automatically apply formatting and fixes

Mega-Linter can [**automatically apply fixes performed by linters**](#apply-fixes), and **push them to the same branch**, or **create a Pull Request** that you can validate

This is pretty handy, especially for linter errors related to formatting (in that case, you don't have any manual update to perform)

### Run locally

Mega-Linter can be run locally thanks to [mega-linter-runner](https://megalinter.github.io/mega-linter-runner/)

### Reports

#### Capabilities

- Accuracy: Count the total number of errors and not only the number of files in error
- Show linter version and applied filters for each linter processed
- Reports stored as artefacts on GitHub Action run or other remote files
  - General log
  - One report file by linter

#### Additional Reporters

- [Console](https://github.com/megalinter/megalinter/tree/main/docs/reporters/ConsoleReporter.md)

![Screenshot](https://github.com/megalinter/megalinter/blob/main/docs/assets/images/ConsoleReporter.jpg?raw=true>)

- [Text files](https://github.com/megalinter/megalinter/tree/main/docs/reporters/TextReporter.md)
- [Pull Request comments](https://github.com/megalinter/megalinter/tree/main/docs/reporters/GitHubCommentReporter.md)

![Screenshot](https://github.com/megalinter/megalinter/blob/main/docs/assets/images/GitHubCommentReporter.jpg?raw=true>)

- [Updated sources](https://github.com/megalinter/megalinter/tree/main/docs/reporters/UpdatedSourcesReporter.md)
- [Email](https://github.com/megalinter/megalinter/tree/main/docs/reporters/EmailReporter.md)
- [File.io](https://github.com/megalinter/megalinter/tree/main/docs/reporters/FileIoReporter.md)

### Enhanced Configuration

- **Assisted installation and configuration** using a yeoman generator and JSON schemas for configuration file

![Runner Install](https://github.com/megalinter/megalinter/blob/main/docs/assets/images/mega-linter-runner-generator.jpg?raw=true)

![Assisted configuration](https://github.com/megalinter/megalinter/raw/main/docs/assets/images/assisted-configuration.jpg)

- Configure **include and exclude regexes** for a **single language or linter**: ex: `JAVASCRIPT_FILTER_REGEX_INCLUDE (src)`
- Configure **additional CLI arguments** for a linter: ex: `JAVASCRIPT_ES_ARGUMENTS "--debug --env-info"`
- Configure **non blocking errors** for a **single language or linter**: ex: `JAVASCRIPT_DISABLE_ERRORS`
- **Simplify languages and linters variables**
  - ENABLE = list of languages and formats to apply lint on codebase (default: all)
  - ENABLE_LINTERS = list of linters to apply lint on codebase (default: all)
  - DISABLE = list of languages and formats to skip (default: none)
  - DISABLE_LINTERS = list of linters to skip (default: none)
  - Variables VALIDATE_XXX are still taken in account (but should not be used in association with ENABLE and DISABLE variables)

### Enhanced Documentation

- [**HTML documentation**](https://megalinter.github.io/)

![HTML doc home](https://github.com/megalinter/megalinter/raw/main/docs/assets/images/html_doc_home.jpg)

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

![HTML doc linter](https://github.com/megalinter/megalinter/raw/main/docs/assets/images/html_doc_linter.jpg)

- Installation links for related IDEs

![HTML doc IDE](https://github.com/megalinter/megalinter/raw/main/docs/assets/images/html_doc_ide.jpg)

- README
  - Separate languages, formats and tooling formats in the linters table
  - Add logos for each descriptor

### Plugins management

For linters less commonly used, Mega-Linters offers a plugins architecture so anyone can publish plugins

### Simplify architecture and evolutive maintenance

- Refactoring runtime in Python, for easier handling than bash thanks to [classes](https://github.com/megalinter/megalinter/tree/main/megalinter) and python modules
- Everything related to each linter [in a single descriptor YML file](https://github.com/megalinter/megalinter/tree/main/megalinter/descriptors)
  - easier evolutive maintenance
  - less conflicts to manage between PRs.
  - Few special cases require a [python linter class](https://github.com/megalinter/megalinter/tree/main/megalinter/descriptors))
- [Default behaviours for all linters](https://github.com/megalinter/megalinter/blob/main/megalinter/Linter.py), with possibility to override part of them for special cases
- Hierarchical architecture: Apply fixes and new behaviours to all linters with a single code update
- **Documentation as code**
  - Generate linters tables (ordered by type: language, format & tooling format) and include it in README. [(see result)](https://megalinter.github.io/supported-linters/)
  - Generate one markdown file per Linter, containing all configuration variables, infos and examples [(See examples)](https://megalinter.github.io/descriptors/javascript_eslint/)
- **Automatic generation of Dockerfile** using YML descriptors, always using the linter latest version
  - Dockerfile commands (FROM, ARG, ENV, COPY, RUN )
  - APK packages (linux)
  - NPM packages (node)
  - PIP packages (python)
  - GEM packages (ruby)
  - Phive packages (PHP)
- Have a centralized exclude list (node_modules,.rbenv, etc...)

### Improve robustness & stability

- [Test classes](https://github.com/megalinter/megalinter/blob/main/megalinter/tests/test_megalinter) for each capability
- [Test classes for each linter](https://github.com/megalinter/megalinter/tree/main/megalinter/tests/test_megalinter/linters): Automatic generation of test classes using [.automation/build.py](https://github.com/megalinter/megalinter/blob/main/.automation/build.py)
- Setup **code coverage** [![codecov](https://codecov.io/gh/megalinter/megalinter/branch/main/graph/badge.svg)](https://codecov.io/gh/megalinter/megalinter)
- **Development CD / CI**
  - Validate multi-status on PR inside each PR (posted from step "Run against all code base")
  - Run test classes and code coverage with pytest during validation GitHub Action
  - Validate descriptor YML files with json schema during build
  - Automated job to upgrade linters to their latest stable version
<!-- mega-linter-vs-super-linter-section-end -->

## V4 versus V5

- Version management: Now mega-linter docker images, github action and mega-linter-runner versions are aligned
  - **latest** for latest official release
  - **beta** for current content of main branch
  - **alpha** for current content of alpha branch
  - docker image, github action and mega-linter-runner can still be called with exact version number
- Being more inclusive: rename `master` branch into `main`