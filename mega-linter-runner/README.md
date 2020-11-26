<!-- markdownlint-disable MD013 MD033 MD041 -->

# Mega-Linter Runner

[![Version](https://img.shields.io/npm/v/npm-groovy-lint.svg)](https://npmjs.org/package/npm-groovy-lint)
[![Docker Pulls](https://img.shields.io/docker/pulls/nvuillam/mega-linter)](https://hub.docker.com/r/nvuillam/mega-linter)
[![Mega-Linter](https://github.com/nvuillam/mega-linter/workflows/Mega-Linter/badge.svg?branch=master)](https://nvuillam.github.io/mega-linter)
[![codecov](https://codecov.io/gh/nvuillam/mega-linter/branch/master/graph/badge.svg)](https://codecov.io/gh/nvuillam/mega-linter)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

<!-- welcome-phrase-start -->
**Mega-Linter** analyzes [**37 languages**](#languages), [**15 formats**](#formats), [**16 tooling formats**](#tooling-formats) , [**copy-pastes**](#other) and [**spell**](#other) in your repository sources, generate [**reports in several formats**](#reports), and can even [**apply formatting and auto-fixes**](#apply-fixes) with **auto-generated commit or PR**, to ensure all your projects are clean, whatever IDE/toolbox are used by their developers !
<!-- welcome-phrase-end -->

<!-- online-doc-start -->
See [**Mega-Linter Online Documentation Web Site**](https://nvuillam.github.io/mega-linter/)
<!-- online-doc-end -->

## Mega-Linter client

This package allows to run Mega-Linter locally before running it in your CD/CI workflow, or simply to locally apply reformattings and fixes without having to install up to date linters for your files

## Installation

### Pre-requisites

You need to have [NodeJS](https://nodejs.org/en/) and [Docker](https://www.docker.com/) installed on your computer to run Mega-Linter locally with Mega-Linter Runner

### Global installation

```shell
npm install mega-linter-runner -g
```

### Local installation

```shell
npm install mega-linter-runner --save-dev
```

## Usage

```shell
mega-linter-runner [OPTIONS]
```

The options are only related to mega-linter-runner. For Mega-Linter options, please use a `.mega-linter.yml` [configuration file](#configuration)

| Option             | Description                                               |
|--------------------|-----------------------------------------------------------|
| `-p` `--path`      | Directory containing the files to lint (default: current directory)    |
| `--fix`            | Automatically apply formatting and fixes in your files    |
| `-r``--release`    | Allos to override Mega-Linter version used (default: v4 stable)  |
| `-h` `--help`      | Show mega-linter-runner help    |
| `-v` `--version`   | Show mega-linter-runner version    |

_You can also use `npx mega-linter-runner` if you do not want to install the package_

## Configuration

Default configuration is ready out of the box

You can define a [.mega-linter.yml](https://nvuillam.github.io/mega-linter/#configuration) configuration file at the root of your repository to customize or deactivate the included linters

## Linters

<!-- linters-table-start -->

<!-- linters-table-end -->