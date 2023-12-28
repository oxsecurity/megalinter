---
title: SALESFORCE linters in MegaLinter
description: sfdx-scanner-apex, sfdx-scanner-aura, sfdx-scanner-lwc, lightning-flow-scanner are available to analyze SALESFORCE files in MegaLinter
---
<!-- markdownlint-disable MD003 MD020 MD033 MD041 -->
<!-- @generated by .automation/build.py, please don't update manually -->
<!-- Instead, update descriptor file at https://github.com/oxsecurity/megalinter/tree/main/megalinter/descriptors/salesforce.yml -->
# SALESFORCE

## Linters

| Linter                                                                                                                                             | Additional                                                                                                                                                                                         |
|----------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [**sfdx-scanner-apex**](salesforce_sfdx_scanner_apex.md)<br/>[_SALESFORCE_SFDX_SCANNER_APEX_](salesforce_sfdx_scanner_apex.md)                     | [![GitHub stars](https://img.shields.io/github/stars/forcedotcom/sfdx-scanner?cacheSeconds=3600)](https://github.com/forcedotcom/sfdx-scanner)                                                     |
| [**sfdx-scanner-aura**](salesforce_sfdx_scanner_aura.md)<br/>[_SALESFORCE_SFDX_SCANNER_AURA_](salesforce_sfdx_scanner_aura.md)                     | [![GitHub stars](https://img.shields.io/github/stars/forcedotcom/sfdx-scanner?cacheSeconds=3600)](https://github.com/forcedotcom/sfdx-scanner)                                                     |
| [**sfdx-scanner-lwc**](salesforce_sfdx_scanner_lwc.md)<br/>[_SALESFORCE_SFDX_SCANNER_LWC_](salesforce_sfdx_scanner_lwc.md)                         | [![GitHub stars](https://img.shields.io/github/stars/forcedotcom/sfdx-scanner?cacheSeconds=3600)](https://github.com/forcedotcom/sfdx-scanner)                                                     |
| [**lightning-flow-scanner**](salesforce_lightning_flow_scanner.md)<br/>[_SALESFORCE_LIGHTNING_FLOW_SCANNER_](salesforce_lightning_flow_scanner.md) | [![GitHub stars](https://img.shields.io/github/stars/Lightning-Flow-Scanner/lightning-flow-scanner-sfdx?cacheSeconds=3600)](https://github.com/Lightning-Flow-Scanner/lightning-flow-scanner-sfdx) |

## Linted files

## Configuration in MegaLinter

| Variable                        | Description                   | Default value |
|---------------------------------|-------------------------------|---------------|
| SALESFORCE_FILTER_REGEX_INCLUDE | Custom regex including filter |               |
| SALESFORCE_FILTER_REGEX_EXCLUDE | Custom regex excluding filter |               |


## Behind the scenes

### Installation

- Dockerfile commands :
```dockerfile
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk
ENV PATH="$JAVA_HOME/bin:${PATH}"
RUN sf plugins install @salesforce/plugin-packaging \
    && echo y|sfdx plugins:install sfdx-hardis \
    && npm cache clean --force || true \
    && rm -rf /root/.npm/_cacache

```

- APK packages (Linux):
  - [openjdk17](https://pkgs.alpinelinux.org/packages?branch=edge&name=openjdk17)
- NPM packages (node.js):
  - [@salesforce/cli](https://www.npmjs.com/package/@salesforce/cli)