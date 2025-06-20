---
title: MegaLinter configuration Guide
description: List of all configuration variables that can be used to customize the use of MegaLinter (activation, filtering, auto-update, pre-post commands…)
---
<!-- markdownlint-disable MD013 -->
<!-- Generated by .automation/build.py, please do not update manually -->
<!-- configuration-section-start -->

# Configuration

MegaLinter configuration variables are defined in a **.mega-linter.yml** file at the root of the repository or with **environment variables**.
You can see an example config file in this repo: [**.mega-linter.yml**](https://github.com/oxsecurity/megalinter/blob/main/.mega-linter.yml)

Configuration is assisted with autocompletion and validation in most commonly used IDEs, thanks to [JSON schema](https://megalinter.io/json-schemas/configuration.html) stored on [schemastore.org](https://www.schemastore.org/)

- VSCode: You need a VSCode extension like [Red Hat YAML](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml)
- IDEA family: Auto-completion natively supported

![Assisted configuration](https://github.com/oxsecurity/megalinter/raw/main/docs/assets/images/assisted-configuration.gif)

## Common variables

| **ENV VAR**                                                          | **Default Value**                             | **Notes**                                                                                                                                                                                                  |
|----------------------------------------------------------------------|-----------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **ADDITIONAL_EXCLUDED_DIRECTORIES**                                  | \[\]                                          | List of additional excluded directory basenames. they're excluded at any nested level.                                                                                                                     |
| [**APPLY_FIXES**](configuration.md#apply-fixes)                      | `none`                                        | Activates formatting and autofix [(more info)](configuration.md#apply-fixes)                                                                                                                               |
| **CLEAR_REPORT_FOLDER**                                              | `false`                                       | Flag to clear files from report folder (usually megalinter-reports) before starting the linting process                                                                                                    |
| **DEFAULT_BRANCH**                                                   | `HEAD`                                        | Deprecated: The name of the repository's default branch.                                                                                                                                                   |
| **DEFAULT_WORKSPACE**                                                | `/tmp/lint`                                   | The location containing files to lint if you are running locally.                                                                                                                                          |
| **DISABLE_ERRORS**                                                   | `false`                                       | Flag to have the linter complete with exit code 0 even if errors were detected.                                                                                                                            |
| [**DISABLE**](#activation-and-deactivation)                          | <!-- -->                                      | List of disabled descriptors keys [(more info)](#activation-and-deactivation)                                                                                                                              |
| [**DISABLE_LINTERS**](#activation-and-deactivation)                  | <!-- -->                                      | List of disabled linters keys [(more info)](#activation-and-deactivation)                                                                                                                                  |
| [**DISABLE_ERRORS_LINTERS**](#activation-and-deactivation)           | <!-- -->                                      | List of enabled but not blocking linters keys [(more info)](#activation-and-deactivation)                                                                                                                  |
| [**ENABLE**](#activation-and-deactivation)                           | <!-- -->                                      | List of enabled descriptors keys [(more info)](#activation-and-deactivation)                                                                                                                               |
| [**ENABLE_LINTERS**](#activation-and-deactivation)                   | <!-- -->                                      | List of enabled linters keys [(more info)](#activation-and-deactivation)                                                                                                                                   |
| **EXCLUDED_DIRECTORIES**                                             | \[…many values…\]                             | List of excluded directory basenames. they're excluded at any nested level.                                                                                                                                |
| **EXTENDS**                                                          | <!-- -->                                      | Base `mega-linter.yml` config file(s) to extend local configuration from. Can be a single URL or a list of `.mega-linter.yml` config files URLs. Later files take precedence.                              |
| **FAIL_IF_MISSING_LINTER_IN_FLAVOR**                                 | `false`                                       | If set to `true`, MegaLinter fails if a linter is missing in the selected flavor                                                                                                                           |
| **FAIL_IF_UPDATED_SOURCES**                                          | `false`                                       | If set to `true`, MegaLinter fails if a linter or formatter has autofixed sources, even if there are no errors                                                                                             |
| [**FILTER_REGEX_EXCLUDE**](#filter-linted-files)                     | `none`                                        | Regular expression defining which files will be excluded from linting [(more info)](#filter-linted-files) .ex: `.*src/test.*`)                                                                             |
| [**FILTER_REGEX_INCLUDE**](#filter-linted-files)                     | `all`                                         | Regular expression defining which files will be processed by linters [(more info)](#filter-linted-files) .ex: `.*src/.*`)                                                                                  |
| **FLAVOR_SUGGESTIONS**                                               | `true`                                        | Provides suggestions about different MegaLinter flavors to use to improve runtime performances                                                                                                             |
| **FORMATTERS_DISABLE_ERRORS**                                        | `true`                                        | Formatter errors will be reported as errors (and not warnings) if this variable is set to `false`                                                                                                          |
| **GIT_AUTHORIZATION_BEARER**                                         | <!-- -->                                      | If set, calls git with **`Authorization: Bearer`+value**                                                                                                                                                   |
| **GITHUB_WORKSPACE**                                                 | <!-- -->                                      | Base directory for `REPORT_OUTPUT_FOLDER`, for user-defined linter rules location, for location of linted files if `DEFAULT_WORKSPACE` isn't set                                                           |
| **IGNORE_GENERATED_FILES**                                           | `false`                                       | If set to `true`, MegaLinter will skip files containing `@generated` marker but without `@not-generated` marker (more info at [https://generated.at](https://generated.at/))                               |
| **IGNORE_GITIGNORED_FILES**                                          | `true`                                        | If set to `true`, MegaLinter will skip files ignored by git using `.gitignore` file                                                                                                                        |
| **JAVASCRIPT_DEFAULT_STYLE**                                         | `standard`                                    | Javascript default style to check/apply. `standard`,`prettier`                                                                                                                                             |
| **LINTER_RULES_PATH**                                                | `.github/linters`                             | Directory for all linter configuration rules.<br/> Can be a local folder or a remote URL (ex: `https://raw.githubusercontent.com/some_org/some_repo/mega-linter-rules` )                                   |
| **LOG_FILE**                                                         | `mega-linter.log`                             | The file name for outputting logs. All output is sent to the log file regardless of `LOG_LEVEL`. Use `none` to not generate this file.                                                                     |
| **LOG_LEVEL**                                                        | `INFO`                                        | How much output the script will generate to the console. One of `INFO`, `DEBUG`, `WARNING` or `ERROR`.                                                                                                     |
| **MARKDOWN_DEFAULT_STYLE**                                           | `markdownlint`                                | Markdown default style to check/apply. `markdownlint`,`remark-lint`                                                                                                                                        |
| **MEGALINTER_CONFIG**                                                | `.mega-linter.yml`                            | Name of MegaLinter configuration file. Can be defined remotely, in that case set this environment variable with the remote URL of `.mega-linter.yml` config file                                           |
| **MEGALINTER_FILES_TO_LINT**                                         | \[\]                                          | Comma-separated list of files to analyze. Using this variable will bypass other file listing methods                                                                                                       |
| **PARALLEL**                                                         | `true`                                        | Process linters in parallel to improve overall MegaLinter performance. If true, linters of same language or formats are grouped in the same parallel process to avoid lock issues if fixing the same files |
| [**PLUGINS**](plugins.md)                                            | \[\]                                          | List of plugin urls to install and run during MegaLinter run                                                                                                                                               |
| [**POST_COMMANDS**](#post-commands)                                  | \[\]                                          | Custom bash commands to run after linters                                                                                                                                                                  |
| [**PRE_COMMANDS**](#pre-commands)                                    | \[\]                                          | Custom bash commands to run before linters                                                                                                                                                                 |
| **PRINT_ALPACA**                                                     | `true`                                        | Enable printing alpaca image to console                                                                                                                                                                    |
| **PRINT_ALL_FILES**                                                  | `false`                                       | Display all files analyzed by the linter instead of only the number                                                                                                                                        |
| **REPORT_OUTPUT_FOLDER**                                             | `${GITHUB_WORKSPACE}/megalinter-reports`      | Directory for generating report files. Set to `none` to not generate reports                                                                                                                               |
| [**SECURED_ENV_VARIABLES**](#environment-variables-security)         | \[\]                                          | Additional list of secured environment variables to hide when calling linters.                                                                                                                             |
| [**SECURED_ENV_VARIABLES_DEFAULT**](#environment-variables-security) | MegaLinter & CI platforms sensitive variables | List of secured environment variables to hide when calling linters. [Default list](#environment-variables-security). This is not recommended to override this variable, use SECURED_ENV_VARIABLES          |
| **SHOW_ELAPSED_TIME**                                                | `false`                                       | Displays elapsed time in reports                                                                                                                                                                           |
| **SHOW_SKIPPED_LINTERS**                                             | `true`                                        | Displays all disabled linters mega-linter could have run                                                                                                                                                   |
| **SKIP_CLI_LINT_MODES**                                              | \[\]                                          | Comma-separated list of cli_lint_modes. To use if you want to skip linters with some CLI lint modes (ex: `file,project`). Available values: `file`,`cli_lint_mode`,`project`.                              |
| **TYPESCRIPT_DEFAULT_STYLE**                                         | `standard`                                    | Typescript default style to check/apply. `standard`,`prettier`                                                                                                                                             |
| **VALIDATE_ALL_CODEBASE**                                            | `true`                                        | Will parse the entire repository and find all files to validate across all types. **NOTE:** When set to `false`, only **new** or **edited** files will be parsed for validation.                           |

## Activation and deactivation

MegaLinter have all linters enabled by default, but allows to enable only some, or disable only some

- If `ENABLE` isn't set, all descriptors are activated by default. If set, all linters of listed descriptors will be activated by default
- If `ENABLE_LINTERS` is set, only listed linters will be processed
- If `DISABLE` is set, the linters in the listed descriptors will be skipped
- If `DISABLE_LINTERS` is set, the listed linters will be skipped
- If `DISABLE_ERRORS_LINTERS` is set, the listed linters will be run, but if errors are found, they will be considered as non blocking

Examples:

- Run all javascript and groovy linters except STANDARD javascript linter. DevSkim errors will be non-blocking

```yaml
ENABLE: JAVASCRIPT,GROOVY
DISABLE_LINTERS: JAVASCRIPT_STANDARD
DISABLE_ERRORS_LINTERS: REPOSITORY_DEVSKIM
```

- Run all linters except PHP linters (PHP_BUILTIN, PHP_PHPCS, PHP_PHPSTAN, PHP_PSALM)

```yaml
DISABLE: PHP
```

- Run all linters except PHP_PHPSTAN and PHP_PSALM linters

```yaml
DISABLE_LINTERS:
  - PHP_PHPSTAN
  - PHP_PSALM
```

## Filter linted files

If you need to lint only a folder or exclude some files from linting, you can use optional environment parameters `FILTER_REGEX_INCLUDE` and `FILTER_REGEX_EXCLUDE`
You can apply filters to a single linter by defining variable `<LINTER_KEY>_FILTER_REGEX_INCLUDE` and `<LINTER_KEY>_FILTER_REGEX_EXCLUDE`

Examples:

- Lint only src folder: `FILTER_REGEX_INCLUDE: (src/)`
- Don't lint files inside test and example folders: `FILTER_REGEX_EXCLUDE: (test/|examples/)`
- Don't lint javascript files inside test folder: `FILTER_REGEX_EXCLUDE: (test/.*\.js)`

Warning: not applicable with linters using CLI lint mode `project` ([see details](#cli-lint-mode))

## Apply fixes

Mega-linter is able to apply fixes provided by linters. To use this capability, you need 3 **env variables** defined at top level

- **APPLY_FIXES**: `all` to apply fixes of all linters, or a list of linter keys (ex: `JAVASCRIPT_ES`,`MARKDOWN_MARKDOWNLINT`)

Only for GitHub Action Workflow file if you use it:

- **APPLY_FIXES_EVENT**: `all`, `push`, `pull_request`, `none` _(use none in case of use of [Updated sources reporter](reporters/UpdatedSourcesReporter.md))_
- **APPLY_FIXES_MODE**: `commit` to create a new commit and push it on the same branch, or `pull_request` to create a new PR targeting the branch.

### Apply fixes issues

You may see **github permission errors**, or workflows not run on the new commit.

To solve these issues, you can apply one of the following solutions.

- Method 1: The most secured
  - [Create Fine Grained Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token#creating-a-fine-grained-personal-access-token), scoped only on your repository and then copy the PAT value
  - [Define environment secret variable](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-an-environment) named **PAT** on your repository, and paste the PAT value
  - Update your Github Actions Workflow to add the environment name

- Method 2: Easier, but any contributor with write access can see your Personal Access Token
  - [Create Classic Personal Access Token](https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/creating-a-personal-access-token#creating-a-token), then copy the PAT value
  - [Define secret variable](https://docs.github.com/en/free-pro-team@latest/actions/reference/encrypted-secrets#creating-encrypted-secrets-for-a-repository) named **PAT** on your repository, and paste the PAT value

### Notes

- You can use [**Updated sources reporter**](reporters/UpdatedSourcesReporter.md) if you don't want fixes to be automatically applied on git branch, but **download them in a zipped file** and manually **extract them in your project**
- If used, **APPLY_FIXES_EVENT** and **APPLY_FIXES_MODE** can not be defined in `.mega-linter.yml`config file, they must be set as environment variables
- If you use **APPLY_FIXES**, add the following line in your `.gitignore file`

```shell
megalinter-reports/
```

## Linter specific variables

See variables related to a single linter behavior in [linters documentations](supported-linters.md)

## Pre-commands

MegaLinter can run custom commands before running linters (for example, installing an plugin required by one of the linters you use)

Example in `.mega-linter.yml` config file

```yaml
PRE_COMMANDS:
  - command: npm install eslint-plugin-whatever
    cwd: "root"        # Will be run at the root of MegaLinter docker image
  - command: echo "pre-test command has been called"
    cwd: "workspace"   # Will be run at the root of the workspace (usually your repository root)
  - command: pip install flake8-cognitive-complexity
    venv: flake8 # Will be run within flake8 python virtualenv. There is one virtualenv per python-based linter, with the same name
```

## Post-commands

MegaLinter can run custom commands after running linters (for example, running additional tests)

Example in `.mega-linter.yml` config file

```yaml
POST_COMMANDS:
  - command: npm run test
    cwd: "workspace"   # Will be run at the root of the workspace (usually your repository root)
```

## Environment variables security

MegaLinter runs on a docker image and calls the linters via command line to gather their results.

If you run it from your **CI/CD pipelines**, the docker image may have **access to your environment variables, that can contain secrets** defined in CI/CD variables.

As it can be complicated to **trust** the authors of all the open-source linters, **MegaLinter removes variables from the environment used to call linters**.

Thanks to this feature, you only need to [**trust MegaLinter and its internal python dependencies**](https://github.com/oxsecurity/megalinter/blob/main/pyproject.toml), but there is **no need to trust all the linters that are used** !

You can add secured variables to the default list using configuration property **SECURED_ENV_VARIABLES** in .mega-linter.yml or in an environment variable (priority is given to ENV variables above `.mega-linter.yml` property).

SECURED_ENV_VARIABLES_DEFAULT contains:

- GITHUB_TOKEN
- PAT
- SYSTEM_ACCESSTOKEN
- GIT_AUTHORIZATION_BEARER
- CI_JOB_TOKEN
- GITLAB_ACCESS_TOKEN_MEGALINTER
- GITLAB_CUSTOM_CERTIFICATE
- WEBHOOK_REPORTER_BEARER_TOKEN
- NPM_TOKEN
- DOCKER_USERNAME
- DOCKER_PASSWORD
- CODECOV_TOKEN
- GCR_USERNAME
- GCR_PASSWORD
- SMTP_PASSWORD

Example of adding extra secured variables `.mega-linter.yml`:

```yaml
SECURED_ENV_VARIABLES:
  - MY_SECRET_TOKEN
  - ANOTHER_VAR_CONTAINING_SENSITIVE_DATA
  - OX_API_KEY
```

Example of adding extra secured variables in CI variables, so they can not be overridden in .mega-linter.yml:

```shell
SECURED_ENV_VARIABLES=MY_SECRET_TOKEN,ANOTHER_VAR_CONTAINING_SENSITIVE_DATA,OX_API_KEY
```

Notes:

- If you override SECURED_ENV_VARIABLES_DEFAULT, it replaces the default list, so it's better to only define SECURED_ENV_VARIABLES to add them to the default list !
- Environment variables are secured for each command line called (linters, plugins, sarif formatter...) except for [PRE_COMMANDS](#pre-commands) , as you might need secured values within their code.

## CLI lint mode

Each linter has a lint mode by default, visible in its MegaLinter documentation ([example](https://megalinter.io/latest/descriptors/repository_trivy/#how-the-linting-is-performed)):

- `list_of_files`: All files are sent in single call to the linter
- `project`: The linter is called from the root of the project, without specifying any file name
- `file`: The linter is called once by file (so the performances may not be very good)

You can override the CLI_LINT_MODE by using configuration variable for each linter (see [linters documentation](https://megalinter.io/supported-linters/))

- Linters with `file` default lint mode can not be overridden to `list_of_files`
- Linters with `project` default lint mode can not be overridden to `list_of_files` or `file`

Allowing `file` or `list_of_files` to be overridden to `project` is mostly for workarounds, for example with linters that have a problem to find their config file when the current folder isn't the repo root.

Special considerations:

- As list of files isn't sent to the linter command, linters using `project` lint mode don't take in account some variables like FILTER_REGEX_INCLUDE and FILTER_REGEX_EXCLUDE. For those linters, you must check their documentation to define ignore configuration as it's awaited by the linter (for example with a `.secretlintignore` file for secretlint)


<!-- configuration-section-end -->
