# Fix SALESFORCE_CODE_ANALYZER_APEXGURU errors

<!-- generated-descriptor-info-start -->
- Linter: **code-analyzer-apexguru** (MegaLinter key: `SALESFORCE_CODE_ANALYZER_APEXGURU`)
- Descriptor: **SALESFORCE** (language)
- MegaLinter documentation: <https://megalinter.io/10.1.0/descriptors/salesforce_code_analyzer_apexguru/>
- Official documentation: <https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/engine-apexguru.html>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `code-analyzer.yml` (custom path can be defined with `SALESFORCE_CODE_ANALYZER_APEXGURU_CONFIG_FILE`)
- Rules index: <https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/engine-apexguru.html>
- Rules configuration: <https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/config.html>
- Error line format (regex): `Found ([0-9]+) violation\(s\)`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `SALESFORCE_CODE_ANALYZER_APEXGURU` to fully disable this linter
  - `SALESFORCE_CODE_ANALYZER_APEXGURU_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `SALESFORCE_CODE_ANALYZER_APEXGURU_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `SALESFORCE_CODE_ANALYZER_APEXGURU_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `SALESFORCE_CODE_ANALYZER_APEXGURU_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `SALESFORCE_CODE_ANALYZER_APEXGURU_ERROR_CONFIG_INVALID`
  - `SALESFORCE_CODE_ANALYZER_APEXGURU_ERROR_NO_ORG`
  - `SALESFORCE_CODE_ANALYZER_APEXGURU_ERROR_ENGINE_SKIPPED`
  - `SALESFORCE_CODE_ANALYZER_APEXGURU_ERROR_NOT_ENABLED`
  - `SALESFORCE_CODE_ANALYZER_APEXGURU_ERROR_TIMEOUT`
<!-- generated-descriptor-info-end -->

<!-- needs-enrichment -->

## Fix instructions

No researched fix instructions are available yet for code-analyzer-apexguru.
Use the documentation links of the section above to:

- understand each reported rule before changing code
- apply the linter auto-fix option when available and safe
- disable a rule inline or in the linter configuration file only when fixing is not relevant
