---
title: Run MegaLinter without Docker (native mode, beta)
description: Run MegaLinter directly on your machine, without Docker, with the linters you choose
---
<!-- markdownlint-disable MD013 -->

# Native mode (without Docker)

> **Beta:** native mode is in beta. [Docker](install-docker.md) remains the default and the recommended way to run MegaLinter, especially on code you do not fully trust: linters (and the configuration files they load) can execute the code of the analyzed repository, and in Docker this happens inside a container.

MegaLinter can run directly on your machine, without a container engine and without downloading a multi-GB image. Only the linters you list are installed, so a run starts in seconds.

Supported platforms: Linux (x86-64 and ARM64), macOS (Intel and Apple Silicon), Windows with Git Bash, and WSL (Linux).

## Quick start

Requirements:

- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Windows: `winget install --id astral-sh.uv -e`, macOS: `brew install uv`)
- Node.js, to run `mega-linter-runner`
- Windows only: [Git for Windows](https://git-scm.com/download/win) (Git Bash), `winget install --id Git.Git -e`

1. List the linters allowed to run natively in your `.mega-linter.yml`:

    ```yaml
    NATIVE_LINTERS:
      - PYTHON_BLACK
      - JAVASCRIPT_ES
      - MARKDOWN_MARKDOWNLINT
    ```

2. Install them, then run:

    ```shell
    npx mega-linter-runner --install-linters --release beta
    npx mega-linter-runner --native --release beta
    ```

The linter keys are the ones used everywhere else in MegaLinter (`ENABLE_LINTERS`, `DISABLE_LINTERS`...). Each [linter page](supported-linters.md) has a "native mode" section with its key and the platforms it supports.

> **Note:** `--install-linters` installs linters for native mode. It is not `--install`, which sets up MegaLinter in your repository (configuration and CI files).

## NATIVE_LINTERS: explicit opt-in

Nothing runs natively unless it is listed in `NATIVE_LINTERS`. A linter that is activated by your configuration but not listed is skipped, so you can keep running a larger set of linters in Docker or in CI.

The special value `all` means every linter matching your configuration:

```yaml
NATIVE_LINTERS:
  - all
```

**Using `all` is discouraged.** It installs many linters, which is slow, and you must fully trust the security of every one of them. Prefer listing the linters you need.

## What is installed, and how

Linters are installed in `~/.megalinter` (change it with `MEGALINTER_HOME`), without administrator rights and without touching your system:

| Kind of linter             | Installation                                                                           |
|:---------------------------|:---------------------------------------------------------------------------------------|
| Python tools               | A virtual environment per linter, from pinned packages with hashes                     |
| Node.js tools              | A folder per linter, from a pinned lock file, without running install scripts          |
| Binaries and jars          | The official release asset, checked against a pinned sha256                            |
| Tools provided by the host | Not downloaded: MegaLinter looks for them on your `PATH` and shows how to install them |

Every download is verified. Upstream signatures and checksums (GitHub attestations, cosign, GPG, release checksum files) are checked when the pinned versions are generated in CI, and the installer only downloads files whose sha256 is pinned in the lock files shipped with MegaLinter. A file that does not match is refused.

## Language runtimes

Some linters need a runtime (Node.js, Java, .NET, Go, PowerShell, Dart, PHP...). MegaLinter uses the one installed on your machine when its version is suitable. Otherwise, `NATIVE_INSTALL_RUNTIMES` decides:

| Value           | Behavior                                                                                 |
|:----------------|:-----------------------------------------------------------------------------------------|
| `ask` (default) | Proposes to install the runtime in `~/.megalinter/runtimes` (interactive terminals only) |
| `auto`          | Installs it without asking                                                               |
| `never`         | Prints how to install it yourself                                                        |

Ruby, R and Rust have no portable, verifiable download: install them with your package manager.

## Security model

- Commands declared by the analyzed repository (`PRE_COMMANDS`, `POST_COMMANDS`), `PLUGINS` and remote `EXTENDS` are **ignored** in native mode, because they would run on your machine with your privileges. Use `--trust-repo-commands` (or `NATIVE_TRUST_REPO_COMMANDS=true` in the environment, never in `.mega-linter.yml`) only for a repository you fully trust.
- Linters only receive an allowlist of system environment variables, so the secrets of your machine (cloud credentials, tokens...) do not leak to them. Add more with `NATIVE_ENV_ALLOWLIST`.
- Native mode refuses to run when `MEGALINTER_HOME` belongs to another user or is writable by others.
- The `megalinter` Python package is installed by `mega-linter-runner` after checking its PyPI attestation: it must have been published by the release workflow of the MegaLinter repository.

## Commands

`mega-linter-runner` forwards to the `megalinter` command that you can also use directly (`uv tool install megalinter --pre`):

| Command                               | Purpose                                                      |
|:--------------------------------------|:-------------------------------------------------------------|
| `megalinter run`                      | Lint the current folder with the linters of `NATIVE_LINTERS` |
| `megalinter install-linters [KEY...]` | Install the given linters, or the ones of `NATIVE_LINTERS`   |
| `megalinter uninstall-linters KEY...` | Remove installed linters                                     |
| `megalinter list-linters`             | Show the native status of every linter                       |
| `megalinter doctor`                   | Check Git Bash, uv, runtimes and the install folder          |
| `megalinter cache prune`              | Empty the download cache                                     |

## Configuration

| Variable                      | Default         | Description                                                           |
|:------------------------------|:----------------|:----------------------------------------------------------------------|
| `NATIVE_LINTERS`              | empty           | Linters allowed to run natively (keys, or `all`)                      |
| `NATIVE_INSTALL_RUNTIMES`     | `ask`           | `ask`, `auto` or `never`                                              |
| `NATIVE_MISSING_LINTERS`      | `install`       | `install`, `skip` or `fail` for a listed linter that is not installed |
| `NATIVE_ENV_ALLOWLIST`        | empty           | Extra environment variables given to the linters                      |
| `NATIVE_IGNORE_HOST_RUNTIMES` | `false`         | Ignore the runtimes installed on the host                             |
| `NATIVE_OFFLINE`              | `false`         | Install only from the local download cache                            |
| `MEGALINTER_HOME`             | `~/.megalinter` | Where linters, runtimes and downloads are stored                      |

## Differences with Docker

- Results can differ from Docker: operating system, tool versions provided by the host, file system case sensitivity and path separators.
- Some linters are not available natively on every platform, with the reason shown in their documentation page and by `megalinter list-linters`. Use Docker for those.
- Flavors do not apply: you choose the linters one by one.
