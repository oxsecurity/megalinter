# Fix SPELL_TYPOS errors

<!-- generated-descriptor-info-start -->
- Linter: **typos** (MegaLinter key: `SPELL_TYPOS`)
- Descriptor: **SPELL** (other)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/spell_typos/>
- Official documentation: <https://github.com/crate-ci/typos>
- Auto-fix support: **yes** — add `SPELL_TYPOS` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter SPELL_TYPOS --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `typos.toml` (custom path can be defined with `SPELL_TYPOS_CONFIG_FILE`)
- Rules index: <https://github.com/crate-ci/typos/blob/main/docs/reference.md>
- Rules configuration: <https://github.com/crate-ci/typos/blob/main/docs/reference.md#configuration>
- How to disable rules inline: <https://github.com/crate-ci/typos/blob/main/docs/reference.md#defaultextend-ignore-re>
- How to ignore files and directories: <https://github.com/crate-ci/typos/blob/main/docs/reference.md#filesextend-exclude>
- Error line format (regex): `"type"\s*:\s*"typo"`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `SPELL_TYPOS` to fully disable this linter
  - `SPELL_TYPOS_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `SPELL_TYPOS_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `SPELL_TYPOS_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `SPELL_TYPOS_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

<!-- needs-enrichment -->

## Fix instructions

No researched fix instructions are available yet for typos.
Use the documentation links of the section above to:

- understand each reported rule before changing code
- apply the linter auto-fix option when available and safe
- disable a rule inline or in the linter configuration file only when fixing is not relevant
