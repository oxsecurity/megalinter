---
title: remark-lint configuration in MegaLinter
description: How to use remark-lint (configure, ignore files, ignore errors, help & version documentations) to analyze MARKDOWN files
---
<!-- markdownlint-disable MD033 MD041 -->
<!-- @generated by .automation/build.py, please don't update manually -->
# <a href="https://remark.js.org/" target="blank" title="Visit linter Web Site"><img src="https://raw.githubusercontent.com/remarkjs/remark-lint/02295bc/logo.svg?sanitize=true" alt="remark-lint" height="100px" class="megalinter-logo"></a>remark-lint
![disabled](https://shields.io/badge/-disabled-orange) [![GitHub stars](https://img.shields.io/github/stars/remarkjs/remark-lint?cacheSeconds=3600)](https://github.com/remarkjs/remark-lint) ![formatter](https://shields.io/badge/-format-yellow) [![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/remarkjs/remark-lint?sort=semver)](https://github.com/remarkjs/remark-lint/releases) [![GitHub last commit](https://img.shields.io/github/last-commit/remarkjs/remark-lint)](https://github.com/remarkjs/remark-lint/commits) [![GitHub commit activity](https://img.shields.io/github/commit-activity/y/remarkjs/remark-lint)](https://github.com/remarkjs/remark-lint/graphs/commit-activity/) [![GitHub contributors](https://img.shields.io/github/contributors/remarkjs/remark-lint)](https://github.com/remarkjs/remark-lint/graphs/contributors/)

_This linter has been disabled in this version_

_Disabled reason: Bug in remark-lint: <https://github.com/remarkjs/remark-lint/issues/322>_

**remark-lint** is a powerful plugin for the remark markdown processor that provides comprehensive linting and formatting capabilities for Markdown files. Built on the unified collective's remark ecosystem, it offers extensive rule-based validation with automatic fixing capabilities and a rich plugin architecture for customized Markdown processing workflows.

**Key Features:**

- **Unified Ecosystem**: Part of the remark/unified processing pipeline with access to a vast plugin ecosystem
- **Comprehensive Rule Set**: Extensive built-in rules for syntax consistency, formatting standards, and structural validation
- **Automatic Fixing**: Many rules can automatically repair Markdown issues, improving workflow efficiency
- **Plugin Architecture**: Highly extensible with 100+ community plugins for specialized linting requirements
- **AST-Based Processing**: Uses Abstract Syntax Tree parsing for deep, accurate Markdown analysis
- **Configurable Presets**: Pre-configured rule sets for common style guides and formatting conventions
- **Inline Control**: Marker-based comments for enabling/disabling rules within documents
- **Performance Optimized**: Efficient processing suitable for large documentation projects and automated pipelines
- **Standards Compliant**: Supports CommonMark and GitHub Flavored Markdown specifications with extension support

## remark-lint documentation

- Version in MegaLinter: **14.0.2**
- Visit [Official Web Site](https://remark.js.org/){target=_blank}
- See [How to configure remark-lint rules](https://github.com/remarkjs/remark-lint#configuring-remark-lint){target=_blank}
  - If custom `.remarkrc` config file isn't found, [.remarkrc](https://github.com/oxsecurity/megalinter/tree/main/TEMPLATES/.remarkrc){target=_blank} will be used
- See [How to disable remark-lint rules in files](https://github.com/remarkjs/remark-message-control#markers){target=_blank}
- See [Index of problems detected by remark-lint](https://github.com/remarkjs/remark-lint/blob/main/doc/rules.md#list-of-rules){target=_blank}

[![remark-lint - GitHub](https://gh-card.dev/repos/remarkjs/remark-lint.svg?fullname=)](https://github.com/remarkjs/remark-lint){target=_blank}

## Configuration in MegaLinter

- Enable remark-lint by adding `MARKDOWN_REMARK_LINT` in [ENABLE_LINTERS variable](https://megalinter.io/beta/configuration/#activation-and-deactivation)
- Disable remark-lint by adding `MARKDOWN_REMARK_LINT` in [DISABLE_LINTERS variable](https://megalinter.io/beta/configuration/#activation-and-deactivation)

- Enable **autofixes** by adding `MARKDOWN_REMARK_LINT` in [APPLY_FIXES variable](https://megalinter.io/beta/configuration/#apply-fixes)

| Variable                                         | Description                                                                                                                                                                                  | Default value                                   |
|--------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| MARKDOWN_DEFAULT_STYLE                           | For remark-lint to be active, MARKDOWN_DEFAULT_STYLE must be `remark-lint`                                                                                                                   | `markdownlint`                                  |
| MARKDOWN_REMARK_LINT_ARGUMENTS                   | User custom arguments to add in linter CLI call<br/>Ex: `-s --foo "bar"`                                                                                                                     |                                                 |
| MARKDOWN_REMARK_LINT_COMMAND_REMOVE_ARGUMENTS    | User custom arguments to remove from command line before calling the linter<br/>Ex: `-s --foo "bar"`                                                                                         |                                                 |
| MARKDOWN_REMARK_LINT_FILTER_REGEX_INCLUDE        | Custom regex including filter<br/>Ex: `(src\|lib)`                                                                                                                                           | Include every file                              |
| MARKDOWN_REMARK_LINT_FILTER_REGEX_EXCLUDE        | Custom regex excluding filter<br/>Ex: `(test\|examples)`                                                                                                                                     | Exclude no file                                 |
| MARKDOWN_REMARK_LINT_CLI_LINT_MODE               | Override default CLI lint mode<br/>- `file`: Calls the linter for each file<br/>- `project`: Call the linter from the root of the project                                                    | `file`                                          |
| MARKDOWN_REMARK_LINT_FILE_EXTENSIONS             | Allowed file extensions. `"*"` matches any extension, `""` matches empty extension. Empty list excludes all files<br/>Ex: `[".py", ""]`                                                      | `[".md"]`                                       |
| MARKDOWN_REMARK_LINT_FILE_NAMES_REGEX            | File name regex filters. Regular expression list for filtering files by their base names using regex full match. Empty list includes all files<br/>Ex: `["Dockerfile(-.+)?", "Jenkinsfile"]` | Include every file                              |
| MARKDOWN_REMARK_LINT_PRE_COMMANDS                | List of bash commands to run before the linter                                                                                                                                               | None                                            |
| MARKDOWN_REMARK_LINT_POST_COMMANDS               | List of bash commands to run after the linter                                                                                                                                                | None                                            |
| MARKDOWN_REMARK_LINT_UNSECURED_ENV_VARIABLES     | List of env variables explicitly not filtered before calling MARKDOWN_REMARK_LINT and its pre/post commands                                                                                  | None                                            |
| MARKDOWN_REMARK_LINT_CONFIG_FILE                 | remark-lint configuration file name</br>Use `LINTER_DEFAULT` to let the linter find it                                                                                                       | `.remarkrc`                                     |
| MARKDOWN_REMARK_LINT_RULES_PATH                  | Path where to find linter configuration file                                                                                                                                                 | Workspace folder, then MegaLinter default rules |
| MARKDOWN_REMARK_LINT_DISABLE_ERRORS              | Run linter but consider errors as warnings                                                                                                                                                   | `true`                                          |
| MARKDOWN_REMARK_LINT_DISABLE_ERRORS_IF_LESS_THAN | Maximum number of errors allowed                                                                                                                                                             | `0`                                             |
| MARKDOWN_REMARK_LINT_CLI_EXECUTABLE              | Override CLI executable                                                                                                                                                                      | `['remark']`                                    |

## IDE Integration

Use remark-lint in your favorite IDE to catch errors before MegaLinter !

|                                                                   <!-- -->                                                                   | IDE                                                  | Extension Name                                                                                            |                                                Install                                                |
|:--------------------------------------------------------------------------------------------------------------------------------------------:|------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------:|
| <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/sublime.ico" alt="" height="32px" class="megalinter-icon"></a> | [Sublime Text](https://www.sublimetext.com/)         | [SublimeLinter-contrib-remark-lint](https://packagecontrol.io/packages/SublimeLinter-contrib-remark-lint) | [Visit Web Site](https://packagecontrol.io/packages/SublimeLinter-contrib-remark-lint){target=_blank} |
|   <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/vim.ico" alt="" height="32px" class="megalinter-icon"></a>   | [vim](https://www.vim.org/)                          | [ale](https://github.com/w0rp/ale)                                                                        |                     [Visit Web Site](https://github.com/w0rp/ale){target=_blank}                      |
| <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/vscode.ico" alt="" height="32px" class="megalinter-icon"></a>  | [Visual Studio Code](https://code.visualstudio.com/) | [vscode-remark-lint](https://github.com/drewbourne/vscode-remark-lint)                                    |           [Visit Web Site](https://github.com/drewbourne/vscode-remark-lint){target=_blank}           |

## MegaLinter Flavors

This linter is available in the following flavors

|                                                                         <!-- -->                                                                         | Flavor                                               | Description               | Embedded linters |                                                                                                                                                                       Info |
|:--------------------------------------------------------------------------------------------------------------------------------------------------------:|:-----------------------------------------------------|:--------------------------|:----------------:|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/images/mega-linter-square.png" alt="" height="32px" class="megalinter-icon"></a> | [all](https://megalinter.io/beta/supported-linters/) | Default MegaLinter Flavor |       126        | ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter) |

## Behind the scenes

### How are identified applicable files

- File extensions: `.md`

<!-- markdownlint-disable -->
<!-- /* cSpell:disable */ -->
### How the linting is performed

- remark-lint is called one time by identified file (`file` CLI lint mode)

### Example calls

```shell
remark --frail myfile.md
```

```shell
remark --frail --rc-path .remarkrc myfile.md
```

```shell
remark --frail -o --rc-path .remarkrc myfile.md
```


### Help content

```shell
Usage: remark [options] [path | glob ...]

  Command line interface to inspect and change markdown files with remark

Options:

  -h  --help                              output usage information
  -v  --version                           output version number
  -o  --output [path]                     specify output location
  -r  --rc-path <path>                    specify configuration file
  -i  --ignore-path <path>                specify ignore file
  -s  --setting <settings>                specify settings
  -e  --ext <extensions>                  specify extensions
  -u  --use <plugins>                     use plugins
  -w  --watch                             watch for changes and reprocess
  -q  --quiet                             output only warnings and errors
  -S  --silent                            output only errors
  -f  --frail                             exit with 1 on warnings
  -t  --tree                              specify input and output as syntax tree
      --report <reporter>                 specify reporter
      --file-path <path>                  specify path to process as
      --ignore-path-resolve-from dir|cwd  resolve patterns in `ignore-path` from its directory or cwd
      --ignore-pattern <globs>            specify ignore patterns
      --silently-ignore                   do not fail when given ignored files
      --tree-in                           specify input as syntax tree
      --tree-out                          output syntax tree
      --inspect                           output formatted syntax tree
      --[no-]stdout                       specify writing to stdout (on by default)
      --[no-]color                        specify color in report (on by default)
      --[no-]config                       search for configuration files (on by default)
      --[no-]ignore                       search for ignore files (on by default)

Examples:

  # Process `input.md`
  $ remark input.md -o output.md

  # Pipe
  $ remark < input.md > output.md

  # Rewrite all applicable files
  $ remark . -o
```

### Installation on mega-linter Docker image

- Dockerfile commands :
```dockerfile
# renovate: datasource=npm depName=remark-cli
ARG NPM_REMARK_CLI_VERSION=12.0.1
# renovate: datasource=npm depName=remark-preset-lint-recommended
ARG NPM_REMARK_PRESET_LINT_RECOMMENDED_VERSION=7.0.1
```

- NPM packages (node.js):
  - [remark-cli](https://www.npmjs.com/package/remark-cli)
  - [remark-preset-lint-recommended](https://www.npmjs.com/package/remark-preset-lint-recommended)
