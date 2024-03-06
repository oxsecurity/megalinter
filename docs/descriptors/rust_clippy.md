---
title: clippy configuration in MegaLinter
description: How to use clippy (configure, ignore files, ignore errors, help & version documentations) to analyze RUST files
---
<!-- markdownlint-disable MD033 MD041 -->
<!-- @generated by .automation/build.py, please don't update manually -->
# clippy
[![GitHub stars](https://img.shields.io/github/stars/rust-lang/rust-clippy?cacheSeconds=3600)](https://github.com/rust-lang/rust-clippy) [![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/rust-lang/rust-clippy?sort=semver)](https://github.com/rust-lang/rust-clippy/releases) [![GitHub last commit](https://img.shields.io/github/last-commit/rust-lang/rust-clippy)](https://github.com/rust-lang/rust-clippy/commits) [![GitHub commit activity](https://img.shields.io/github/commit-activity/y/rust-lang/rust-clippy)](https://github.com/rust-lang/rust-clippy/graphs/commit-activity/) [![GitHub contributors](https://img.shields.io/github/contributors/rust-lang/rust-clippy)](https://github.com/rust-lang/rust-clippy/graphs/contributors/)

## clippy documentation

- Version in MegaLinter: **0.1.76**
- Visit [Official Web Site](https://github.com/rust-lang/rust-clippy#readme){target=_blank}
- See [How to configure clippy rules](https://github.com/rust-lang/rust-clippy#configuration){target=_blank}
- See [How to disable clippy rules in files](https://github.com/rust-lang/rust-clippy#allowingdenying-lints){target=_blank}
- See [Index of problems detected by clippy](https://rust-lang.github.io/rust-clippy/stable/index.html){target=_blank}

[![rust-clippy - GitHub](https://gh-card.dev/repos/rust-lang/rust-clippy.svg?fullname=)](https://github.com/rust-lang/rust-clippy){target=_blank}

## Configuration in MegaLinter

- Enable clippy by adding `RUST_CLIPPY` in [ENABLE_LINTERS variable](https://megalinter.io/beta/configuration/#activation-and-deactivation)
- Disable clippy by adding `RUST_CLIPPY` in [DISABLE_LINTERS variable](https://megalinter.io/beta/configuration/#activation-and-deactivation)

| Variable                                | Description                                                                                                                                                                                  | Default value                                   |
|-----------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| RUST_CLIPPY_ARGUMENTS                   | User custom arguments to add in linter CLI call<br/>Ex: `-s --foo "bar"`                                                                                                                     |                                                 |
| RUST_CLIPPY_COMMAND_REMOVE_ARGUMENTS    | User custom arguments to remove from command line before calling the linter<br/>Ex: `-s --foo "bar"`                                                                                         |                                                 |
| RUST_CLIPPY_FILE_EXTENSIONS             | Allowed file extensions. `"*"` matches any extension, `""` matches empty extension. Empty list excludes all files<br/>Ex: `[".py", ""]`                                                      | `[".rs"]`                                       |
| RUST_CLIPPY_FILE_NAMES_REGEX            | File name regex filters. Regular expression list for filtering files by their base names using regex full match. Empty list includes all files<br/>Ex: `["Dockerfile(-.+)?", "Jenkinsfile"]` | Include every file                              |
| RUST_CLIPPY_PRE_COMMANDS                | List of bash commands to run before the linter                                                                                                                                               | None                                            |
| RUST_CLIPPY_POST_COMMANDS               | List of bash commands to run after the linter                                                                                                                                                | None                                            |
| RUST_CLIPPY_UNSECURED_ENV_VARIABLES     | List of env variables explicitly not filtered before calling RUST_CLIPPY and its pre/post commands                                                                                           | None                                            |
| RUST_CLIPPY_CONFIG_FILE                 | clippy configuration file name</br>Use `LINTER_DEFAULT` to let the linter find it                                                                                                            | `.clippy.toml`                                  |
| RUST_CLIPPY_RULES_PATH                  | Path where to find linter configuration file                                                                                                                                                 | Workspace folder, then MegaLinter default rules |
| RUST_CLIPPY_DISABLE_ERRORS              | Run linter but consider errors as warnings                                                                                                                                                   | `false`                                         |
| RUST_CLIPPY_DISABLE_ERRORS_IF_LESS_THAN | Maximum number of errors allowed                                                                                                                                                             | `0`                                             |
| RUST_CLIPPY_CLI_EXECUTABLE              | Override CLI executable                                                                                                                                                                      | `['cargo-clippy']`                              |

## IDE Integration

Use clippy in your favorite IDE to catch errors before MegaLinter !

|                                                                 <!-- -->                                                                  | IDE                      | Extension Name                                              |                                   Install                                   |
|:-----------------------------------------------------------------------------------------------------------------------------------------:|--------------------------|-------------------------------------------------------------|:---------------------------------------------------------------------------:|
| <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/atom.ico" alt="" height="32px" class="megalinter-icon"></a> | [Atom](https://atom.io/) | [Atom IDE Rest](https://github.com/rust-lang/atom-ide-rust) | [Visit Web Site](https://github.com/rust-lang/atom-ide-rust){target=_blank} |

## MegaLinter Flavours

This linter is available in the following flavours

|                                                                         <!-- -->                                                                         | Flavor                                                 | Description                                     | Embedded linters |                                                                                                                                                                                       Info |
|:--------------------------------------------------------------------------------------------------------------------------------------------------------:|:-------------------------------------------------------|:------------------------------------------------|:----------------:|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/images/mega-linter-square.png" alt="" height="32px" class="megalinter-icon"></a> | [all](https://megalinter.io/beta/supported-linters/)   | Default MegaLinter Flavor                       |       121        |                 ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter) |
|       <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/cupcake.ico" alt="" height="32px" class="megalinter-icon"></a>       | [cupcake](https://megalinter.io/beta/flavors/cupcake/) | MegaLinter for the most commonly used languages |        84        | ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-cupcake/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-cupcake) |
|        <img src="https://github.com/oxsecurity/megalinter/raw/main/docs/assets/icons/rust.ico" alt="" height="32px" class="megalinter-icon"></a>         | [rust](https://megalinter.io/beta/flavors/rust/)       | Optimized for RUST based projects               |        51        |       ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/oxsecurity/megalinter-rust/beta) ![Docker Pulls](https://img.shields.io/docker/pulls/oxsecurity/megalinter-rust) |

## Behind the scenes

### How are identified applicable files

- File extensions: `.rs`

<!-- markdownlint-disable -->
<!-- /* cSpell:disable */ -->
### How the linting is performed

clippy is called once on the whole project directory (`project` CLI lint mode)

- filtering can not be done using MegaLinter configuration variables,it must be done using clippy configuration or ignore file (if existing)
- `VALIDATE_ALL_CODEBASE: false` doesn't make clippy analyze only updated files

### Example calls

```shell
cargo-clippy
```


### Help content

```shell
Checks a package to catch common mistakes and improve your Rust code.

Usage:
    cargo clippy [OPTIONS] [--] [<ARGS>...]

Common options:
    --no-deps                Run Clippy only on the given crate, without linting the dependencies
    --fix                    Automatically apply lint suggestions. This flag implies --no-deps and --all-targets
    -h, --help               Print this message
    -V, --version            Print version info and exit
    --explain [LINT]         Print the documentation for a given lint

See all options with cargo check --help.

Allowing / Denying lints

To allow or deny a lint from the command line you can use cargo clippy -- with:

    -W / --warn [LINT]       Set lint warnings
    -A / --allow [LINT]      Set lint allowed
    -D / --deny [LINT]       Set lint denied
    -F / --forbid [LINT]     Set lint forbidden

You can use tool lints to allow or deny lints from your code, e.g.:

    #[allow(clippy::needless_lifetimes)]

```

### Installation on mega-linter Docker image
