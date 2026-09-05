# Fix GHERKIN_GHERKIN_LINT errors

<!-- generated-descriptor-info-start -->
- Linter: **gherkin-lint** (MegaLinter key: `GHERKIN_GHERKIN_LINT`)
- Descriptor: **GHERKIN** (tooling_format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/gherkin_gherkin_lint/>
- Official documentation: <https://github.com/gherkin-lint/gherkin-lint>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.gherkin-lintrc` (custom path can be defined with `GHERKIN_GHERKIN_LINT_CONFIG_FILE`)
- Rules index: <https://github.com/gherkin-lint/gherkin-lint#available-rules>
- Rules configuration: <https://github.com/gherkin-lint/gherkin-lint#rule-configuration>
- How to disable rules inline: <https://github.com/gherkin-lint/gherkin-lint#ignoring-feature-files>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `GHERKIN_GHERKIN_LINT` to fully disable this linter
  - `GHERKIN_GHERKIN_LINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `GHERKIN_GHERKIN_LINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `GHERKIN_GHERKIN_LINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `GHERKIN_GHERKIN_LINT_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `GHERKIN_GHERKIN_LINT_ERROR_CONFIG_INVALID`
<!-- generated-descriptor-info-end -->

## Fix instructions

gherkin-lint parses `.feature` files with the Gherkin parser and reports structural and style violations. There is no auto-fix: edit the feature files manually.

Fix strategy by error category:

- Parse/structure errors (always-on rules): keep exactly one `Feature:` per file (`one-feature-per-file`), at most one `Background:` per file (`up-to-one-background-per-file`), remove tags placed on a `Background:` (`no-tags-on-backgrounds`), and split multiline steps into separate steps (`no-multiline-steps`).
- Whitespace and layout: delete trailing spaces (`no-trailing-spaces`), re-indent `Feature`/`Scenario`/steps to the configured column offsets (`indentation`), and add or remove the final newline as required (`new-line-at-eof`).
- Naming: give every `Feature:` and `Scenario:` a name (`no-unnamed-features`), deduplicate names across files (`no-dupe-feature-names`, `no-dupe-scenario-names`), shorten names over the configured limit (`name-length`), and rename files to the configured style such as `PascalCase` or `kebab-case` (`file-name`).
- Content rules: reorder steps into Given/When/Then sequence (`keywords-in-logical-order`), add an `Examples:` table to every `Scenario Outline` (`no-scenario-outlines-without-examples`), remove or replace forbidden text (`no-restricted-patterns`), and split large scenarios or files (`scenario-size`, `max-scenarios-per-file`).
- Tag rules: remove tags outside the allowed list (`allowed-tags`), remove forbidden tags like `@wip` (`no-restricted-tags`), and add the mandated tag pattern to each scenario (`required-tags`).

Reproduce locally with `gherkin-lint -c .gherkin-lintrc path/to/features` to iterate quickly.

## Inline disable

gherkin-lint has no inline suppression comments inside `.feature` files. To exempt a file, add its glob to the `.gherkin-lintignore` file or turn the rule off in the configuration file (see below); the `-i`/`--ignore` CLI option (comma-separated globs) also skips files and overrides the ignore file.

## Ignore via configuration

The configuration file is a JSON map of rule names to `"on"`/`"off"` (or `["on", {options}]` for rules with options):

```json
{
  "no-unnamed-features": "off",
  "indentation": ["on", {"Feature": 0, "Step": 2}],
  "no-restricted-tags": ["on", {"tags": ["@watch", "@wip"]}]
}
```

To exclude files entirely, create a `.gherkin-lintignore` file with one glob pattern per line:

```text
features/legacy/**
**/generated-*.feature
```

## When disabling is legitimate

- Generated or vendored feature files (e.g. exported from a BDD management tool) that will be regenerated: exclude them via `.gherkin-lintignore` rather than editing them.
- Team conventions that intentionally diverge, such as a different indentation scheme or file naming style: configure the rule's options instead of fighting each finding.
- Legacy suites with pervasive duplicate scenario names where renaming would break reporting or automation bindings: turn the `no-dupe-*` rules off until a planned cleanup.
- Tag policies (`required-tags`, `allowed-tags`) that conflict with tags consumed by your test runner: adjust the allowed/required patterns in the configuration.

Prefer fixing the feature files or tuning `.gherkin-lintrc`; disabling at MegaLinter level (`DISABLE_LINTERS`, `..._DISABLE_ERRORS`, filter regex) is the last resort.
