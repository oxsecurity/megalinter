---
title: RUBY linters in MegaLinter
description: rubocop is available to analyze RUBY files in MegaLinter
---
<!-- markdownlint-disable MD003 MD020 MD033 MD041 -->
<!-- @generated by .automation/build.py, please don't update manually -->
<!-- Instead, update descriptor file at https://github.com/oxsecurity/megalinter/tree/main/megalinter/descriptors/ruby.yml -->
# RUBY

## Linters

| Linter                                                               | Additional                                                                                                                                                                             |
|----------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [**rubocop**](ruby_rubocop.md)<br/>[_RUBY_RUBOCOP_](ruby_rubocop.md) | [![GitHub stars](https://img.shields.io/github/stars/rubocop-hq/rubocop?cacheSeconds=3600)](https://github.com/rubocop-hq/rubocop) ![autofix](https://shields.io/badge/-autofix-green) |

## Linted files

- File extensions:
  - `.rb`

## Configuration in MegaLinter

| Variable                  | Description                   | Default value |
|---------------------------|-------------------------------|---------------|
| RUBY_FILTER_REGEX_INCLUDE | Custom regex including filter |               |
| RUBY_FILTER_REGEX_EXCLUDE | Custom regex excluding filter |               |
