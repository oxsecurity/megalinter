# Fix SWIFT_SWIFTLINT errors

<!-- generated-descriptor-info-start -->
- Linter: **swiftlint** (MegaLinter key: `SWIFT_SWIFTLINT`)
- Descriptor: **SWIFT** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/swift_swiftlint/>
- Official documentation: <https://github.com/realm/SwiftLint>
- Auto-fix support: **yes** — add `SWIFT_SWIFTLINT` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter SWIFT_SWIFTLINT --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `.swiftlint.yml` (custom path can be defined with `SWIFT_SWIFTLINT_CONFIG_FILE`)
- Rules index: <https://realm.github.io/SwiftLint/rule-directory.html>
- Rules configuration: <https://github.com/realm/SwiftLint#configuration>
- How to disable rules inline: <https://github.com/realm/SwiftLint#disable-rules-in-code>
- Error line format (regex): `Found ([0-9]+) violations`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `SWIFT_SWIFTLINT` to fully disable this linter
  - `SWIFT_SWIFTLINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `SWIFT_SWIFTLINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `SWIFT_SWIFTLINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `SWIFT_SWIFTLINT_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `SWIFT_SWIFTLINT_ERROR_INVALID_CONFIG`
  - `SWIFT_SWIFTLINT_ERROR_NO_LINTABLE_FILES`
  - `SWIFT_SWIFTLINT_ERROR_CUSTOM_RULE_REGEX`
<!-- generated-descriptor-info-end -->

## Fix instructions

SwiftLint enforces Swift style and conventions with 200+ rules (loosely based on the
archived GitHub Swift Style Guide), covering formatting, naming, safety and complexity.

- Run `swiftlint --fix` (or MegaLinter auto-fix) first: it rewrites files in place and
  resolves most formatting violations (`trailing_whitespace`, `comma`, `colon`,
  `opening_brace`/`closing_brace`, `trailing_newline`, ...). Commit before running it,
  since files on disk are overwritten.
- Safety rules are not auto-correctable — fix them by hand: replace `as!` with `as?`
  plus unwrapping (`force_cast`), replace `try!` with `do/try/catch` or `try?`
  (`force_try`).
- Naming rules (`identifier_name`, `type_name`): rename to lowerCamelCase identifiers
  and UpperCamelCase types within the configured length bounds.
- Metrics rules (`line_length`, `file_length`, `function_body_length`,
  `cyclomatic_complexity`, `nesting`, `function_parameter_count`): split long
  lines/functions/files, extract helpers, group parameters into a struct.
- Look up any unfamiliar rule in the rule directory (link above) — each page shows
  triggering and non-triggering examples.

## Inline disable

Use `// swiftlint:disable <rule1> [<rule2> ...]` and re-enable with
`// swiftlint:enable <rule1> ...`; without a matching `enable`, the disable lasts until
the end of the file. Scoped variants: `// swiftlint:disable:next <rule>`,
`// swiftlint:disable:this <rule>`, `// swiftlint:disable:previous <rule>`.
`all` disables every rule.

```swift
// swiftlint:disable:next force_cast
let cell = tableView.dequeueReusableCell(withIdentifier: "id") as! MyCell

// swiftlint:disable force_try
let data = try! Data(contentsOf: url)
// swiftlint:enable force_try
```

## Ignore via configuration

In the configuration file, disable rules with `disabled_rules`, restrict the active set
with `only_rules`, enable extra rules with `opt_in_rules`, and exclude paths with
`excluded` (case-sensitive, supports wildcards, takes precedence over `included`).
Severity can be lowered per rule instead of disabling it.

```yaml
disabled_rules:
  - trailing_whitespace
excluded:
  - Carthage
  - Pods
  - Sources/Generated/*.swift
line_length: 130
force_cast: warning # error by default
```

There is no separate ignore file: all exclusions live in the configuration file.
Nested configuration files in subdirectories are used as child configs for the files
below them.

## When disabling is legitimate

- Generated or vendored Swift sources (SwiftGen/Sourcery output, `Pods`, `Carthage`):
  exclude the paths rather than fixing code you do not own.
- Test code that intentionally uses `force_cast`/`force_try` for brevity, where a crash
  is an acceptable test failure — prefer a scoped inline disable or a nested config.
- Metrics thresholds (`line_length`, `function_body_length`) that conflict with an
  established team style — raise the limit in configuration instead of disabling the
  rule.
- Opt-in or analyzer rules producing false positives on valid API usage — disable that
  single rule, not the linter.

Disabling the whole linter at MegaLinter level is the last resort — prefer fixing,
inline disables, or configuration-level exclusions.
