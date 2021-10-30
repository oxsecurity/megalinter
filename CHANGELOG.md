# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v5.0.0]

- Migration from github individual repo **nvuillam/mega-linter** to github organization repo **megalinter/megalinter**
- Migration from docker hub space **nvuillam** to space **megalinter**
  - Docker images are now **megalinter/megalinter** or **megalinter/megalinter-FLAVOR**
- Documentation is now hosted at <https://megalinter.github.io/>
- Tool to upgrade user repos configuration files using `npx mega-linter-runner --upgrade` (will upgrade references to nvuillam/mega-linter into megalinter/megalinter)
- Version management: Now mega-linter docker images, github action and mega-linter-runner versions are aligned
  - **latest** for latest official release
  - **beta** for current content of main branch
  - **alpha** for current content of alpha branch
  - docker image, github action and mega-linter-runner can still be called with exact version number
- Being more inclusive: rename `master` branch into `main`
- **IGNORE_GITIGNORED_FILES** parameter default to `true`

## [Unreleased] (main branch)

Note: Can be used with `megalinter/megalinter@beta` in your GitHub Action mega-linter.yml file, or with `megalinter/megalinter@beta` docker image

- Linter versions upgrades
<!-- linter-versions-end -->

## [4.47.0] - 2021-10-30

- Upgrades
  - Base docker image python:3.9.6-alpine3.13 to python:3.9.7-alpine3.13
  - Automerge internal job pascalgn/automerge-action-0.14.2 to pascalgn/automerge-action-0.14.3
