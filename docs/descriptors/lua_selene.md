---
title: selene configuration in MegaLinter
description: How to use selene (configure, ignore files, ignore errors, help & version documentations) to analyze LUA files
---
<!-- markdownlint-disable MD033 MD041 -->
<!-- @generated by .automation/build.py, please don't update manually -->
# selene
[![GitHub stars](https://img.shields.io/github/stars/Kampfkarren/selene?cacheSeconds=3600)](https://github.com/Kampfkarren/selene) [![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/Kampfkarren/selene?sort=semver)](https://github.com/Kampfkarren/selene/releases) [![GitHub last commit](https://img.shields.io/github/last-commit/Kampfkarren/selene)](https://github.com/Kampfkarren/selene/commits) [![GitHub commit activity](https://img.shields.io/github/commit-activity/y/Kampfkarren/selene)](https://github.com/Kampfkarren/selene/graphs/commit-activity/) [![GitHub contributors](https://img.shields.io/github/contributors/Kampfkarren/selene)](https://github.com/Kampfkarren/selene/graphs/contributors/)

**Selene** is a blazing-fast modern Lua linter written in Rust that provides comprehensive static analysis for Lua code. It offers extensive configurability and can be tailored to specific Lua environments like Roblox, World of Warcraft addons, or standard Lua.

**Key Features:**

- **Rust-powered performance** for extremely fast static analysis
- **Environment-specific configurations** for Roblox, WoW addons, and standard Lua
- **Comprehensive lint rules** covering code quality, style, and correctness
- **Custom rule creation** for project-specific requirements
- **TOML configuration files** for easy project setup and sharing
- **Detailed error messages** with context and suggestions for fixes
- **Multiple output formats** including JSON for tool integration
- **Incremental analysis** for fast checking of large codebases
- **Standard library definitions** for accurate global variable validation
- **Inline rule filtering** using comments to disable specific checks
- **Performance suggestions** to optimize Lua code execution

## selene documentation

- Version in MegaLinter: **0.29.0**
- Visit [Official Web Site](https://kampfkarren.github.io/selene/){target=_blank}
- See [How to configure selene rules](https://kampfkarren.github.io/selene/usage/configuration.html){target=_blank}
- See [How to disable selene rules in files](https://kampfkarren.github.io/selene/usage/filtering.html){target=_blank}
- See [Index of problems detected by selene](https://kampfkarren.github.io/selene/lints/index.html){target=_blank}

[![selene - GitHub](https://gh-card.dev/repos/Kampfkarren/selene.svg?fullname=)](https://github.com/Kampfkarren/selene){target=_blank}

## Configuration in MegaLinter

- Enable selene by adding `LUA_SELENE` in [ENABLE_LINTERS variable](https://megalinter.io/beta/configuration/#activation-and-deactivation)
- Disable selene by adding `LUA_SELENE` in [DISABLE_LINTERS variable](https://megalinter.io/beta/configuration/#activation-and-deactivation)

| Variable                               | Description                                                                                                                                                                                  | Default value                                   |
|----------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| LUA_SELENE_ARGUMENTS                   | User custom arguments to add in linter CLI call<br/>Ex: `-s --foo "bar"`                                                                                                                     |                                                 |
| LUA_SELENE_COMMAND_REMOVE_ARGUMENTS    | User custom arguments to remove from command line before calling the linter<br/>Ex: `-s --foo "bar"`                                                                                         |                                                 |
| LUA_SELENE_FILTER_REGEX_INCLUDE        | Custom regex including filter<br/>Ex: `(src\|lib)`                                                                                                                                           | Include every file                              |
| LUA_SELENE_FILTER_REGEX_EXCLUDE        | Custom regex excluding filter<br/>Ex: `(test\|examples)`                                                                                                                                     | Exclude no file                                 |
| LUA_SELENE_CLI_LINT_MODE               | Override default CLI lint mode<br/>- `file`: Calls the linter for each file<br/>- `project`: Call the linter from the root of the project                                                    | `file`                                          |
| LUA_SELENE_FILE_EXTENSIONS             | Allowed file extensions. `"*"` matches any extension, `""` matches empty extension. Empty list excludes all files<br/>Ex: `[".py", ""]`                                                      | `[".lua"]`                                      |
| LUA_SELENE_FILE_NAMES_REGEX            | File name regex filters. Regular expression list for filtering files by their base names using regex full match. Empty list includes all files<br/>Ex: `["Dockerfile(-.+)?", "Jenkinsfile"]` | Include every file                              |
| LUA_SELENE_PRE_COMMANDS                | List of bash commands to run before the linter                                                                                                                                               | None                                            |
| LUA_SELENE_POST_COMMANDS               | List of bash commands to run after the linter                                                                                                                                                | None                                            |
| LUA_SELENE_UNSECURED_ENV_VARIABLES     | List of env variables explicitly not filtered before calling LUA_SELENE and its pre/post commands                                                                                            | None                                            |
| LUA_SELENE_CONFIG_FILE                 | selene configuration file name</br>Use `LINTER_DEFAULT` to let the linter find it                                                                                                            | `selene.toml`                                   |
| LUA_SELENE_RULES_PATH                  | Path where to find linter configuration file                                                                                                                                                 | Workspace folder, then MegaLinter default rules |
| LUA_SELENE_DISABLE_ERRORS              | Run linter but consider errors as warnings                                                                                                                                                   | `false`                                         |
| LUA_SELENE_DISABLE_ERRORS_IF_LESS_THAN | Maximum number of errors allowed                                                                                                                                                             | `0`                                             |
| LUA_SELENE_CLI_EXECUTABLE              | Override CLI executable                                                                                                                                                                      | `['selene']`                                    |

## IDE Integration

Use selene in your favorite IDE to catch errors before MegaLinter !

|                                                                   <!-- -->                                                                   | IDE                                                  | Extension Name                                                                                                         |                                                                                    Install                                                                                     |
|:--------------------------------------------------------------------------------------------------------------------------------------------:|------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/default.ico" alt="" height="32px" class="megalinter-icon"></a> | neovim                                               | [['nvim-lint', 'none-ls']](['https://github.com/mfussenegger/nvim-lint', 'https://github.com/nvimtools/none-ls.nvim']) |                          [Visit Web Site](['https://github.com/mfussenegger/nvim-lint', 'https://github.com/nvimtools/none-ls.nvim']){target=_blank}                           |
| <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/sublime.ico" alt="" height="32px" class="megalinter-icon"></a> | [Sublime Text](https://www.sublimetext.com/)         | [SublimeLinter-contrib-selene](https://packagecontrol.io/packages/SublimeLinter-contrib-selene)                        |                                        [Visit Web Site](https://packagecontrol.io/packages/SublimeLinter-contrib-selene){target=_blank}                                        |
| <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/vscode.ico" alt="" height="32px" class="megalinter-icon"></a>  | [Visual Studio Code](https://code.visualstudio.com/) | [selene-vscode](https://marketplace.visualstudio.com/items?itemName=Kampfkarren.selene-vscode)                         | [![Install in VSCode](https://github.com/oxsecurity/megalinter/raw/main/docs/assets/images/btn_install_vscode.png)](vscode:extension/Kampfkarren.selene-vscode){target=_blank} |

## MegaLinter Flavors

This linter is available in the following flavors

|                                                                         <!-- -->                                                                         | Flavor                                               | Description               | Embedded linters |                                                                                                                                                                       Info |
|:--------------------------------------------------------------------------------------------------------------------------------------------------------:|:-----------------------------------------------------|:--------------------------|:----------------:|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/images/mega-linter-square.png" alt="" height="32px" class="megalinter-icon"></a> | [all](https://megalinter.io/beta/supported-linters/) | Default MegaLinter Flavor |       126        | ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter) |

## Behind the scenes

### How are identified applicable files

- File extensions: `.lua`

<!-- markdownlint-disable -->
<!-- /* cSpell:disable */ -->
### How the linting is performed

- selene is called one time by identified file (`file` CLI lint mode)

### Example calls

```shell
selene myfile.lua
```

```shell
selene --config chktexrc.toml myfile.lua
```


### Help content

```shell
selene 0.29.0

USAGE:
    selene [FLAGS] [OPTIONS] <files>...
    selene <SUBCOMMAND>

FLAGS:
        --allow-warnings    Pass when only warnings occur
    -h, --help              Prints help information
        --no-exclude
    -n, --no-summary        Suppress summary information
    -q, --quiet             Display only the necessary information. Equivalent to --display-style="quiet"
    -V, --version           Prints version information

OPTIONS:
        --color <color>                     [default: auto]  [possible values: Always, Auto, Never]
        --config <config>                  A toml file to configure the behavior of selene [default: selene.toml]
        --display-style <display-style>    Sets the display method [possible values: Json, Json2, Rich, Quiet]
        --num-threads <num-threads>        Number of threads to run on, default to the numbers of logical cores on your
                                           system [default: 4]
        --pattern <pattern>...             A glob to match files with to check

ARGS:
    <files>...

SUBCOMMANDS:
    capabilities           Prints the capabilities of the current build
    generate-roblox-std
    help                   Prints this message or the help of the given subcommand(s)
    update-roblox-std
    upgrade-std
    validate-config
```

### Installation on mega-linter Docker image

- Dockerfile commands :
```dockerfile
# Parent descriptor install
RUN wget --tries=5 https://www.lua.org/ftp/lua-5.3.5.tar.gz -O - -q | tar -xzf - \
    && cd lua-5.3.5 \
    && make linux \
    && make install \
    && cd .. && rm -r lua-5.3.5/

# Linter install
# renovate: datasource=crate depName=selene
ARG CARGO_SELENE_VERSION=0.29.0
```

- Cargo packages (Rust):
  - [selene@0.29.0](https://crates.io/crates/selene/0.29.0)
