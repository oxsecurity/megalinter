# Fix KOTLIN_KTLINT errors

<!-- generated-descriptor-info-start -->
- Linter: **ktlint** (MegaLinter key: `KOTLIN_KTLINT`)
- Descriptor: **KOTLIN** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/kotlin_ktlint/>
- Official documentation: <https://ktlint.github.io>
- Auto-fix support: **yes** — add `KOTLIN_KTLINT` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter KOTLIN_KTLINT --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Rules index: <https://ktlint.github.io/#rules>
- Rules configuration: <https://pinterest.github.io/ktlint/latest/rules/configuration-ktlint/>
- How to disable rules inline: <https://pinterest.github.io/ktlint/latest/faq/#how-do-i-suppress-errors-for-a-lineblockfile>
- Error line format (regex): `\s+[\w\-_]+:[\w\-_]+: ([0-9]+)`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `KOTLIN_KTLINT` to fully disable this linter
  - `KOTLIN_KTLINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `KOTLIN_KTLINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `KOTLIN_KTLINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `KOTLIN_KTLINT_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `KOTLIN_KTLINT_ERROR_OUT_OF_MEMORY`
  - `KOTLIN_KTLINT_ERROR_RULESET_NOT_FOUND`
<!-- generated-descriptor-info-end -->

## Fix instructions

ktlint is an anti-bikeshedding Kotlin linter and formatter: it enforces the official Kotlin
code style (indentation, spacing, wildcard imports, import ordering, max line length,
trailing commas, final newline...). Almost every violation is auto-fixable.

- Prefer the auto-fix path: enable MegaLinter auto-fix (see generated block above) or run
  `ktlint --format` (alias `ktlint -F`) locally to rewrite the files in place.
- For the few rules `--format` cannot fix automatically (e.g. some `max-line-length` or
  naming violations), edit the code manually: split long lines, rename identifiers, replace
  wildcard imports with explicit ones.
- Rule ids are qualified as `rule-set-id:rule-id` (e.g. `standard:no-wildcard-imports`);
  look each reported id up in the rules index to understand the expected style.
- Align the enforced style with the project by setting `ktlint_code_style` in
  `.editorconfig` (`ktlint_official`, `intellij_idea` or `android_studio`) instead of
  fighting individual rules.

## Inline disable

Since ktlint 0.50, suppression works only through `@Suppress` / `@SuppressWarnings`
annotations with rule ids prefixed by `ktlint:` — `ktlint-disable` comments are no longer
supported. Import statements cannot be annotated: use a file-level annotation for them.

```kotlin
// Suppress one rule on a declaration
@Suppress("ktlint:standard:max-line-length")
val foo = "some really loooooooooooooooooooong string exceeding the max line length"

// Suppress all ktlint rules on a construct
@Suppress("ktlint")
class Foo {}

// File level (required for import-related rules)
@file:Suppress("ktlint:standard:no-wildcard-imports")
```

## Ignore via configuration

ktlint is configured through `.editorconfig` sections. Disable an individual rule with
`ktlint_{ruleset-id}_{rule-id} = disabled`, or a whole rule set with
`ktlint_{ruleset-id} = disabled`; scope overrides to a directory with a glob section.

```ini
[*.{kt,kts}]
ktlint_code_style = ktlint_official
max_line_length = 120
ktlint_standard_import-ordering = disabled

[generated/**.{kt,kts}]
ktlint_standard = disabled
```

Do not put spaces inside the glob (`[*.{kt,kts}]`, not `[*.{kt, kts}]`) — sections with
spaces are silently ignored. ktlint has no dedicated ignore file; exclude files via such
per-path `.editorconfig` sections or with the MegaLinter filter variable listed above.

## When disabling is legitimate

- Generated Kotlin sources (protobuf, KSP/kapt output, OpenAPI clients): disable the
  `standard` rule set for those paths in `.editorconfig` rather than editing them.
- The project intentionally follows the IntelliJ IDEA or Android Studio style: set
  `ktlint_code_style` accordingly instead of suppressing rule-by-rule.
- A rule conflicts with a framework requirement (e.g. DSL naming or a mandatory wildcard
  import): use a targeted `@Suppress("ktlint:standard:<rule-id>")` on that declaration.
- ktlint itself documents suppression as an escape latch for the rare cases where it cannot
  produce a correct result — keep it rule-scoped and local.

Disabling the linter at MegaLinter level (`DISABLE_LINTERS`, `KOTLIN_KTLINT_DISABLE_ERRORS`)
is the last resort, after per-rule and per-path options are exhausted.