- Config reporter: Parse `.vscode/extensions.json` as json5 (with comments)
- Add eslint-plugin-jsx-a11y dependency
- Rename default PHPStan config file, from `phpstan.neon` to `phpstan.neon.dist` accordingly to [PHPStan resolution priority](https://phpstan.org/config-reference#config-file)
- Allows `list_of_files` cli_lint_mode on PHPSTAN linter to improve performance compare to `file` mode
- `phpstan` is now installed with `phive` rather than `composer` (reduces disk usage)
- Allows `list_of_files` cli_lint_mode on PHPCS linter to improve performance compare to `file` mode
- Allows `list_of_files` cli_lint_mode on EditorConfig-Checker linter to improve performance compare to `file` mode
- Fix internal CSS because of StyleLint new rule `selector-class-pattern`
- Fix ansible-lint version collection
- Message to recommend to upgrade to MegaLinter v5

- Linter versions upgrades
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.54.1 to **0.54.2** on 2021-09-23
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 1.6.0 to **1.7.0** on 2021-09-23
  - [checkov](https://www.checkov.io/) from 2.0.430 to **2.0.436** on 2021-09-23
  - [coffeelint](http://www.coffeelint.org) from 5.0.3 to **5.0.4** on 2021-09-24
  - [checkov](https://www.checkov.io/) from 2.0.436 to **2.0.438** on 2021-09-24
  - [php](https://www.php.net) from 7.4.21 to **7.4.24** on 2021-09-24
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.32.3 to **0.32.4** on 2021-09-24
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.8.0 to **6.8.1** on 2021-09-25
  - [checkov](https://www.checkov.io/) from 2.0.438 to **2.0.441** on 2021-09-25
  - [secretlint](https://github.com/secretlint/secretlint) from 4.0.0 to **4.1.0** on 2021-09-25
  - [checkov](https://www.checkov.io/) from 2.0.441 to **2.0.442** on 2021-09-26
  - [checkov](https://www.checkov.io/) from 2.0.442 to **2.0.443** on 2021-09-27
  - [protolint](https://github.com/yoheimuta/protolint) from 0.32.0 to **0.35.1** on 2021-09-26
  - [protolint](https://github.com/yoheimuta/protolint) from 0.32.0 to **0.35.1** on 2021-09-27
  - [checkov](https://www.checkov.io/) from 2.0.443 to **2.0.446** on 2021-09-27
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.10.1 to **5.11.0** on 2021-09-29
  - [checkov](https://www.checkov.io/) from 2.0.446 to **2.0.448** on 2021-09-29
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 8.2.0 to **9.0.0** on 2021-09-30
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 2.11.0 to **2.12.0** on 2021-09-30
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 2.11.0 to **2.12.0** on 2021-09-30
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 2.11.0 to **2.12.0** on 2021-09-30
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.8.1 to **6.9.0** on 2021-09-30
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.11.0 to **5.11.1** on 2021-09-30
  - [checkov](https://www.checkov.io/) from 2.0.448 to **2.0.454** on 2021-09-30
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.9.0 to **6.9.1** on 2021-09-30
  - [checkov](https://www.checkov.io/) from 2.0.454 to **2.0.461** on 2021-09-30
  - [checkstyle](https://checkstyle.sourceforge.io) from 9.0 to **9.0.1** on 2021-10-03
  - [luacheck](https://luacheck.readthedocs.io) from 0.23.0 to **0.25.0** on 2021-10-03
  - [checkov](https://www.checkov.io/) from 2.0.461 to **2.0.467** on 2021-10-03
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.0.7 to **1.0.8** on 2021-10-03
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.32.4 to **0.34.0** on 2021-10-03
  - [sqlfluff](https://www.sqlfluff.com/) from 0.6.6 to **0.6.7** on 2021-10-05
  - [checkov](https://www.checkov.io/) from 2.0.467 to **2.0.469** on 2021-10-05
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.28.1 to **0.29.0** on 2021-10-06
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.11.1 to **5.12.0** on 2021-10-06
  - [sqlfluff](https://www.sqlfluff.com/) from 0.6.7 to **0.6.8** on 2021-10-06
  - [checkov](https://www.checkov.io/) from 2.0.469 to **2.0.475** on 2021-10-06
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.12.0 to **5.12.1** on 2021-10-06
  - [checkov](https://www.checkov.io/) from 2.0.475 to **2.0.476** on 2021-10-06
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.12.1 to **5.12.2** on 2021-10-07
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.34.0 to **0.34.1** on 2021-10-07
  - [checkov](https://www.checkov.io/) from 2.0.476 to **2.0.477** on 2021-10-07
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.10.0 to **1.11.0** on 2021-10-07
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.12.2 to **5.12.3** on 2021-10-09
  - [checkov](https://www.checkov.io/) from 2.0.477 to **2.0.479** on 2021-10-09
  - [sqlfluff](https://www.sqlfluff.com/) from 0.6.8 to **0.6.9** on 2021-10-10
  - [checkov](https://www.checkov.io/) from 2.0.479 to **2.0.481** on 2021-10-10
  - [checkov](https://www.checkov.io/) from 2.0.481 to **2.0.482** on 2021-10-10
  - [phpcs](https://github.com/squizlabs/PHP_CodeSniffer) from 3.6.0 to **3.6.1** on 2021-10-12
  - [flake8](https://flake8.pycqa.org) from 3.9.2 to **4.0.1** on 2021-10-12
  - [checkov](https://www.checkov.io/) from 2.0.482 to **2.0.484** on 2021-10-12
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.34.1 to **0.34.3** on 2021-10-12
  - [checkov](https://www.checkov.io/) from 2.0.484 to **2.0.485** on 2021-10-13
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.1.4 to **7.1.5** on 2021-10-16
  - [sqlfluff](https://www.sqlfluff.com/) from 0.6.9 to **0.7.0** on 2021-10-16
  - [checkov](https://www.checkov.io/) from 2.0.485 to **2.0.491** on 2021-10-16
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.0.8 to **1.0.9** on 2021-10-16
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.34.3 to **0.35.3** on 2021-10-16
  - [tflint](https://github.com/terraform-linters/tflint) from 0.32.1 to **0.33.0** on 2021-10-16
  - [checkov](https://www.checkov.io/) from 2.0.491 to **2.0.492** on 2021-10-17
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.6.5 to **1.6.6** on 2021-10-17
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.54.2 to **0.54.3** on 2021-10-21
  - [coffeelint](http://www.coffeelint.org) from 5.0.4 to **5.0.5** on 2021-10-21
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.4.3 to **0.4.4** on 2021-10-21
  - [tekton-lint](https://github.com/IBM/tekton-lint) from 0.5.2 to **0.6.0** on 2021-10-21
  - [checkov](https://www.checkov.io/) from 2.0.492 to **2.0.497** on 2021-10-21
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.35.3 to **0.35.4** on 2021-10-21
  - [stylelint](https://stylelint.io) from 13.13.1 to **14.0.0** on 2021-10-24
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.55 to **0.1.56** on 2021-10-24
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.9.1 to **6.10.0** on 2021-10-24
  - [sqlfluff](https://www.sqlfluff.com/) from 0.7.0 to **0.7.1** on 2021-10-24
  - [checkov](https://www.checkov.io/) from 2.0.497 to **2.0.509** on 2021-10-24
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.11.0 to **1.12.0** on 2021-10-24
  - [checkov](https://www.checkov.io/) from 2.0.509 to **2.0.510** on 2021-10-25
  - [checkov](https://www.checkov.io/) from 2.0.510 to **2.0.516** on 2021-10-26
  - [stylelint](https://stylelint.io) from 14.0.0 to **14.0.1** on 2021-10-26
  - [checkov](https://www.checkov.io/) from 2.0.516 to **2.0.524** on 2021-10-26
  - [php](https://www.php.net) from 7.4.24 to **7.4.25** on 2021-10-27
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.54.3 to **0.54.4** on 2021-10-28
  - [htmlhint](https://htmlhint.com/) from 0.15.2 to **0.16.0** on 2021-10-29
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.0.9 to **1.0.10** on 2021-10-29
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.35.4 to **0.35.5** on 2021-10-29

## [4.46.0] - 2021-09-21

- Add openssh apk for git repos using ssh
- Change default yamllint config file name from `.yaml-lint.yml` to `.yamllint.yml`
- Allow to disable console reporter using `CONSOLE_REPORTER: false`
- Override `cli_lint_mode` of linters using configuration : _LINTER_\_CLI_LINT_MODE
- Performances
  - Use list_of_files linting mode for yamllint , black and prettier
- Fixes
  - Add CONFIG_REPORTER in json schema
  - Fix Broken CI due to mega-linter test plugin

- Linter versions upgrades
  - [checkov](https://www.checkov.io/) from 2.0.396 to **2.0.399** on 2021-09-06
  - [golangci-lint](https://golangci-lint.run/) from 1.42.0 to **1.42.1** on 2021-09-07
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.7.0 to **6.8.0** on 2021-09-07
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.53.1 to **0.54.1** on 2021-09-12
  - [prettier](https://prettier.io/) from 2.3.2 to **2.4.0** on 2021-09-12
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.54 to **0.1.55** on 2021-09-12
  - [sqlfluff](https://www.sqlfluff.com/) from 0.6.4 to **0.6.5** on 2021-09-12
  - [checkov](https://www.checkov.io/) from 2.0.399 to **2.0.407** on 2021-09-12
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.31.8 to **0.31.10** on 2021-09-12
  - [tflint](https://github.com/terraform-linters/tflint) from 0.31.0 to **0.32.1** on 2021-09-12
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.9.0 to **5.9.1** on 2021-09-12
  - [phpstan](https://phpstan.org/) from 0.12.98 to **0.12.99** on 2021-09-15
  - [puppet-lint](http://puppet-lint.com/) from 2.5.0 to **2.5.2** on 2021-09-15
  - [black](https://black.readthedocs.io/en/stable/) from 21.8 to **21.9** on 2021-09-15
  - [checkov](https://www.checkov.io/) from 2.0.407 to **2.0.414** on 2021-09-15
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.31.10 to **0.31.11** on 2021-09-15
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.31.11 to **0.32.1** on 2021-09-15
  - [secretlint](https://github.com/secretlint/secretlint) from 3.3.0 to **4.0.0** on 2021-09-18
  - [htmlhint](https://htmlhint.com/) from 0.15.1 to **0.15.2** on 2021-09-18
  - [prettier](https://prettier.io/) from 2.4.0 to **2.4.1** on 2021-09-18
  - [pylint](https://www.pylint.org) from 2.10.2 to **2.11.1** on 2021-09-18
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.9.30 to **0.9.31** on 2021-09-18
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.9.1 to **5.10.1** on 2021-09-18
  - [checkov](https://www.checkov.io/) from 2.0.414 to **2.0.421** on 2021-09-18
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.0.6 to **1.0.7** on 2021-09-18
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.32.1 to **0.32.2** on 2021-09-18
  - [checkov](https://www.checkov.io/) from 2.0.421 to **2.0.425** on 2021-09-19
  - [checkov](https://www.checkov.io/) from 2.0.425 to **2.0.426** on 2021-09-19
  - [checkov](https://www.checkov.io/) from 2.0.426 to **2.0.427** on 2021-09-20
  - [coffeelint](http://www.coffeelint.org) from 5.0.2 to **5.0.3** on 2021-09-21
  - [rstfmt](https://github.com/dzhu/rstfmt) from 0.0.9 to **0.0.10** on 2021-09-21
  - [sqlfluff](https://www.sqlfluff.com/) from 0.6.5 to **0.6.6** on 2021-09-21
  - [checkov](https://www.checkov.io/) from 2.0.427 to **2.0.428** on 2021-09-21
  - [checkov](https://www.checkov.io/) from 2.0.428 to **2.0.430** on 2021-09-21
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.32.2 to **0.32.3** on 2021-09-21

## [4.45.0] - 2021-09-04

- New CONFIG_REPORTER to generate "ready to copy" folder containing default linter configurations and IDE extensions recommendations
- New JSON_REPORTER to generate an output json file in report folder
- Manage pre_commands and post_commands at linter level
  - Default commands defined at linter descriptor level
  - Overridable by user in linterName_PRE_COMMANDS and linterName_POST_COMMANDS in `.mega-linter.yml`
- Fix tflint config so no custom PRE_COMMAND is necessary
- Use dotnet installer to setup tsqllint. tsqllint is now part of the main Mega-Linter flavor, but removed from JAVASCRIPT flavor
- Ignore linter_FILTER_REGEX_INCLUDE/linter_FILTER_REGEX_EXCLUDE for linters running on the whole project directory
- mega-linter-runner updates
  - New CLI argument `--json`, to get the full report as JSON in stdout last line
  - Fix mega-linter-runner --install when local folder path contain spaces
  - Upgrade mega-linter-runner dependencies (npm audit fix)
  - Better comments for generated .mega-linter.yml config file

- Linter versions upgrades
  - [markdown-table-formatter](https://www.npmjs.com/package/markdown-table-formatter) from 1.1.0 to **1.2.0** on 2021-08-20
  - [phpstan](https://phpstan.org/) from 0.12.94 to **0.12.95** on 2021-08-20
  - [pylint](https://www.pylint.org) from 2.9.6 to **2.10.1** on 2021-08-21
  - [sqlfluff](https://www.sqlfluff.com/) from 0.6.3 to **0.6.4** on 2021-08-21
  - [phpstan](https://phpstan.org/) from 0.12.95 to **0.12.96** on 2021-08-21
  - [pylint](https://www.pylint.org) from 2.10.1 to **2.10.2** on 2021-08-22
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.7.2 to **5.8.0** on 2021-08-22
  - [yamllint](https://yamllint.readthedocs.io/) from 1.26.2 to **1.26.3** on 2021-08-22
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 1.5.0 to **1.6.0** on 2021-08-23
  - [checkov](https://www.checkov.io/) from 2.0.363 to **2.0.367** on 2021-08-23
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.8.0 to **5.8.1** on 2021-08-24
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.31.5 to **0.31.6** on 2021-08-24
  - [hadolint](https://github.com/hadolint/hadolint) from 2.6.0 to **2.7.0** on 2021-08-28
  - [dotenv-linter](https://dotenv-linter.github.io/) from 3.1.0 to **3.1.1** on 2021-08-28
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.8.1 to **5.8.2** on 2021-08-28
  - [checkov](https://www.checkov.io/) from 2.0.367 to **2.0.376** on 2021-08-28
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.31.6 to **0.31.7** on 2021-08-28
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.9.0 to **1.10.0** on 2021-08-28
  - [checkov](https://www.checkov.io/) from 2.0.376 to **2.0.377** on 2021-08-29
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.53.0 to **0.53.1** on 2021-08-31
  - [tsqllint](https://github.com/tsqllint/tsqllint) from 1.13.5.0 to **1.14.0.0** on 2021-08-31
  - [checkov](https://www.checkov.io/) from 2.0.377 to **2.0.380** on 2021-08-31
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.31.7 to **0.31.8** on 2021-08-31
  - [checkstyle](https://checkstyle.sourceforge.io) from 8.45.1 to **9.0** on 2021-09-01
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.8.2 to **5.9.0** on 2021-09-01
  - [checkov](https://www.checkov.io/) from 2.0.380 to **2.0.387** on 2021-09-01
  - [phpstan](https://phpstan.org/) from 0.12.96 to **0.12.97** on 2021-09-02
  - [checkov](https://www.checkov.io/) from 2.0.387 to **2.0.392** on 2021-09-02
  - [checkov](https://www.checkov.io/) from 2.0.392 to **2.0.393** on 2021-09-02
  - [phpstan](https://phpstan.org/) from 0.12.97 to **0.12.98** on 2021-09-03
  - [checkov](https://www.checkov.io/) from 2.0.393 to **2.0.395** on 2021-09-03
  - [checkov](https://www.checkov.io/) from 2.0.395 to **2.0.396** on 2021-09-04
  - [black](https://black.readthedocs.io/en/stable/) from 20.8 to **21.8** on 2021-09-04
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.4.2 to **0.4.3** on 2021-09-04
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.0.5 to **1.0.6** on 2021-09-04

## [4.44.0] - 2021-08-19

- Upgrade tflint descriptor to use ghcr.io/terraform-linters/tflint docker image and initialize tflint
- Add page for flavors stats in online documentation
- Unable to list git ignored files when IGNORED_GITIGNORED_FILES: true ([#PR605](https://github.com/megalinter/megalinter/pull/605), by [David Bernard](https://github.com/davidB) with the contribution of [Tim Pansino](https://github.com/TimPansino))

- Linter versions upgrades
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.1.3 to **7.1.4** on 2021-08-13
  - [checkov](https://www.checkov.io/) from 2.0.347 to **2.0.348** on 2021-08-13
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.6.6 to **5.6.7** on 2021-08-14
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.31.3 to **0.31.4** on 2021-08-14
  - [tflint](https://github.com/terraform-linters/tflint) from 0.29.1 to **0.31.0** on 2021-08-14
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.6.7 to **5.7.1** on 2021-08-15
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 1.4.0 to **1.5.0** on 2021-08-15
  - [checkov](https://www.checkov.io/) from 2.0.348 to **2.0.350** on 2021-08-15
  - [coffeelint](http://www.coffeelint.org) from 5.0.1 to **5.0.2** on 2021-08-17
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.9.29 to **0.9.30** on 2021-08-17
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.7.1 to **5.7.2** on 2021-08-17
  - [sqlfluff](https://www.sqlfluff.com/) from 0.6.2 to **0.6.3** on 2021-08-17
  - [checkov](https://www.checkov.io/) from 2.0.350 to **2.0.352** on 2021-08-17
  - [golangci-lint](https://golangci-lint.run/) from 1.41.1 to **1.42.0** on 2021-08-18
  - [checkov](https://www.checkov.io/) from 2.0.352 to **2.0.361** on 2021-08-18
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 2.10.1005 to **2.11.0** on 2021-08-19
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 2.10.1005 to **2.11.0** on 2021-08-19
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 2.10.1005 to **2.11.0** on 2021-08-19
  - [checkov](https://www.checkov.io/) from 2.0.361 to **2.0.363** on 2021-08-19
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.0.4 to **1.0.5** on 2021-08-19
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.31.4 to **0.31.5** on 2021-08-19

## [4.43.0] - 2021-08-12

- Add [secretlint](https://github.com/secretlint/secretlint) to check for credentials , secrets and passwords stored in linted repository

- Linter versions upgrades
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.6.1 to **6.7.0** on 2021-08-12
  - [checkov](https://www.checkov.io/) from 2.0.344 to **2.0.346** on 2021-08-12
  - [checkov](https://www.checkov.io/) from 2.0.346 to **2.0.347** on 2021-08-12

## [4.42.0] - 2021-08-12

- Add [tsqllint](https://github.com/tsqllint/tsqllint) to lint [TSQL files](https://www.tsql.info/)
- Store docker pulls statistics history
- add `IGNORE_GENERATED_FILES` in json schema
- allow commonjs config file for eslint - [#629](https://github.com/megalinter/megalinter/pull/629), by [vitalitytv](https://github.com/vitaliytv)

- Linter versions upgrades
  - [checkov](https://www.checkov.io/) from 2.0.295 to **2.0.297** on 2021-07-25
  - [puppet-lint](http://puppet-lint.com/) from 2.4.2 to **2.5.0** on 2021-07-26
  - [checkov](https://www.checkov.io/) from 2.0.297 to **2.0.303** on 2021-07-26
  - [checkov](https://www.checkov.io/) from 2.0.303 to **2.0.307** on 2021-07-28
  - [v8r](https://github.com/chris48s/v8r) from 0.5.0 to **0.6.0** on 2021-07-29
  - [pylint](https://www.pylint.org) from 2.9.5 to **2.9.6** on 2021-07-29
  - [checkov](https://www.checkov.io/) from 2.0.307 to **2.0.313** on 2021-07-29
  - [isort](https://pycqa.github.io/isort/) from 5.9.2 to **5.9.3** on 2021-07-30
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.53 to **0.1.54** on 2021-07-30
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.4.1 to **0.4.2** on 2021-07-30
  - [checkov](https://www.checkov.io/) from 2.0.313 to **2.0.317** on 2021-07-30
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.31.1 to **0.31.2** on 2021-07-30
  - [eslint](https://eslint.org) from 7.31.0 to **7.32.0** on 2021-07-31
  - [phpstan](https://phpstan.org/) from 0.12.93 to **0.12.94** on 2021-07-31
  - [checkov](https://www.checkov.io/) from 2.0.317 to **2.0.318** on 2021-07-31
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.31.2 to **0.31.3** on 2021-07-31
  - [checkstyle](https://checkstyle.sourceforge.io) from 8.44 to **8.45** on 2021-08-01
  - [shfmt](https://github.com/mvdan/sh) from 3.3.0 to **3.3.1** on 2021-08-02
  - [checkov](https://www.checkov.io/) from 2.0.318 to **2.0.323** on 2021-08-02
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.52.0 to **0.53.0** on 2021-08-03
  - [checkov](https://www.checkov.io/) from 2.0.323 to **2.0.327** on 2021-08-03
  - [remark-lint](https://remark.js.org/) from 13.0.0 to **14.0.1** on 2021-08-04
  - [checkov](https://www.checkov.io/) from 2.0.327 to **2.0.330** on 2021-08-04
  - [yamllint](https://yamllint.readthedocs.io/) from 1.26.1 to **1.26.2** on 2021-08-04
  - [checkov](https://www.checkov.io/) from 2.0.330 to **2.0.334** on 2021-08-05
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.0.3 to **1.0.4** on 2021-08-05
  - [checkov](https://www.checkov.io/) from 2.0.334 to **2.0.336** on 2021-08-05
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 2.10.0 to **2.10.1005** on 2021-08-06
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 2.10.0 to **2.10.1005** on 2021-08-06
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 2.10.0 to **2.10.1005** on 2021-08-06
  - [v8r](https://github.com/chris48s/v8r) from 0.6.0 to **0.6.1** on 2021-08-07
  - [checkov](https://www.checkov.io/) from 2.0.336 to **2.0.337** on 2021-08-07
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.8.1 to **1.9.0** on 2021-08-07
  - [checkov](https://www.checkov.io/) from 2.0.337 to **2.0.338** on 2021-08-08
  - [checkstyle](https://checkstyle.sourceforge.io) from 8.45 to **8.45.1** on 2021-08-09
  - [checkov](https://www.checkov.io/) from 2.0.338 to **2.0.340** on 2021-08-09
  - [checkov](https://www.checkov.io/) from 2.0.340 to **2.0.342** on 2021-08-10
  - [checkov](https://www.checkov.io/) from 2.0.342 to **2.0.344** on 2021-08-10

## [4.41.0] - 2021-07-25

- New config variable **IGNORE_GITIGNORED_FILES** (default: `false`). If set to `true`, Mega-Linter will skips files ignored by git using `.gitignore` files
- New config variable **IGNORE_GENERATED_FILES** (default: `false`). If set to `true`, Mega-Linter will skips files containing `@generated` marker and not containing `@not-generated` marker

- Linter versions upgrades
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 2.9.2 to **2.9.1** on 2021-07-14
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 2.9.2 to **2.9.1** on 2021-07-14
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 2.9.2 to **2.9.1** on 2021-07-14
  - [checkov](https://www.checkov.io/) from 2.0.267 to **2.0.269** on 2021-07-14
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.5.3 to **6.6.0** on 2021-07-17
  - [sqlfluff](https://www.sqlfluff.com/) from 0.6.0 to **0.6.1** on 2021-07-17
  - [checkov](https://www.checkov.io/) from 2.0.269 to **1.0.860** on 2021-07-17
  - [checkov](https://www.checkov.io/) from 1.0.860 to **2.0.276** on 2021-07-17
  - [eslint](https://eslint.org) from 7.30.0 to **7.31.0** on 2021-07-17
  - [checkov](https://www.checkov.io/) from 2.0.276 to **2.0.278** on 2021-07-18
  - [checkov](https://www.checkov.io/) from 2.0.278 to **2.0.279** on 2021-07-18
  - [checkov](https://www.checkov.io/) from 2.0.279 to **2.0.280** on 2021-07-18
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.6.0 to **6.6.1** on 2021-07-20
  - [checkov](https://www.checkov.io/) from 2.0.280 to **2.0.283** on 2021-07-20
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.0.1 to **1.0.2** on 2021-07-20
  - [phpstan](https://phpstan.org/) from 0.12.92 to **0.12.93** on 2021-07-21
  - [pylint](https://www.pylint.org) from 2.9.3 to **2.9.4** on 2021-07-21
  - [checkov](https://www.checkov.io/) from 2.0.283 to **2.0.287** on 2021-07-21
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.31.0 to **0.31.1** on 2021-07-21
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.27.1 to **0.28.1** on 2021-07-25
  - [pylint](https://www.pylint.org) from 2.9.4 to **2.9.5** on 2021-07-25
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 2.9.1 to **2.10.0** on 2021-07-25
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 2.9.1 to **2.10.0** on 2021-07-25
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 2.9.1 to **2.10.0** on 2021-07-25
  - [sqlfluff](https://www.sqlfluff.com/) from 0.6.1 to **0.6.2** on 2021-07-25
  - [checkov](https://www.checkov.io/) from 2.0.287 to **2.0.295** on 2021-07-25
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.0.2 to **1.0.3** on 2021-07-25
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.8.0 to **1.8.1** on 2021-07-25
  - [xmllint](http://xmlsoft.org/xmllint.html) from 20910 to **20912** on 2021-07-25

## [4.40.0] - 2021-07-14

- Add [mypy](https://github.com/python/mypy) python linter
- mega-linter-runner: Add possibility to send the docker image to use, including from another registry than docker hub, with argument `--image`

- Linter versions upgrades
  - [phpstan](https://phpstan.org/) from 0.12.91 to **0.12.92** on 2021-07-10
  - [checkov](https://www.checkov.io/) from 2.0.259 to **2.0.261** on 2021-07-11
  - [checkov](https://www.checkov.io/) from 2.0.261 to **2.0.262** on 2021-07-11
  - [checkov](https://www.checkov.io/) from 2.0.262 to **2.0.263** on 2021-07-12
  - [checkov](https://www.checkov.io/) from 2.0.263 to **2.0.266** on 2021-07-13
  - [checkov](https://www.checkov.io/) from 2.0.266 to **2.0.267** on 2021-07-13

## [4.39.0] - 2021-07-14 [DELETED RELEASE BECAUSE NOT WORKING, USE 4.38.0 UNTIL 4.40.0 RELEASE]

- Add [mypy](https://github.com/python/mypy) python linter
- mega-linter-runner: Add possibility to send the docker image to use, including from another registry than docker hub, with argument `--image`

- Linter versions upgrades
  - [phpstan](https://phpstan.org/) from 0.12.91 to **0.12.92** on 2021-07-10
  - [checkov](https://www.checkov.io/) from 2.0.259 to **2.0.261** on 2021-07-11
  - [checkov](https://www.checkov.io/) from 2.0.261 to **2.0.262** on 2021-07-11
  - [checkov](https://www.checkov.io/) from 2.0.262 to **2.0.263** on 2021-07-12
  - [checkov](https://www.checkov.io/) from 2.0.263 to **2.0.266** on 2021-07-13
  - [checkov](https://www.checkov.io/) from 2.0.266 to **2.0.267** on 2021-07-13

## [4.38.0] - 2021-07-10

- New python linter: [bandit](https://github.com/PyCQA/bandit), added by [Tom Pansino](https://github.com/tpansino)
- Manage Github action versioning: Match Mega-Linter docker image version

- Linter versions upgrades
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.5.2 to **6.5.3** on 2021-07-07
  - [checkov](https://www.checkov.io/) from 2.0.251 to **2.0.253** on 2021-07-07
  - [php](https://www.php.net) from 7.4.19 to **7.4.21** on 2021-07-07
  - [sql-lint](https://github.com/joereynolds/sql-lint) from 0.0.18 to **0.0.19** on 2021-07-08
  - [checkov](https://www.checkov.io/) from 2.0.253 to **2.0.257** on 2021-07-08
  - [isort](https://pycqa.github.io/isort/) from 5.9.1 to **5.9.2** on 2021-07-10
  - [checkov](https://www.checkov.io/) from 2.0.257 to **2.0.259** on 2021-07-10

## [4.37.0] - 2021-07-05

- Downgrade npm to npm@latest-6 to avoid idealTree error when using npm install
- Use pip to install ansible & ansible-lint as alpine apk package ansible disappeared
- Add `--doc` argument to build.sh to generate doc only when requested (manually, or from CI job Auto-Update-Linters)
- Add rust in default installations as it is required for latest pip cryptography package

- Linter versions upgrades
  - [rstfmt](https://github.com/dzhu/rstfmt) from 0.0.0 to **0.0.9** on 2021-06-24
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 2.9.1 to **2.9.2** on 2021-06-24
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 2.9.1 to **2.9.2** on 2021-06-24
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 2.9.1 to **2.9.2** on 2021-06-24
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.4.1 to **6.5.0** on 2021-06-24
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from Terraform.v1.0.0 to **1.0.0** on 2021-06-24
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.30.7 to **0.31.0** on 2021-06-24
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.5.0 to **6.5.1** on 2021-06-24
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.0.0 to **1.0.1** on 2021-06-24
  - [prettier](https://prettier.io/) from 2.3.1 to **2.3.2** on 2021-06-27
  - [checkstyle](https://checkstyle.sourceforge.io) from 8.43 to **8.44** on 2021-06-28
  - [checkov](https://www.checkov.io/) from 2.0.226 to **2.0.228** on 2021-06-28
  - [checkov](https://www.checkov.io/) from 2.0.228 to **2.0.229** on 2021-06-28
  - [checkov](https://www.checkov.io/) from 2.0.229 to **2.0.230** on 2021-06-28
  - [checkov](https://www.checkov.io/) from 2.0.230 to **2.0.232** on 2021-06-28
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.51.0 to **0.52.0** on 2021-07-05
  - [hadolint](https://github.com/hadolint/hadolint) from 2.5.0 to **2.6.0** on 2021-07-05
  - [eslint](https://eslint.org) from 7.29.0 to **7.30.0** on 2021-07-05
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 1.3.1 to **1.4.0** on 2021-07-05
  - [phpstan](https://phpstan.org/) from 0.12.90 to **0.12.91** on 2021-07-05
  - [pylint](https://www.pylint.org) from 2.8.3 to **2.9.3** on 2021-07-05
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.5.1 to **6.5.2** on 2021-07-05
  - [checkov](https://www.checkov.io/) from 2.0.232 to **2.0.250** on 2021-07-05
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.7.0 to **1.8.0** on 2021-07-05
  - [checkov](https://www.checkov.io/) from 2.0.250 to **2.0.251** on 2021-07-05

## [4.36.0] - 2021-06-22

- Fix Phive (php package manager) installation
- Fix dependency error with importlib_metadata before build

- Linter versions upgrades
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2021.04.23 to **2021.06.18** on 2021-06-22
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.50.0 to **0.51.0** on 2021-06-22
  - [hadolint](https://github.com/hadolint/hadolint) from 2.4.1 to **2.5.0** on 2021-06-22
  - [dotenv-linter](https://dotenv-linter.github.io/) from 3.0.0 to **3.1.0** on 2021-06-22
  - [golangci-lint](https://golangci-lint.run/) from 1.40.1 to **1.41.1** on 2021-06-22
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 8.1.0 to **8.2.0** on 2021-06-22
  - [htmlhint](https://htmlhint.com/) from 0.14.2 to **0.15.1** on 2021-06-22
  - [eslint](https://eslint.org) from 7.28.0 to **7.29.0** on 2021-06-22
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 1.2.1 to **1.3.1** on 2021-06-22
  - [phpstan](https://phpstan.org/) from 0.12.88 to **0.12.90** on 2021-06-22
  - [isort](https://pycqa.github.io/isort/) from 5.8.0 to **5.9.1** on 2021-06-22
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.52 to **0.1.53** on 2021-06-22
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.4.0 to **0.4.1** on 2021-06-22
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.6.0 to **5.6.6** on 2021-06-22
  - [sqlfluff](https://www.sqlfluff.com/) from 0.5.6 to **0.6.0** on 2021-06-22
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from Terraform.v0.15.5 to **Terraform.v1.0.0** on 2021-06-22
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.29.8 to **0.30.7** on 2021-06-22
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.6.0 to **1.7.0** on 2021-06-22
  - [tflint](https://github.com/terraform-linters/tflint) from 0.29.0 to **0.29.1** on 2021-06-22

## [4.35.0] - 2021-06-12

- Fix [#304](https://github.com/megalinter/megalinter/issues/304): Display error message when docker is not found when running mega-linter-runner
- Calculate sum of docker pulls for main page counter badge
- Check _RULES_PATH for active_only_if_file_found check ([#418](https://github.com/megalinter/megalinter/pull/418), by [Omeed Musavi](https://github.com/omusavi))
- Upgrade clj-kondo 2021.04.23-alpine
- Upgrade to python:3.9.5-alpine
- Partial fix [#481](https://github.com/megalinter/megalinter/issues/481): Allow applying fixes on push events ([PR487](https://github.com/megalinter/megalinter/pull/487) by [Vít Kučera](https://github.com/vkucera))
- Fix build.sh on windows
- Add trivy security check of all built Mega-Linter docker images

- Linter versions upgrades
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.29.2 to **0.29.3** on 2021-05-16
  - [shfmt](https://github.com/mvdan/sh) from 3.2.4 to **3.3.0** on 2021-05-18
  - [phpstan](https://phpstan.org/) from 0.12.87 to **0.12.88** on 2021-05-18
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.49.1 to **0.49.2** on 2021-05-19
  - [cpplint](https://github.com/cpplint/cpplint) from 1.5.4 to **1.5.5** on 2021-05-21
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.9.27 to **0.9.28** on 2021-05-21
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.3.0 to **6.4.0** on 2021-05-21
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from Terraform.v0.15.3 to **Terraform.v0.15.4** on 2021-05-21
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.29.3 to **0.29.4** on 2021-05-21
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 2.8.0 to **2.9.1** on 2021-05-22
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 2.8.0 to **2.9.1** on 2021-05-22
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 2.8.0 to **2.9.1** on 2021-05-22
  - [jscpd](https://github.com/kucherenko/jscpd/tree/master/packages/jscpd) from 3.3.25 to **3.3.26** on 2021-05-24
  - [eslint](https://eslint.org) from 7.26.0 to **7.27.0** on 2021-05-24
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2021.02.13 to **2021.04.23** on 2021-05-24
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.29.4 to **0.29.5** on 2021-05-24
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.4.0 to **6.4.1** on 2021-05-28
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.29.5 to **0.29.6** on 2021-05-28
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.29.6 to **0.29.7** on 2021-05-29
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 4.1.3 to **5.5.2** on 2021-05-30
  - [checkstyle](https://checkstyle.sourceforge.io) from 8.42 to **8.43** on 2021-05-30
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.9.28 to **0.9.29** on 2021-05-30
  - [pylint](https://www.pylint.org) from 2.8.2 to **2.8.3** on 2021-06-01
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.49.2 to **0.50.0** on 2021-06-04
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from Terraform.v0.15.4 to **Terraform.v0.15.5** on 2021-06-04
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.29.7 to **0.29.8** on 2021-06-04
  - [eslint](https://eslint.org) from 7.27.0 to **7.28.0** on 2021-06-05
  - [prettier](https://prettier.io/) from 2.3.0 to **2.3.1** on 2021-06-07
  - [protolint](https://github.com/yoheimuta/protolint) from 0.31.0 to **0.32.0** on 2021-06-07
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.5.2 to **5.6.0** on 2021-06-07
  - [sql-lint](https://github.com/joereynolds/sql-lint) from 0.0.17 to **0.0.18** on 2021-06-07
  - [tflint](https://github.com/terraform-linters/tflint) from 0.28.1 to **0.29.0** on 2021-06-07

## [4.34.0] - 2021-04-30

- Fix bug in Mega-Linter plugins installation (related to [#PR403](https://github.com/megalinter/megalinter/pull/403))

- Linter versions upgrades
  - [sqlfluff](https://www.sqlfluff.com/) from 0.5.3 to **0.5.5** on 2021-05-14
  - [hadolint](https://github.com/hadolint/hadolint) from 2.4.0 to **2.4.1** on 2021-05-15
  - [golangci-lint](https://golangci-lint.run/) from 1.40.0 to **1.40.1** on 2021-05-15
  - [sqlfluff](https://www.sqlfluff.com/) from 0.5.5 to **0.5.6** on 2021-05-15

## [4.33.0] - 2021-04-30

- Split Salesforce sfdx-scanner into pmd, eslint aura and eslint lwc

- Linter versions upgrades
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.1.1 to **6.1.2** on 2021-04-20
  - [stylelint](https://stylelint.io) from 13.12.0 to **13.13.0** on 2021-04-25
  - [hadolint](https://github.com/hadolint/hadolint) from 2.2.0 to **2.3.0** on 2021-04-25
  - [eslint](https://eslint.org) from 7.24.0 to **7.25.0** on 2021-04-25
  - [pylint](https://www.pylint.org) from 2.7.4 to **2.8.0** on 2021-04-25
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.1.2 to **6.2.1** on 2021-04-25
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.4.0 to **1.5.0** on 2021-04-25
  - [checkstyle](https://checkstyle.sourceforge.io) from 8.41.1 to **8.42** on 2021-04-25
  - [pylint](https://www.pylint.org) from 2.8.0 to **2.8.1** on 2021-04-25
  - [tflint](https://github.com/terraform-linters/tflint) from 0.27.0 to **0.28.0** on 2021-04-25
  - [pylint](https://www.pylint.org) from 2.8.1 to **2.8.2** on 2021-04-27
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.48.3 to **0.49.0** on 2021-04-28
  - [phpstan](https://phpstan.org/) from 0.12.84 to **0.12.85** on 2021-04-28
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.28.21 to **0.29.0** on 2021-04-28
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.2.1 to **6.3.0** on 2021-04-30
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.5.0 to **1.5.1** on 2021-04-30

## [4.32.0] - 2021-04-20

- Fix #376 : Link-title to license
- Add support from prettier as JSON formatter ([#421](https://github.com/megalinter/megalinter/pull/421), by [Omeed Musavi](https://github.com/omusavi)

- Linter versions upgrades
  - [phpstan](https://phpstan.org/) from 0.12.82 to **0.12.83** on 2021-04-03
  - [markdown-table-formatter](https://www.npmjs.com/package/markdown-table-formatter) from 1.0.4 to **1.1.0** on 2021-04-05
  - [tflint](https://github.com/terraform-linters/tflint) from 0.25.0 to **0.26.0** on 2021-04-05
  - [sqlfluff](https://www.sqlfluff.com/) from 0.4.1 to **0.5.0** on 2021-04-06
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.48.1 to **0.48.2** on 2021-04-07
  - [yamllint](https://yamllint.readthedocs.io/) from 1.26.0 to **1.26.1** on 2021-04-07
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.1.0 to **6.1.1** on 2021-04-08
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.28.16 to **0.28.19** on 2021-04-09
  - [phpcs](https://github.com/squizlabs/PHP_CodeSniffer) from 3.5.8 to **3.6.0** on 2021-04-09
  - [eslint](https://eslint.org) from 7.23.0 to **7.24.0** on 2021-04-10
  - [sqlfluff](https://www.sqlfluff.com/) from 0.5.0 to **0.5.1** on 2021-04-10
  - [protolint](https://github.com/yoheimuta/protolint) from 0.30.1 to **0.31.0** on 2021-04-11
  - [sqlfluff](https://www.sqlfluff.com/) from 0.5.1 to **0.5.2** on 2021-04-11
  - [sfdx-scanner](https://forcedotcom.github.io/sfdx-scanner/) from 2.7.0 to **2.8.0** on 2021-04-14
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.28.19 to **0.28.21** on 2021-04-15
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.48.2 to **0.48.3** on 2021-04-17
  - [flake8](https://flake8.pycqa.org) from 3.9.0 to **3.9.1** on 2021-04-17
  - [tflint](https://github.com/terraform-linters/tflint) from 0.26.0 to **0.27.0** on 2021-04-19
  - [hadolint](https://github.com/hadolint/hadolint) from 2.1.0 to **2.2.0** on 2021-04-19
  - [phpstan](https://phpstan.org/) from 0.12.83 to **0.12.84** on 2021-04-19
  - [shellcheck](https://github.com/koalaman/shellcheck) from 0.7.1 to **0.7.2** on 2021-04-19

## [4.31.0] - 2021-04-03

- Keep license pre-formatted in docs
- Use Python virtual-environment in dev-dependencies shell example
- Fix #367 : Display editorconfig-checker version
- Fix #379 : New configuration FAIL_IF_MISSING_LINTER_IN_FLAVOR

- Linter versions upgrades
  - [flake8](https://flake8.pycqa.org) from 3.8.4 to **3.9.0** on 2021-03-15
  - [ktlint](https://ktlint.github.io) from 0.40.0 to **0.41.0** on 2021-03-21
  - [phpstan](https://phpstan.org/) from 0.12.81 to **0.12.82** on 2021-03-21
  - [isort](https://pycqa.github.io/isort/) from 5.7.0 to **5.8.0** on 2021-03-21
  - [sfdx-scanner](https://forcedotcom.github.io/sfdx-scanner/) from 2.6.0 to **2.7.0** on 2021-03-21
  - [sql-lint](https://github.com/joereynolds/sql-lint) from 0.0.15 to **0.0.16** on 2021-03-21
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.43.0 to **0.43.1** on 2021-03-21
  - [editorconfig-checker](https://editorconfig-checker.github.io/) from 0.0.0 to **2.3.4** on 2021-03-22
  - [ktlint](https://ktlint.github.io) from 0.41.0 to **0.40.0** on 2021-03-22
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.47.2 to **0.48.1** on 2021-03-30
  - [coffeelint](http://www.coffeelint.org) from 4.1.3 to **4.1.4** on 2021-03-30
  - [hadolint](https://github.com/hadolint/hadolint) from 1.23.0 to **2.0.0** on 2021-03-30
  - [golangci-lint](https://golangci-lint.run/) from 1.38.0 to **1.39.0** on 2021-03-30
  - [checkstyle](https://checkstyle.sourceforge.io) from 8.41 to **8.41.1** on 2021-03-30
  - [eslint](https://eslint.org) from 7.22.0 to **7.23.0** on 2021-03-30
  - [kubeval](https://www.kubeval.com/) from 0.15.0 to **0.16.1** on 2021-03-30
  - [perlcritic](https://metacpan.org/pod/Perl::Critic) from 1.138 to **1.140** on 2021-03-30
  - [pylint](https://www.pylint.org) from 2.7.2 to **2.7.4** on 2021-03-30
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.0.212 to **0.1.51** on 2021-03-30
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.9.26 to **0.9.27** on 2021-03-30
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.28.9 to **0.28.16** on 2021-03-30
  - [kubeval](https://www.kubeval.com/) from 0.16.0 to **0.16.1** on 2021-03-30
  - [pylint](https://www.pylint.org) from 2.7.3 to **2.7.4** on 2021-03-30
  - [editorconfig-checker](https://editorconfig-checker.github.io/) from 2.3.4 to **2.3.5** on 2021-03-31
  - [hadolint](https://github.com/hadolint/hadolint) from 2.0.0 to **2.1.0** on 2021-04-02
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.0.5 to **6.1.0** on 2021-04-02

## [4.30.0] - 2021-03-14

- Fix #361 - Not respecting `*_DISABLE_ERRORS: false`
- New variable **FORMATTERS_DISABLE_ERRORS** to force all formatters to be blocking if errors are found
- Add *.svg in .jscpd (copy-paste detector) default ignore paths

- Linter versions upgrades
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.47.1 to **0.47.2** on 2021-03-13
  - [eslint](https://eslint.org) from 7.21.0 to **7.22.0** on 2021-03-13
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 1.1.0 to **1.2.1** on 2021-03-14

## [4.29.0] - 2021-03-12

- Fix regex to list Salesforce errors
- Fix Updated Files Reporter when Mega-Linter is not running on GitHub Action
- Fix #359 - invalid literal with _DISABLE_ERRORS_IF_LESS_THAN

- Linter versions upgrades
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2021.01.20 to **2021.02.13** on 2021-03-01
  - [jscpd](https://github.com/kucherenko/jscpd/tree/master/packages/jscpd) from 3.3.24 to **3.3.25** on 2021-03-06
  - [hadolint](https://github.com/hadolint/hadolint) from 1.22.1 to **1.23.0** on 2021-03-06
  - [golangci-lint](https://golangci-lint.run/) from 1.37.1 to **1.38.0** on 2021-03-06
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.26.0 to **0.27.1** on 2021-03-06
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.0.0 to **6.0.2** on 2021-03-06
  - [sqlfluff](https://www.sqlfluff.com/) from 0.4.0 to **0.4.1** on 2021-03-06
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.42.0 to **0.43.0** on 2021-03-06
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.3.3 to **1.4.0** on 2021-03-06
  - [stylelint](https://stylelint.io) from 13.11.0 to **13.12.0** on 2021-03-06
  - [tflint](https://github.com/terraform-linters/tflint) from 0.24.1 to **0.25.0** on 2021-03-06
  - [shfmt](https://github.com/mvdan/sh) from 3.2.2 to **3.2.4** on 2021-03-10
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.46.0 to **0.47.0** on 2021-03-10
  - [git_diff](https://git-scm.com) from 2.30.1 to **2.30.2** on 2021-03-10
  - [phpstan](https://phpstan.org/) from 0.12.80 to **0.12.81** on 2021-03-10
  - [protolint](https://github.com/yoheimuta/protolint) from 0.29.0 to **0.30.1** on 2021-03-10
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.3.1 to **0.4.0** on 2021-03-10
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.0.2 to **6.0.3** on 2021-03-10
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.47.0 to **0.47.1** on 2021-03-12
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.1.2 to **7.1.3** on 2021-03-12
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.0.3 to **6.0.5** on 2021-03-12
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.28.6 to **0.28.9** on 2021-03-12

## [4.28.0] - 2021-03-01

- Feature: **<LINTER_NAME>_DISABLE_ERRORS_IF_LESS_THAN** : set linter status to warning if maximum allowed errors is not reached
- Add colors in logs

- Linter versions upgrades
  - [pylint](https://www.pylint.org) from 2.6.0 to **2.6.2** on 2021-02-16
  - [golangci-lint](https://golangci-lint.run/) from 1.36.0 to **1.37.0** on 2021-02-19
  - [phpstan](https://phpstan.org/) from 0.12.76 to **0.12.77** on 2021-02-19
  - [sfdx-scanner](https://forcedotcom.github.io/sfdx-scanner/) from 2.5.1 to **2.6.0** on 2021-02-19
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.28.2 to **0.28.6** on 2021-02-19
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.3.2 to **1.3.3** on 2021-02-19
  - [stylelint](https://stylelint.io) from 13.10.0 to **13.11.0** on 2021-02-21
  - [golangci-lint](https://golangci-lint.run/) from 1.37.0 to **1.37.1** on 2021-02-21
  - [phpstan](https://phpstan.org/) from 0.12.77 to **0.12.78** on 2021-02-21
  - [pylint](https://www.pylint.org) from 2.6.2 to **2.7.0** on 2021-02-22
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.45.0 to **0.46.0** on 2021-02-24
  - [pylint](https://www.pylint.org) from 2.7.0 to **2.7.1** on 2021-02-24
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 0.9.0 to **1.0.0** on 2021-02-25
  - [phpstan](https://phpstan.org/) from 0.12.78 to **0.12.79** on 2021-02-25
  - [protolint](https://github.com/yoheimuta/protolint) from 0.28.2 to **0.29.0** on 2021-02-25
  - [jscpd](https://github.com/kucherenko/jscpd/tree/master/packages/jscpd) from 3.3.23 to **3.3.24** on 2021-02-28
  - [eslint](https://eslint.org) from 7.20.0 to **7.21.0** on 2021-02-28
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.9.25 to **0.9.26** on 2021-02-28
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 5.32.2 to **6.0.0** on 2021-02-28
  - [checkstyle](https://checkstyle.sourceforge.io) from 8.40 to **8.41** on 2021-03-01
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 1.0.0 to **1.1.0** on 2021-03-01
  - [phpstan](https://phpstan.org/) from 0.12.79 to **0.12.80** on 2021-03-01
  - [pylint](https://www.pylint.org) from 2.7.1 to **2.7.2** on 2021-03-01
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2021.01.20 to **2021.02.13** on 2021-03-01

## [4.27.0] - 2021-02-16

- Linters
  - Format YAML with prettier

- Core
  - Lint docker image using [Dockle](https://github.com/goodwithtech/dockle)

- Fixes
  - Fix ansible-lint test cases for new version
  - Update --help expected return code for shfmt ash formatter and revive go linter
  - Add --write to update files fixed by eslint
  - Pimp Mega-Linter sources by adding newLines when missing (manually and from build.py) + fix logger initialization error + call python3 by default ([PR329](https://github.com/megalinter/megalinter/pull/329) by [Tom Klingenberg](https://github.com/ktomk))
  - Increase max line length to 500 in yaml-lint default configuration

- Linter versions upgrades
  - [ansible-lint](https://ansible-lint.readthedocs.io/en/latest/) from 4.2.0 to **5.0.0** on 2021-02-09
  - [bash-exec](https://tiswww.case.edu/php/chet/bash/bashtop.html) from 5.0.17 to **5.1.0** on 2021-02-09
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.44.6 to **0.44.7** on 2021-02-09
  - [hadolint](https://github.com/hadolint/hadolint) from 1.21.0 to **1.22.1** on 2021-02-09
  - [git_diff](https://git-scm.com) from 2.26.2 to **2.30.1** on 2021-02-09
  - [php](https://www.php.net) from 7.3.26 to **7.4.15** on 2021-02-09
  - [phpstan](https://phpstan.org/) from 0.12.71 to **0.12.74** on 2021-02-09
  - [protolint](https://github.com/yoheimuta/protolint) from 0.28.0 to **0.28.2** on 2021-02-09
  - [lintr](https://github.com/jimhester/lintr) from 2.0.1.9000 to **0.0.0** on 2021-02-09
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 5.32.0 to **5.32.1** on 2021-02-09
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.27.1 to **0.28.2** on 2021-02-09
  - [ansible-lint](https://ansible-lint.readthedocs.io/en/latest/) from 5.0.0 to **0.0.0** on 2021-02-09
  - [dotnet-format](https://github.com/dotnet/format) from 4.1.131201 to **5.0.211103** on 2021-02-12
  - [stylelint](https://stylelint.io) from 13.9.0 to **13.10.0** on 2021-02-12
  - [phpstan](https://phpstan.org/) from 0.12.74 to **0.12.75** on 2021-02-12
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.0.4 to **7.1.2** on 2021-02-12
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 5.32.1 to **5.32.2** on 2021-02-12
  - [coffeelint](http://www.coffeelint.org) from 4.1.2 to **4.1.3** on 2021-02-14
  - [eslint](https://eslint.org) from 7.19.0 to **7.20.0** on 2021-02-14
  - [phpstan](https://phpstan.org/) from 0.12.75 to **0.12.76** on 2021-02-14
  - [black](https://black.readthedocs.io/en/stable/) from 19.10 to **20.8** on 2021-02-15
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.2.6 to **0.3.0** on 2021-02-15
  - [sqlfluff](https://www.sqlfluff.com/) from 0.3.6 to **0.4.0** on 2021-02-15
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.44.7 to **0.45.0** on 2021-02-16
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.3.0 to **0.3.1** on 2021-02-16

## [4.26.2] - 2021-01-29

- Linter versions upgrades
  - [shfmt](https://github.com/mvdan/sh) from 3.2.1 to **3.2.2** on 2021-01-30
  - [yamllint](https://yamllint.readthedocs.io/) from 1.25.0 to **1.26.0** on 2021-01-30
  - [hadolint](https://github.com/hadolint/hadolint) from 1.20.0 to **1.21.0** on 2021-02-02
  - [checkstyle](https://checkstyle.sourceforge.io) from 8.39 to **8.40** on 2021-02-02
  - [eslint](https://eslint.org) from 7.18.0 to **7.19.0** on 2021-02-02
  - [phpstan](https://phpstan.org/) from 0.12.70 to **0.12.71** on 2021-02-02
  - [tflint](https://github.com/terraform-linters/tflint) from 0.23.1 to **0.24.1** on 2021-02-02
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.44.5 to **0.44.6** on 2021-02-03
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.3.1 to **1.3.2** on 2021-02-04

## [4.26.1] - 2021-01-29

- Fixes
  - Prevent `unexpected token` error using mega-linter-runner on old versions of node
  - [#293](https://github.com/megalinter/megalinter/issues/293) Fix CI for PR from forked repositories
  - [#295](https://github.com/megalinter/megalinter/issues/295) Fix crash when .cspell.json is not parseable (wrong JSON format)
  - [#311](https://github.com/megalinter/megalinter/issues/295) Add java in salesforce flavor descriptor because it is used by Apex PMD

- Linter versions upgrades
  - [phpstan](https://phpstan.org/) from 0.12.68 to **0.12.69** on 2021-01-24
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.44.4 to **0.44.5** on 2021-01-25
  - [golangci-lint](https://golangci-lint.run/) from 1.35.2 to **1.36.0** on 2021-01-27
  - [protolint](https://github.com/yoheimuta/protolint) from 0.27.0 to **0.28.0** on 2021-01-27
  - [hadolint](https://github.com/hadolint/hadolint) from 1.19.0 to **1.20.0** on 2021-01-28
  - [phpstan](https://phpstan.org/) from 0.12.69 to **0.12.70** on 2021-01-28
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2020.09.09 to **2021.01.20** on 2021-01-28

## [4.26.0] - 2021-01-24

- Core architecture
  - Manage remote `mega-linter.yml` configuration files
  - New property **EXTENDS**, allowing to inherit from remote `mega-linter.yml` configuration files
  - Add docker-in-docker management (reuse running docker instance)
  - Allow to skip auto apply fixes with commit or PR if latest commit text contains `skip fix`
  - Provide new issue link to create a new flavor to improve performances

- Linters
  - Add [revive](https://github.com/mgechev/revive) GO linter
  - Add [SwiftLint](https://github.com/realm/SwiftLint) for Swift language
  - New Mega-Linter flavor **swift**
  - Get correct version for eslint-plugin-jsonc

- Linter versions upgrades
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.2.5 to **0.2.6** on 2021-01-22
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.3.0 to **1.3.1** on 2021-01-22
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 6.14.10 to **0.9.0** on 2021-01-24

## [4.25.0] - 2021-01-22

- Linters
  - Add SQL linter [sqlfluff](https://github.com/sqlfluff/sqlfluff)

- Fixes
  - [#269](https://github.com/megalinter/megalinter/issues/269) eslint: .eslintrc.yml is considered as found whereas it's not located in workspace root

- Linter versions upgrades
  - [stylelint](https://stylelint.io) from 13.8.0 to **13.9.0** on 2021-01-19
  - [markdown-table-formatter](https://www.npmjs.com/package/markdown-table-formatter) from 1.0.1 to **1.0.4** on 2021-01-19
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.2.0 to **1.3.0** on 2021-01-19
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.44.3 to **0.44.4** on 2021-01-19
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.1.1 to **7.0.4** on 2021-01-19
  - [sfdx-scanner](https://forcedotcom.github.io/sfdx-scanner/) from 2.4.0 to **2.5.1** on 2021-01-21
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.26.7 to **0.27.1** on 2021-01-22

## [4.24.1] - 2021-01-19

- mega-linter-runner --install
  - Create .jscpd.json file if copy-paste detection is activated
  - Display ending message

- Fixes
  - [#266](https://github.com/megalinter/megalinter/issues/266): shfmt error in python flavor, and reactivate BASH_SHFMT and DOCKERFILE_HADOLINT for own sources linting)

- Linter versions upgrades
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.1.0 to **7.1.1** on 2021-01-15
  - [eslint](https://eslint.org) from 7.17.0 to **7.18.0** on 2021-01-16
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 7.17.0 to **7.18.0** on 2021-01-16
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.9.24 to **0.9.25** on 2021-01-16
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 5.31.1 to **5.32.0** on 2021-01-16
  - [protolint](https://github.com/yoheimuta/protolint) from 0.26.1 to **0.27.0** on 2021-01-18
  - [phpstan](https://phpstan.org/) from 0.12.67 to **0.12.68** on 2021-01-19

## [4.24.0] - 2021-01-14

- Linters
  - Add [markdown-table-formatter](https://github.com/nvuillam/markdown-table-formatter)
  - Fix python error when CSpell found no errors

- Linter versions upgrades
  - [v8r](https://github.com/chris48s/v8r) from 0.4.0 to **0.5.0** on 2021-01-14
  - [phpstan](https://phpstan.org/) from 0.12.66 to **0.12.67** on 2021-01-14
  - [psalm](https://psalm.dev) from 4.3.1 to **Psalm.4.x-dev@** on 2021-01-14

## [4.23.3] - 2021-01-14

- Fix `.cspell.json` file updater

- Linter versions upgrades
  - [v8r](https://github.com/chris48s/v8r) from 0.4.0 to **0.5.0** on 2021-01-14

## [4.23.2] - 2021-01-14

- mega-linter-runner --install:
  - Fix `.mega-linter.yml` DISABLE property when nothing in it
  - Add default `.cspell.json` if spelling mistakes detector is activated

## [4.23.1] - 2021-01-12

- Core
  - Refactor part of Linter & reporters to manage correctly logs when linter cli_lint_mode is `project` or `list_of_files`
    - Generate ConsoleLinter and Text reports based from Linter.files_lint_results instead of at each loop
    - When TAP Reporter active, switch linters with cli_lint_mode == "list_of_files" to "files"
    - Fix linter output when cli_lint_mode == "list_of_files"
  - Decrease number of Dockerfile steps

## [4.23.0] - 2021-01-12

- Core
  - If the linter is a formatter, errors are not considered as blocking errors by default

- Linters
  - Add **prettier** to format Javascript and Typescript. **standard** remains default
  - Add **remark-lint** to check and fix Markdown files. **markdownlint** remains default

- Linter versions upgrades
  - [golangci-lint](https://golangci-lint.run/) from 1.35.1 to **1.35.2** on 2021-01-11
    - [golangci-lint](https://golangci-lint.run/) from 1.35.0 to **1.35.1** on 2021-01-11
    - [golangci-lint](https://golangci-lint.run/) from 1.34.1 to **1.35.0** on 2021-01-08
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.44.2 to **0.44.3** on 2021-01-09
  - [tflint](https://github.com/terraform-linters/tflint) from 0.23.0 to **0.23.1** on 2021-01-10
  - [dotenv-linter](https://dotenv-linter.github.io/) from 2.2.1 to **3.0.0** on 2021-01-11
    - Update Mega-Linter to call dotenv-linter v3 with `fix` and not `--fix` anymore
  - [phpstan](https://phpstan.org/) from 0.12.65 to **0.12.66** on 2021-01-11

## [4.22.1] - 2021-01-07

- Core
  - Improve `warning` status in logs
  - Remove timestamp at each log line

- Enhance integration with GitLab CI
  - Update configuration generator
  - Update core to clean logs when in GitLab CI context

## [4.22.0] - 2021-01-06

- Core
  - Allow user to configure custom scripts in `.mega-linter.yml` to run before and after linting, with variables `PRE_RUN` and `POST_RUN`
  - Fix wrong linter status bug
  - Enhance configuration variables performances
  - Rename XXX_FILE_NAME into XXX_CONFIG_FILE

- Linters
  - Add JSONC (json with comments) linting with eslint-plugin-jsonc

## [4.21.0] - 2021-01-03

- Linters
  - Add misspell spell checker
  - Allow to define cli_lint_errors_regex in descriptors to extract number of errors from linter output stdout
  - Call linters CLIs with list of files instead of once by file, to improve performances
    - eslint
    - markdownlint
    - pylint
    - flake8
    - isort

- Core
  - Implement architecture for Mega-Linter plugins
  - Count number of errors in linter logs with regexes (`cli_lint_errors_count` and `cli_lint_errors_regex` in descriptor files)
  - Cleanup unused legacy from Super-Linter

- Reports
  - Better icons for Console, GitHub Comment and Text reporters: ✅ ❌

- Documentation
  - Add Install button for VsCode IDE extensions when available
  - Add Install button for JetBrains IDEs extensions when available
  - Add a new page **All linters** listing all linters and references to Mega-Linter in their documentation
  - Add json-schema documentation generation and references

- CI
  - Use `quick build` and `TEST_KEYWORDS` in commit messages, to improve contributor experience

- Fixes
  - Upgrade .tflint default config to work with new tflint version

## [4.20.0] - 2020-12-28

- Flavors
  - Add **ci_light** flavor for only CI config files (Dockerfile,Jenkinsfile,JSON,YAML,XML)
  - Add **salesforce** flavor for Salesforce projects (DX or Metadata)
  - If all required linters are not in the current flavor, just skip them with a warning message

- Core
  - Add Json Schema for descriptors (allows validation and auto-completion from IDEs)
  - Add Json Schema for .mega-linter.yml configuration files

## [4.19.0] - 2020-12-27

- Installation
  - Add a yeoman generator in mega-linter-runner to initialize configuration in a repository: `npx mega-linter-runner --install`

- Linters
  - New linter v8r to validate json and yaml files with schemastore.org

## [4.18.0] - 2020-12-23

- Core
  - Do not suggest flavors when Mega-Linter validates only the diff files (`VALIDATE_ALL_CODE_BASE: false`)
  - Fix ConsoleReporter active linters table content
  - Check if linter is able to fix before flagging it as a fixing linter during runtime

- Flavors
  - New flavor: **documentation**

- Reporters
  - Support GitHub Enterprise for GitHub Comment Reporter
  - Support GitHub Enterprise for GitHub Status Reporter

- Doc
  - Add docker pulls badge in flavors documentation
  - Generate list of references to Mega-Linter

## [4.17.0] - 2020-12-18

- Core
  - Allow to use remote linters configuration files with LINTER_RULES_PATH
  - Add `.jekyll-cache` in the list of ignored folders by default
  - Arrange display of Flavor suggestions (text and order) in reporter logs
- Build
  - Dynamically generate (build.py) the list of flavors in github actions workflows
- Doc
  - Reorganize online documentation menus
- Linters
  - Add new linter git_diff to check for git conflicts markers
  - Fix rakudo installation
  - Fix phpstan installation

## [4.16.0] - 2020-12-14

- Flavored Mega-Linters
  - Generate lightweight docker images to improve Mega-Linter performances on some language based projects
  - During Mega-Linter run, suggest user to use a flavor and write it in reporters
  - Update descriptor YML files to define flavours
  - Update build.py to create one Dockerfile by Mega-Linter flavour & flavors documentation
  - New GHA workflows to build all flavoured Mega-Linters when pushing in master

- Fixes
  - Output reporter problems as warnings
  - Do not make Mega-Linter fail in case GitHubStatusReporter fails

- Doc
  - Rename "index" pages into more meaningful labels

## [4.15.0] - 2020-12-13

- Add Vue.js linting (eslint-plugin-vue added in dependencies)

- Configuration parameters changes:
  - Change config setting logic: `EXCLUDED_DIRECTORIES` is now replacing original directory list instead of extending it
  - Add config setting: `ADDITIONAL_EXCLUDED_DIRECTORIES` extends `EXCLUDED_DIRECTORIES` directory list
  - Add config setting: `&lt;LINTER_KEY&gt;_FILE_EXTENSIONS` to override corresponding value from linter descriptor file
  - Add config setting: `&lt;LINTER_KEY&gt;_FILE_NAMES_REGEX` to override corresponding value from linter descriptor file

- Descriptor yaml schema changes:
  - Rename `files_names_not_ends_with` to `file_names_not_ends_with`
  - Rename `files_names` to `files_names_regex` and change behavior to expect regular expressions in the list.
    They are applied using full match (i.e. the whole text should match the regular expression)

- Fix error message from Email Reporter when SMTP password is not set
- Fix automerge action yml (skip if secrets.PAT is not set)
- Improve caching of compiled regular expressions
- Override mkdocs theme to make analytics work

- CI
  - Auto update linters and documentation: Create update PR only if linter versions has been updated
  - Build and deploy docker images only when it is relevant (not in case of just documentation update for example)

## [4.14.2] - 2020-12-07

- Quick fix Github Comment Reporter
- Reorder linters for reports

## [4.14.1] - 2020-12-07

- Fixes
  - Fix python error when File.io does not respond, + harmonize reporter logs

## [4.14.0] - 2020-12-07

- Linters
  - Add Salesforce linter: sfdx-scanner

- Core architecture
  - Allow to call extra commands to build help content

## [4.13.0] - 2020-12-05

- Major updates in online documentation generation
  - Reorganize TOC
  - Generate individual pages from README sections and update their internal links targets
  - Open external links in a new browser tab

- New configuration parameters
  - Allow disabling printing alpaca image to console using PRINT_ALPACA config parameter
  - Support list of additional excluded directory basenames via EXCLUDED_DIRECTORIES configuration parameter

- New reporters:
  - Email reporter, to send mega-linter reports by mail if smtp server is configured
  - File.io reporter, to access reports with a file.io hyperlink

- Fixes
  - Fix markdown comments generator when build on Windows
  - Fix terrascan unit test case
  - Run some actions/steps only when PR is from same repository
  - Add comments in markdown generated by build.py
  - Fix boolean variables not taken in account in .mega-linter.yml config file

- Performance
  - Change way to install linters in Dockerfile (replace FROM ... COPY) by package or sh installation, to reduce the docker build steps from 93 to 87
    - shellcheck
    - editorconfig-checker
    - dotenv-linter
    - golangci-lint
    - kubeval

## [4.12.0] - 2020-11-29

- Performances
  - Update default workflow to get ride of has_updates action (replace by output `has_updated_files` from mega-linter github action)
  - Avoid duplicate runs in mega-linter.yml template and internal workflows, using [skip-duplicate-actions](https://github.com/fkirc/skip-duplicate-actions)
  - Give a proper name to each internal workflow
  - Fix issue about mkdirs failing

## [4.11.0] - 2020-11-29

- Manage parallel processing of linters to improve performances

## [4.10.1] - 2020-11-28

- Fallback to default behaviours instead of crashes when git not available

- mega-linter-runner
  - Allow to send env parameters to mega-linter-runner cli
  - Add examples in documentation
  - Publish mega-linter-runner beta version when pushing in master branch

## [4.10.0] - 2020-11-23

- Add link to linters rules index in documentation
- Remove ANSI color codes from log files
- Add performances by linter in console log
- New option **SHOW_ELAPSED_TIME** , allowing the number of seconds elapsed by linter in reports

- NPM package **Mega-Linter runner**
  - runs Mega-Linter locally, using .mega-linter.yml configuration (requires docker installed on your computer)
  - test cases added in CI

## [4.9.0] - 2020-11-23

- Core
  - Allow configuration to be defined in a `.mega-linter.yml` file

- Linters
  - Add Gherkin (Cucumber language) & gherkin-lint
  - Add RST linter : [rst-lint](https://github.com/twolfson/restructuredtext-lint)
  - Add RST linter : [rstcheck](https://github.com/myint/rstcheck)
  - Add RST formatter : [rstfmt](https://github.com/dzhu/rstfmt)
  - Activate formatting for BASH_SHFMT
  - Activate formatting for SNAKEMAKE_SNAKEFMT
  - JsCpd: remove copy-paste HTML folder when no abuse copy-paste has been found

- Logs
  - Store log files as artifacts during test cases
  - Add examples of success and failed linter logs in documentation
  - Remove `/tmp/lint` and `/github/workspace` from log files

- Documentation
  - Add list of supported IDE in each linter documentation
  - Generate GitHub card on linter doc when available
  - Store link preview info during build

## [4.8.0] - 2020-11-17

- New reporter: [Updated sources](https://megalinter.github.io/reporters/UpdatedSourcesReporter/)

## [4.7.1] - 2020-11-16

- Activate auto-fix for Groovy

## [4.7.0] - 2020-11-16

- Update markdown-link-check default config
- Add tip in documentation about .cspell.json generated by Mega-Linter
- Remove /tmp/lint from logs
- Improve summary table for linters in project mode (all project linted in one call, not one file by one file)
- Add Reporters in documentation, with screenshots
- New Mega-Linter variables to activate/deactivate/configure reporters

## [4.6.0] - 2020-11-13

- Automatic build of documentation with mkdocs-material
- Automatic deployment to [https://megalinter.github.io/](https://megalinter.github.io/)
- Add [markdown-link-check](https://github.com/tcort/markdown-link-check)

## [4.5.0] - 2020-11-11

- Add Visual Basic .NET language & dotnet-format
- Refactor removal of arguments for formatters (from custom class to Linter generic class)
- Perl: lint files with no extension containing Perl shebang
- Add automerge for PR issues from linter versions updates
- Fix ignored root files issue

## [4.4.0] - 2020-11-05

- Add Python [iSort](https://pycqa.github.io/isort/)
- Quick fix "PR Comment" reporter (orange light emoji)
- Refresh fork

## [4.3.2] - 2020-11-04

- Add spell checker **cspell**
- Add Github Action Workflow to automatically:
  - update linters dependencies
  - rebuild Mega-Linter documentation
  - create a PR with updates

- Apply fixes performed by linters:
  - User configuration (APPLY_FIXES vars)
  - Descriptors configuration: cli_lint_fix_arg_name set on linter in YML when it can format and/or auto-fix issues
  - Provide fixed files info in reports
  - Test cases for all fixable file types: sample_project_fixes
  - Generate README linters table with column "Fix"
  - Provide fix capability in linters docs
  - Update Workflows YMLs to create PR or commit to apply fixes

- Core Archi:
  - All linters now have a name different than descriptor_id
  - replace calls from os.path.exists to os.path.isfile and os.path.isdir

- Other:
  - fix Phive install
  - Upgrade linter versions & help

## [4.0.0] - 2020-10-01

- Initial version
