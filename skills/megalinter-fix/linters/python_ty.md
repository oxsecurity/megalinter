# Fix PYTHON_TY errors

<!-- generated-descriptor-info-start -->
- Linter: **ty** (MegaLinter key: `PYTHON_TY`)
- Descriptor: **PYTHON** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/python_ty/>
- Official documentation: <https://docs.astral.sh/ty/>
- Auto-fix support: **yes** — add `PYTHON_TY` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter PYTHON_TY --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `ty.toml` (custom path can be defined with `PYTHON_TY_CONFIG_FILE`)
- Rules index: <https://docs.astral.sh/ty/rules/>
- Rules configuration: <https://docs.astral.sh/ty/configuration/>
- How to disable rules inline: <https://docs.astral.sh/ty/configuration/#suppression>
- How to ignore files and directories: <https://docs.astral.sh/ty/configuration/#file-selection>
- Error line format (regex): `Found ([0-9]+) diagnostic`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `PYTHON_TY` to fully disable this linter
  - `PYTHON_TY_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `PYTHON_TY_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `PYTHON_TY_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `PYTHON_TY_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `PYTHON_TY_ERROR_CONFIG_PARSE`
  - `PYTHON_TY_ERROR_IMPORT_NOT_FOUND`
<!-- generated-descriptor-info-end -->

<!-- needs-enrichment -->

## Fix instructions

No researched fix instructions are available yet for ty.
Use the documentation links of the section above to:

- understand each reported rule before changing code
- apply the linter auto-fix option when available and safe
- disable a rule inline or in the linter configuration file only when fixing is not relevant
