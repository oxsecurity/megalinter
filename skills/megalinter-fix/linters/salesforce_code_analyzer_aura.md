# Fix SALESFORCE_CODE_ANALYZER_AURA errors

<!-- generated-descriptor-info-start -->
- Linter: **code-analyzer-aura** (MegaLinter key: `SALESFORCE_CODE_ANALYZER_AURA`)
- Descriptor: **SALESFORCE** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/salesforce_code_analyzer_aura/>
- Official documentation: <https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/get-started.html>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `code-analyzer.yml` (custom path can be defined with `SALESFORCE_CODE_ANALYZER_AURA_CONFIG_FILE`)
- Rules index: <https://github.com/forcedotcom/eslint-plugin-aura#rules>
- Rules configuration: <https://eslint.org/docs/latest/use/configure>
- How to disable rules inline: <https://eslint.org/docs/latest/use/configure/rules#disabling-rules>
- Error line format (regex): `Found ([0-9]+) violation\(s\)`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `SALESFORCE_CODE_ANALYZER_AURA` to fully disable this linter
  - `SALESFORCE_CODE_ANALYZER_AURA_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `SALESFORCE_CODE_ANALYZER_AURA_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `SALESFORCE_CODE_ANALYZER_AURA_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `SALESFORCE_CODE_ANALYZER_AURA_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `SALESFORCE_CODE_ANALYZER_AURA_ERROR_CONFIG_INVALID`
  - `SALESFORCE_CODE_ANALYZER_AURA_ERROR_NO_TARGET_FILES`
<!-- generated-descriptor-info-end -->

## Fix instructions

This linter runs the ESLint engine of Salesforce Code Analyzer with `@salesforce/eslint-plugin-aura` rules
on Aura component JavaScript (controllers, helpers, renderers). Reproduce findings locally with the
Salesforce CLI plugin (`sf code-analyzer run`) or the VS Code extension before editing.

Fix the most common rule families as follows:

- `aura-api`: use only documented Aura framework (`$A`) APIs; remove calls to undocumented or private members.
- `no-deprecated-aura-error`: stop calling `$A.error(...)`; replace it with supported error handling.
- `no-deprecated-component-creation` / `no-deprecated-event-creation`: replace the deprecated component or
  event creation methods flagged by the rule with their current, non-deprecated equivalents.
- `getevt-markup-prefix`: add the `markup://` prefix to event names passed to `$A.getEvt()`.
- Locker rules (`ecma-intrinsics`, `secure-document`, `secure-window`): restrict code to the public APIs
  exposed by Lightning Locker's secure wrappers; remove direct access to blocked globals or intrinsics.

There is no auto-fix: apply each change manually, then re-run the analyzer until it reports `Found 0 violation(s)`.

## Inline disable

Code Analyzer v5 uses its own suppression markers, not plain ESLint `eslint-disable` comments.
Place the marker in a comment above the code block:

```javascript
// Code-analyzer-suppress(eslint:no-deprecated-aura-error)
handleLegacyError: function (component, message) {
    $A.error(message);
}
```

Selector variants: `Code-analyzer-suppress(all)`, `(eslint)` for the whole engine, `(eslint:rule-name)` for
one rule. Re-enable later in the file with `// Code-analyzer-unsuppress(eslint:rule-name)`.

## Ignore via configuration

Disable a rule globally, or suppress it for specific files, in the configuration file:

```yaml
rules:
  eslint:
    no-deprecated-aura-error:
      disabled: true

suppressions:
  "aura/legacyCmp/legacyCmpHelper.js":
    - rule_selector: "eslint:aura-api"
      reason: "Legacy component - LWC migration planned"
```

Rules can also be kept active with lowered `severity` (e.g. `Info`) or different `tags` instead of being
disabled. To use your own ESLint setup, point the engine to it with `engines: > eslint: >
eslint_config_file: .eslintrc.json`. There is no dedicated ignore file: use `suppressions` entries or the
MegaLinter exclude regex variable for path-based exclusion.

## When disabling is legitimate

- Third-party or vendored Aura code bundled in the repository that you do not maintain.
- Legacy components scheduled for migration to LWC, where rewriting deprecated `$A` calls is planned as a
  separate effort (prefer a `suppressions` entry with a `reason` over a global disable).
- Locker rule findings on APIs you have verified work under your org's Lightning Locker configuration.
- Disabling the linter at MegaLinter level is the last resort: prefer inline suppression markers or
  `code-analyzer.yml` rules/suppressions first.
