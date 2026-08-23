# Fix TERRAFORM_TOFU_FMT errors

<!-- generated-descriptor-info-start -->
- Linter: **tofu-fmt** (MegaLinter key: `TERRAFORM_TOFU_FMT`)
- Descriptor: **TERRAFORM** (tooling_format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/terraform_tofu_fmt/>
- Official documentation: <https://opentofu.org/docs/cli/commands/fmt/>
- Auto-fix support: **yes** — add `TERRAFORM_TOFU_FMT` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter TERRAFORM_TOFU_FMT --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Rules configuration: <https://opentofu.org/docs/language/syntax/style/>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `TERRAFORM_TOFU_FMT` to fully disable this linter
  - `TERRAFORM_TOFU_FMT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `TERRAFORM_TOFU_FMT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `TERRAFORM_TOFU_FMT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `TERRAFORM_TOFU_FMT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

<!-- needs-enrichment -->

## Fix instructions

No researched fix instructions are available yet for tofu-fmt.
Use the documentation links of the section above to:

- understand each reported rule before changing code
- apply the linter auto-fix option when available and safe
- disable a rule inline or in the linter configuration file only when fixing is not relevant
