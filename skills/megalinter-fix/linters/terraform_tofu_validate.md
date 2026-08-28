# Fix TERRAFORM_TOFU_VALIDATE errors

<!-- generated-descriptor-info-start -->
- Linter: **tofu-validate** (MegaLinter key: `TERRAFORM_TOFU_VALIDATE`)
- Descriptor: **TERRAFORM** (tooling_format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/terraform_tofu_validate/>
- Official documentation: <https://opentofu.org/docs/cli/commands/validate/>
- Auto-fix support: no (errors must be fixed manually)
- Rules index: <https://opentofu.org/docs/cli/commands/validate/>
- How to disable rules inline: <https://opentofu.org/docs/language/expressions/custom-conditions/>
- Error line format (regex): `Error:`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `TERRAFORM_TOFU_VALIDATE` to fully disable this linter
  - `TERRAFORM_TOFU_VALIDATE_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `TERRAFORM_TOFU_VALIDATE_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `TERRAFORM_TOFU_VALIDATE_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `TERRAFORM_TOFU_VALIDATE_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `TERRAFORM_TOFU_VALIDATE_ERROR_PROVIDER_UNAVAILABLE`
  - `TERRAFORM_TOFU_VALIDATE_ERROR_MODULE_NOT_INSTALLED`
  - `TERRAFORM_TOFU_VALIDATE_ERROR_MODULE_DOWNLOAD_FAILED`
  - `TERRAFORM_TOFU_VALIDATE_ERROR_UNREADABLE_MODULE_DIRECTORY`
  - `TERRAFORM_TOFU_VALIDATE_ERROR_INCONSISTENT_LOCK_FILE`
<!-- generated-descriptor-info-end -->

<!-- needs-enrichment -->

## Fix instructions

No researched fix instructions are available yet for tofu-validate.
Use the documentation links of the section above to:

- understand each reported rule before changing code
- apply the linter auto-fix option when available and safe
- disable a rule inline or in the linter configuration file only when fixing is not relevant
