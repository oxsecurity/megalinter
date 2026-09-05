# Fix API_SPECTRAL errors

<!-- generated-descriptor-info-start -->
- Linter: **spectral** (MegaLinter key: `API_SPECTRAL`)
- Descriptor: **API** (tooling_format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/api_spectral/>
- Official documentation: <https://github.com/stoplightio/spectral>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.spectral.yaml` (custom path can be defined with `API_SPECTRAL_CONFIG_FILE`)
- Rules index: <https://docs.stoplight.io/docs/spectral/4dec24461f3af-open-api-rules>
- Rules configuration: <https://docs.stoplight.io/docs/spectral/9ffa04e052cc1-spectral-cli#using-a-ruleset-file>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `API_SPECTRAL` to fully disable this linter
  - `API_SPECTRAL_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `API_SPECTRAL_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `API_SPECTRAL_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `API_SPECTRAL_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `API_SPECTRAL_ERROR_RULESET_PARSE_FAILED`
  - `API_SPECTRAL_ERROR_FUNCTION_NOT_DEFINED`
  - `API_SPECTRAL_ERROR_RULESET_REF_UNREACHABLE`
<!-- generated-descriptor-info-end -->

<!-- needs-enrichment -->

## Fix instructions

No researched fix instructions are available yet for spectral.
Use the documentation links of the section above to:

- understand each reported rule before changing code
- apply the linter auto-fix option when available and safe
- disable a rule inline or in the linter configuration file only when fixing is not relevant
