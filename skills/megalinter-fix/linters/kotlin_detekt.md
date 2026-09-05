# Fix KOTLIN_DETEKT errors

<!-- generated-descriptor-info-start -->
- Linter: **detekt** (MegaLinter key: `KOTLIN_DETEKT`)
- Descriptor: **KOTLIN** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/kotlin_detekt/>
- Official documentation: <https://detekt.dev/>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `detekt-config.yml` (custom path can be defined with `KOTLIN_DETEKT_CONFIG_FILE`)
- Rules index: <https://detekt.dev/docs/rules/comments>
- Rules configuration: <https://detekt.dev/configurations.html>
- How to disable rules inline: <https://detekt.dev/suppressing-rules.html>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `KOTLIN_DETEKT` to fully disable this linter
  - `KOTLIN_DETEKT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `KOTLIN_DETEKT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `KOTLIN_DETEKT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `KOTLIN_DETEKT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

detekt is a static code analyzer for Kotlin that reports code smells grouped into rule sets: `comments`, `complexity`, `coroutines`, `empty-blocks`, `exceptions`, `naming`, `performance`, `potential-bugs` and `style`. There is no auto-fix in MegaLinter: fix each finding manually according to its rule set.

- `complexity` (e.g. `LongMethod`, `TooManyFunctions`): extract helper functions or classes to reduce size and nesting.
- `style` (e.g. `MagicNumber`, `WildcardImport`, `MaxLineLength`, `VarCouldBeVal`): replace magic numbers with named constants, expand wildcard imports into explicit ones, wrap long lines, turn `var` into `val` when never reassigned.
- `potential-bugs` and `exceptions`: address the reported logic issue (e.g. handle or narrow caught exceptions, never leave empty catch blocks).
- `empty-blocks`: remove the empty block or add the intended implementation/comment.
- `naming`: rename identifiers to match the configured patterns.

Read the rule description in the rules index to understand the intent before changing code. If the project uses a custom config, remember detekt ignores default values unless `--build-upon-default-config` is set.

## Inline disable

Use Kotlin's `@Suppress` annotation with the rule ID, optionally prefixed with `detekt:` and/or the rule set:

```kotlin
@Suppress("detekt:MagicNumber")
fun retryDelay() = 4200L

@file:Suppress("TooManyFunctions") // file-level, at the top of the file
```

Accepted formats: `"MagicNumber"`, `"style:MagicNumber"`, `"detekt:MagicNumber"`, `"detekt:style:MagicNumber"`, `"detekt.style.MagicNumber"`, a whole rule set (`"style"`), or `"detekt:all"`. Prefer the `detekt:` prefix to avoid clashing with compiler suppressions.

## Ignore via configuration

Disable a rule or a whole rule set, or exclude paths per rule, in the YAML configuration file:

```yaml
complexity:
  TooManyFunctions:
    active: false
style:
  MagicNumber:
    excludes: ['**/test/**', '**/generated/**']
empty-blocks:
  active: false   # disables the whole rule set
```

Rule properties (thresholds, patterns) can also be tuned instead of disabling, e.g. `thresholdInFiles: 20`. For legacy codebases, generate a baseline file with `detekt --create-baseline --baseline baseline.xml` so only new findings are reported; false positives can be recorded under `ManuallySuppressedIssues` in that XML file.

## When disabling is legitimate

- False positives on the reported rule: suppress inline with a `detekt:` prefixed `@Suppress`, or record them in the baseline's `ManuallySuppressedIssues` to keep the code clean.
- Generated code or vendored sources: exclude their paths with per-rule `excludes` globs rather than deactivating rules globally.
- Test code where thresholds and magic numbers are intentional: exclude `**/test/**` folders on the noisy rules.
- Legacy codebases adopting detekt incrementally: use the baseline mechanism instead of disabling rules.

Disabling the linter at MegaLinter level (`DISABLE_LINTERS` or `KOTLIN_DETEKT_DISABLE_ERRORS`) is the last resort.
