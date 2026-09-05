# Fix GRAPHQL_BIOME errors

<!-- generated-descriptor-info-start -->
- Linter: **biome** (MegaLinter key: `GRAPHQL_BIOME`)
- Descriptor: **GRAPHQL** (format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/graphql_biome/>
- Official documentation: <https://biomejs.dev>
- Auto-fix support: **yes** — add `GRAPHQL_BIOME` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter GRAPHQL_BIOME --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `biome.json` (custom path can be defined with `GRAPHQL_BIOME_CONFIG_FILE`)
- Rules index: <https://biomejs.dev/linter/rules/>
- Rules configuration: <https://biomejs.dev/reference/configuration/>
- How to disable rules inline: <https://biomejs.dev/analyzer/suppressions/>
- Error line format (regex): `Found ([0-9]+) error`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `GRAPHQL_BIOME` to fully disable this linter
  - `GRAPHQL_BIOME_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `GRAPHQL_BIOME_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `GRAPHQL_BIOME_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `GRAPHQL_BIOME_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

<!-- needs-enrichment -->

## Fix instructions

No researched fix instructions are available yet for biome.
Use the documentation links of the section above to:

- understand each reported rule before changing code
- apply the linter auto-fix option when available and safe
- disable a rule inline or in the linter configuration file only when fixing is not relevant
