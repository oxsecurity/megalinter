---
title: actionlint configuration in MegaLinter
description: How to use actionlint (configure, ignore files, ignore errors, help & version documentations) to analyze ACTION files
---
<!-- markdownlint-disable MD033 MD041 -->
<!-- @generated by .automation/build.py, please don't update manually -->
# actionlint
[![GitHub stars](https://img.shields.io/github/stars/rhysd/actionlint?cacheSeconds=3600)](https://github.com/rhysd/actionlint) [![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/rhysd/actionlint?sort=semver)](https://github.com/rhysd/actionlint/releases) [![GitHub last commit](https://img.shields.io/github/last-commit/rhysd/actionlint)](https://github.com/rhysd/actionlint/commits) [![GitHub commit activity](https://img.shields.io/github/commit-activity/y/rhysd/actionlint)](https://github.com/rhysd/actionlint/graphs/commit-activity/) [![GitHub contributors](https://img.shields.io/github/contributors/rhysd/actionlint)](https://github.com/rhysd/actionlint/graphs/contributors/)

Static checker for GitHub Actions workflow files

## actionlint documentation

- Version in MegaLinter: **1.6.27**
- Visit [Official Web Site](https://rhysd.github.io/actionlint/){target=_blank}
- See [How to configure actionlint rules](https://github.com/rhysd/actionlint/blob/main/docs/config.md){target=_blank}

[![actionlint - GitHub](https://gh-card.dev/repos/rhysd/actionlint.svg?fullname=)](https://github.com/rhysd/actionlint){target=_blank}

## Configuration in MegaLinter

- Enable actionlint by adding `ACTION_ACTIONLINT` in [ENABLE_LINTERS variable](https://megalinter.io/beta/configuration/#activation-and-deactivation)
- Disable actionlint by adding `ACTION_ACTIONLINT` in [DISABLE_LINTERS variable](https://megalinter.io/beta/configuration/#activation-and-deactivation)

| Variable                                      | Description                                                                                                                                                                                                         | Default value                                   |
|-----------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| ACTION_ACTIONLINT_ARGUMENTS                   | User custom arguments to add in linter CLI call<br/>Ex: `-s --foo "bar"`                                                                                                                                            |                                                 |
| ACTION_ACTIONLINT_COMMAND_REMOVE_ARGUMENTS    | User custom arguments to remove from command line before calling the linter<br/>Ex: `-s --foo "bar"`                                                                                                                |                                                 |
| ACTION_ACTIONLINT_FILTER_REGEX_INCLUDE        | Custom regex including filter<br/>Ex: `(src\|lib)`                                                                                                                                                                  | Include every file                              |
| ACTION_ACTIONLINT_FILTER_REGEX_EXCLUDE        | Custom regex excluding filter<br/>Ex: `(test\|examples)`                                                                                                                                                            | Exclude no file                                 |
| ACTION_ACTIONLINT_CLI_LINT_MODE               | Override default CLI lint mode<br/>- `file`: Calls the linter for each file<br/>- `list_of_files`: Call the linter with the list of files as argument<br/>- `project`: Call the linter from the root of the project | `list_of_files`                                 |
| ACTION_ACTIONLINT_FILE_EXTENSIONS             | Allowed file extensions. `"*"` matches any extension, `""` matches empty extension. Empty list excludes all files<br/>Ex: `[".py", ""]`                                                                             | `[".yml", ".yaml"]`                             |
| ACTION_ACTIONLINT_FILE_NAMES_REGEX            | File name regex filters. Regular expression list for filtering files by their base names using regex full match. Empty list includes all files<br/>Ex: `["Dockerfile(-.+)?", "Jenkinsfile"]`                        | Include every file                              |
| ACTION_ACTIONLINT_PRE_COMMANDS                | List of bash commands to run before the linter                                                                                                                                                                      | None                                            |
| ACTION_ACTIONLINT_POST_COMMANDS               | List of bash commands to run after the linter                                                                                                                                                                       | None                                            |
| ACTION_ACTIONLINT_UNSECURED_ENV_VARIABLES     | List of env variables explicitly not filtered before calling ACTION_ACTIONLINT and its pre/post commands                                                                                                            | None                                            |
| ACTION_ACTIONLINT_CONFIG_FILE                 | actionlint configuration file name</br>Use `LINTER_DEFAULT` to let the linter find it                                                                                                                               | `actionlint.yml`                                |
| ACTION_ACTIONLINT_RULES_PATH                  | Path where to find linter configuration file                                                                                                                                                                        | Workspace folder, then MegaLinter default rules |
| ACTION_ACTIONLINT_DISABLE_ERRORS              | Run linter but consider errors as warnings                                                                                                                                                                          | `false`                                         |
| ACTION_ACTIONLINT_DISABLE_ERRORS_IF_LESS_THAN | Maximum number of errors allowed                                                                                                                                                                                    | `0`                                             |
| ACTION_ACTIONLINT_CLI_EXECUTABLE              | Override CLI executable                                                                                                                                                                                             | `['actionlint']`                                |
| ACTION_DIRECTORY                              | Directory containing ACTION files (use `any` to always activate the linter)                                                                                                                                         | `.github/workflows`                             |

## MegaLinter Flavours

This linter is available in the following flavours

|                                                                         <!-- -->                                                                         | Flavor                                                             | Description                                              | Embedded linters |                                                                                                                                                                                                   Info |
|:--------------------------------------------------------------------------------------------------------------------------------------------------------:|:-------------------------------------------------------------------|:---------------------------------------------------------|:----------------:|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/images/mega-linter-square.png" alt="" height="32px" class="megalinter-icon"></a> | [all](https://megalinter.io/beta/supported-linters/)               | Default MegaLinter Flavor                                |       121        |                             ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter) |
|        <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/c_cpp.ico" alt="" height="32px" class="megalinter-icon"></a>        | [c_cpp](https://megalinter.io/beta/flavors/c_cpp/)                 | Optimized for pure C/C++ projects                        |        55        |                 ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-c_cpp/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-c_cpp) |
|       <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/cupcake.ico" alt="" height="32px" class="megalinter-icon"></a>       | [cupcake](https://megalinter.io/beta/flavors/cupcake/)             | MegaLinter for the most commonly used languages          |        84        |             ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-cupcake/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-cupcake) |
|    <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/documentation.ico" alt="" height="32px" class="megalinter-icon"></a>    | [documentation](https://megalinter.io/beta/flavors/documentation/) | MegaLinter for documentation projects                    |        51        | ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-documentation/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-documentation) |
|       <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/dotnet.ico" alt="" height="32px" class="megalinter-icon"></a>        | [dotnet](https://megalinter.io/beta/flavors/dotnet/)               | Optimized for C, C++, C# or VB based projects            |        64        |               ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-dotnet/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-dotnet) |
|      <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/dotnetweb.ico" alt="" height="32px" class="megalinter-icon"></a>      | [dotnetweb](https://megalinter.io/beta/flavors/dotnetweb/)         | Optimized for C, C++, C# or VB based projects with JS/TS |        73        |         ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-dotnetweb/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-dotnetweb) |
|         <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/go.ico" alt="" height="32px" class="megalinter-icon"></a>          | [go](https://megalinter.io/beta/flavors/go/)                       | Optimized for GO based projects                          |        53        |                       ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-go/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-go) |
|        <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/java.ico" alt="" height="32px" class="megalinter-icon"></a>         | [java](https://megalinter.io/beta/flavors/java/)                   | Optimized for JAVA based projects                        |        54        |                   ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-java/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-java) |
|     <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/javascript.ico" alt="" height="32px" class="megalinter-icon"></a>      | [javascript](https://megalinter.io/beta/flavors/javascript/)       | Optimized for JAVASCRIPT or TYPESCRIPT based projects    |        60        |       ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-javascript/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-javascript) |
|         <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/php.ico" alt="" height="32px" class="megalinter-icon"></a>         | [php](https://megalinter.io/beta/flavors/php/)                     | Optimized for PHP based projects                         |        54        |                     ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-php/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-php) |
|       <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/python.ico" alt="" height="32px" class="megalinter-icon"></a>        | [python](https://megalinter.io/beta/flavors/python/)               | Optimized for PYTHON based projects                      |        62        |               ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-python/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-python) |
|        <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/ruby.ico" alt="" height="32px" class="megalinter-icon"></a>         | [ruby](https://megalinter.io/beta/flavors/ruby/)                   | Optimized for RUBY based projects                        |        51        |                   ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-ruby/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-ruby) |
|        <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/rust.ico" alt="" height="32px" class="megalinter-icon"></a>         | [rust](https://megalinter.io/beta/flavors/rust/)                   | Optimized for RUST based projects                        |        51        |                   ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-rust/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-rust) |
|     <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/salesforce.ico" alt="" height="32px" class="megalinter-icon"></a>      | [salesforce](https://megalinter.io/beta/flavors/salesforce/)       | Optimized for Salesforce based projects                  |        55        |       ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-salesforce/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-salesforce) |
|        <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/swift.ico" alt="" height="32px" class="megalinter-icon"></a>        | [swift](https://megalinter.io/beta/flavors/swift/)                 | Optimized for SWIFT based projects                       |        51        |                 ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-swift/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-swift) |
|      <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/terraform.ico" alt="" height="32px" class="megalinter-icon"></a>      | [terraform](https://megalinter.io/beta/flavors/terraform/)         | Optimized for TERRAFORM based projects                   |        55        |         ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-terraform/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-terraform) |

## Behind the scenes

### How are identified applicable files

- Activated only if sub-directory `.github/workflows` is found. (directory name can be overridden with `ACTION_DIRECTORY`)
- File extensions: `.yml`, `.yaml`

<!-- markdownlint-disable -->
<!-- /* cSpell:disable */ -->
### How the linting is performed

- actionlint is called once with the list of files as arguments (`list_of_files` CLI lint mode)

### Example calls

```shell
actionlint /path/to/workflow1.yml /path/to/workflow2.yaml
```


### Help content

```shell
Usage: actionlint [FLAGS] [FILES...] [-]

  actionlint is a linter for GitHub Actions workflow files.

  To check all YAML files in current repository, just run actionlint without
  arguments. It automatically finds the nearest '.github/workflows' directory:

    $ actionlint

  To check specific files, pass the file paths as arguments:

    $ actionlint file1.yaml file2.yaml

  To check content which is not saved in file yet (e.g. output from some
  command), pass - argument. It reads stdin and checks it as workflow file:

    $ actionlint -

  To serialize errors into JSON, use -format option. It allows to format error
  messages flexibly with Go template syntax.

    $ actionlint -format '{{json .}}'

Documents:

  https://github.com/rhysd/actionlint/tree/main/docs

Flags:
  -color
      Always enable colorful output. This is useful to force colorful outputs
  -config-file string
      File path to config file
  -debug
      Enable debug output (for development)
  -format string
      Custom template to format error messages in Go template syntax. See https://github.com/rhysd/actionlint/tree/main/docs/usage.md#format
  -ignore value
      Regular expression matching to error messages you want to ignore. This flag is repeatable
  -init-config
      Generate default config file at .github/actionlint.yaml in current project
  -no-color
      Disable colorful output
  -oneline
      Use one line per one error. Useful for reading error messages from programs
  -pyflakes string
      Command name or file path of "pyflakes" external command. If empty, pyflakes integration will be disabled (default "pyflakes")
  -shellcheck string
      Command name or file path of "shellcheck" external command. If empty, shellcheck integration will be disabled (default "shellcheck")
  -stdin-filename string
      File name when reading input from stdin
  -verbose
      Enable verbose output
  -version
      Show version and how this binary was installed
```

### Installation on mega-linter Docker image

- Dockerfile commands :
```dockerfile
FROM rhysd/actionlint:latest as actionlint
# shellcheck is a dependency for actionlint

FROM koalaman/shellcheck:stable as shellcheck
COPY --link --from=actionlint /usr/local/bin/actionlint /usr/bin/actionlint
# shellcheck is a dependency for actionlint

COPY --link --from=shellcheck /bin/shellcheck /usr/bin/shellcheck
```

- APK packages (Linux):
  - [py3-pyflakes](https://pkgs.alpinelinux.org/packages?branch=edge&name=py3-pyflakes)