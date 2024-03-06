---
title: SNAKEMAKE linters in MegaLinter
description: snakemake, snakefmt are available to analyze SNAKEMAKE files in MegaLinter
---
<!-- markdownlint-disable MD003 MD020 MD033 MD041 -->
<!-- @generated by .automation/build.py, please don't update manually -->
<!-- Instead, update descriptor file at https://github.com/oxsecurity/megalinter/tree/main/megalinter/descriptors/snakemake.yml -->
# SNAKEMAKE

## Linters

| Linter                                                                                  | Additional                                                                                                                                                                               |
|-----------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [**snakemake**](snakemake_snakemake.md)<br/>[_SNAKEMAKE_LINT_](snakemake_snakemake.md)  | [![GitHub stars](https://img.shields.io/github/stars/snakemake/snakemake?cacheSeconds=3600)](https://github.com/snakemake/snakemake)                                                     |
| [**snakefmt**](snakemake_snakefmt.md)<br/>[_SNAKEMAKE_SNAKEFMT_](snakemake_snakefmt.md) | [![GitHub stars](https://img.shields.io/github/stars/snakemake/snakefmt?cacheSeconds=3600)](https://github.com/snakemake/snakefmt) ![formatter](https://shields.io/badge/-format-yellow) |

## Linted files

- File extensions:
  - `.smk`

- File names:
  - `Snakefile`

## Configuration in MegaLinter

| Variable                       | Description                   | Default value |
|--------------------------------|-------------------------------|---------------|
| SNAKEMAKE_FILTER_REGEX_INCLUDE | Custom regex including filter |               |
| SNAKEMAKE_FILTER_REGEX_EXCLUDE | Custom regex excluding filter |               |
