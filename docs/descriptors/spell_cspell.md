---
title: cspell configuration in MegaLinter
description: How to use cspell (configure, ignore files, ignore errors, help & version documentations) to analyze SPELL files
---
<!-- markdownlint-disable MD033 MD041 -->
<!-- @generated by .automation/build.py, please don't update manually -->
# <a href="https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell" target="blank" title="Visit linter Web Site"><img src="https://streetsidesoftware.gallerycdn.vsassets.io/extensions/streetsidesoftware/code-spell-checker/1.9.2/1601218033318/Microsoft.VisualStudio.Services.Icons.Default" alt="cspell" height="100px" class="megalinter-logo"></a>cspell
[![GitHub stars](https://img.shields.io/github/stars/streetsidesoftware/cspell?cacheSeconds=3600)](https://github.com/streetsidesoftware/cspell) [![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/streetsidesoftware/cspell?sort=semver)](https://github.com/streetsidesoftware/cspell/releases) [![GitHub last commit](https://img.shields.io/github/last-commit/streetsidesoftware/cspell)](https://github.com/streetsidesoftware/cspell/commits) [![GitHub commit activity](https://img.shields.io/github/commit-activity/y/streetsidesoftware/cspell)](https://github.com/streetsidesoftware/cspell/graphs/commit-activity/) [![GitHub contributors](https://img.shields.io/github/contributors/streetsidesoftware/cspell)](https://github.com/streetsidesoftware/cspell/graphs/contributors/)

MegaLinter generates content of a `.cspell.json` config file at the end of its TextReporter artifact

Copy it at the root of your repository, read it, remove real spelling errors (after have corrected them in the source), and you're good to go !

If you do not want cspell to analyze the files names, define `SPELL_CSPELL_ANALYZE_FILE_NAMES` to `false`

## cspell documentation

- Version in MegaLinter: **8.2.3**
- Visit [Official Web Site](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell#readme){target=_blank}
- See [How to configure cspell rules](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell#customization){target=_blank}
- See [How to disable cspell rules in files](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell#enable--disable-checking-sections-of-code){target=_blank}

[![cspell - GitHub](https://gh-card.dev/repos/streetsidesoftware/cspell.svg?fullname=)](https://github.com/streetsidesoftware/cspell){target=_blank}

## Configuration in MegaLinter

- Enable cspell by adding `SPELL_CSPELL` in [ENABLE_LINTERS variable](https://megalinter.io/beta/configuration/#activation-and-deactivation)
- Disable cspell by adding `SPELL_CSPELL` in [DISABLE_LINTERS variable](https://megalinter.io/beta/configuration/#activation-and-deactivation)

| Variable                                 | Description                                                                                                                                                                                                         | Default value                                   |
|------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| SPELL_CSPELL_ANALYZE_FILE_NAMES          | If set to `true`, MegaLinter will also send file names to cspell for analysis. Disable by defining `SPELL_CSPELL_ANALYZE_FILE_NAMES` to `false`                                                                     | `true`                                          |
| SPELL_CSPELL_ARGUMENTS                   | User custom arguments to add in linter CLI call<br/>Ex: `-s --foo "bar"`                                                                                                                                            |                                                 |
| SPELL_CSPELL_COMMAND_REMOVE_ARGUMENTS    | User custom arguments to remove from command line before calling the linter<br/>Ex: `-s --foo "bar"`                                                                                                                |                                                 |
| SPELL_CSPELL_FILTER_REGEX_INCLUDE        | Custom regex including filter<br/>Ex: `(src\|lib)`                                                                                                                                                                  | Include every file                              |
| SPELL_CSPELL_FILTER_REGEX_EXCLUDE        | Custom regex excluding filter<br/>Ex: `(test\|examples)`                                                                                                                                                            | Exclude no file                                 |
| SPELL_CSPELL_CLI_LINT_MODE               | Override default CLI lint mode<br/>- `file`: Calls the linter for each file<br/>- `list_of_files`: Call the linter with the list of files as argument<br/>- `project`: Call the linter from the root of the project | `list_of_files`                                 |
| SPELL_CSPELL_FILE_EXTENSIONS             | Allowed file extensions. `"*"` matches any extension, `""` matches empty extension. Empty list excludes all files<br/>Ex: `[".py", ""]`                                                                             | Exclude every file                              |
| SPELL_CSPELL_FILE_NAMES_REGEX            | File name regex filters. Regular expression list for filtering files by their base names using regex full match. Empty list includes all files<br/>Ex: `["Dockerfile(-.+)?", "Jenkinsfile"]`                        | Include every file                              |
| SPELL_CSPELL_PRE_COMMANDS                | List of bash commands to run before the linter                                                                                                                                                                      | None                                            |
| SPELL_CSPELL_POST_COMMANDS               | List of bash commands to run after the linter                                                                                                                                                                       | None                                            |
| SPELL_CSPELL_UNSECURED_ENV_VARIABLES     | List of env variables explicitly not filtered before calling SPELL_CSPELL and its pre/post commands                                                                                                                 | None                                            |
| SPELL_CSPELL_CONFIG_FILE                 | cspell configuration file name</br>Use `LINTER_DEFAULT` to let the linter find it                                                                                                                                   | `.cspell.json`                                  |
| SPELL_CSPELL_RULES_PATH                  | Path where to find linter configuration file                                                                                                                                                                        | Workspace folder, then MegaLinter default rules |
| SPELL_CSPELL_DISABLE_ERRORS              | Run linter but consider errors as warnings                                                                                                                                                                          | `false`                                         |
| SPELL_CSPELL_DISABLE_ERRORS_IF_LESS_THAN | Maximum number of errors allowed                                                                                                                                                                                    | `0`                                             |
| SPELL_CSPELL_CLI_EXECUTABLE              | Override CLI executable                                                                                                                                                                                             | `['cspell']`                                    |

## IDE Integration

Use cspell in your favorite IDE to catch errors before MegaLinter !

|                                                                  <!-- -->                                                                   | IDE                                                  | Extension Name                                                                                                  |                                                                                          Install                                                                                           |
|:-------------------------------------------------------------------------------------------------------------------------------------------:|------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/vscode.ico" alt="" height="32px" class="megalinter-icon"></a> | [Visual Studio Code](https://code.visualstudio.com/) | [Code Spell Checker](https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker) | [![Install in VSCode](https://github.com/oxsecurity/megalinter/raw/main/docs/assets/images/btn_install_vscode.png)](vscode:extension/streetsidesoftware.code-spell-checker){target=_blank} |

## MegaLinter Flavours

This linter is available in the following flavours

|                                                                         <!-- -->                                                                         | Flavor                                                             | Description                                              | Embedded linters |                                                                                                                                                                                                   Info |
|:--------------------------------------------------------------------------------------------------------------------------------------------------------:|:-------------------------------------------------------------------|:---------------------------------------------------------|:----------------:|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/images/mega-linter-square.png" alt="" height="32px" class="megalinter-icon"></a> | [all](https://megalinter.io/beta/supported-linters/)               | Default MegaLinter Flavor                                |       121        |                             ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter) |
|        <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/c_cpp.ico" alt="" height="32px" class="megalinter-icon"></a>        | [c_cpp](https://megalinter.io/beta/flavors/c_cpp/)                 | Optimized for pure C/C++ projects                        |        55        |                 ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-c_cpp/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-c_cpp) |
|       <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/cupcake.ico" alt="" height="32px" class="megalinter-icon"></a>       | [cupcake](https://megalinter.io/beta/flavors/cupcake/)             | MegaLinter for the most commonly used languages          |        85        |             ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-cupcake/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-cupcake) |
|    <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/documentation.ico" alt="" height="32px" class="megalinter-icon"></a>    | [documentation](https://megalinter.io/beta/flavors/documentation/) | MegaLinter for documentation projects                    |        51        | ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-documentation/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-documentation) |
|       <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/dotnet.ico" alt="" height="32px" class="megalinter-icon"></a>        | [dotnet](https://megalinter.io/beta/flavors/dotnet/)               | Optimized for C, C++, C# or VB based projects            |        64        |               ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-dotnet/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-dotnet) |
|      <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/dotnetweb.ico" alt="" height="32px" class="megalinter-icon"></a>      | [dotnetweb](https://megalinter.io/beta/flavors/dotnetweb/)         | Optimized for C, C++, C# or VB based projects with JS/TS |        73        |         ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-dotnetweb/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-dotnetweb) |
|         <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/go.ico" alt="" height="32px" class="megalinter-icon"></a>          | [go](https://megalinter.io/beta/flavors/go/)                       | Optimized for GO based projects                          |        53        |                       ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-go/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-go) |
|        <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/java.ico" alt="" height="32px" class="megalinter-icon"></a>         | [java](https://megalinter.io/beta/flavors/java/)                   | Optimized for JAVA based projects                        |        55        |                   ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-java/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-java) |
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

- If this linter is active, all files linted by all other active linters will be linted

<!-- markdownlint-disable -->
<!-- /* cSpell:disable */ -->
### How the linting is performed

- cspell is called once with the list of files as arguments (`list_of_files` CLI lint mode)

### Example calls

```shell
cspell myfile.any
```

```shell
cspell -c cspell.json myfile.any
```


### Help content

```shell
Usage: cspell [options] [command]

Spelling Checker for Code

Options:
  -V, --version                         output the version number
  -h, --help                            display help for command

Commands:
  lint [options] [globs...]             Check spelling
  trace [options] [words...]            Trace words -- Search for words in the
                                        configuration and dictionaries.
  check [options] <files...>            Spell check file(s) and display the
                                        result. The full file is displayed in
                                        color.
  suggestions|sug [options] [words...]  Spelling Suggestions for words.
  link                                  Link dictionaries and other settings to
                                        the cspell global config.
  help [command]                        display help for command
```

### Installation on mega-linter Docker image

- NPM packages (node.js):
  - [cspell](https://www.npmjs.com/package/cspell)