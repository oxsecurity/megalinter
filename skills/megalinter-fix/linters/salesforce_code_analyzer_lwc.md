# Fix SALESFORCE_CODE_ANALYZER_LWC errors

<!-- generated-descriptor-info-start -->
- Linter: **code-analyzer-lwc** (MegaLinter key: `SALESFORCE_CODE_ANALYZER_LWC`)
- Descriptor: **SALESFORCE** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/salesforce_code_analyzer_lwc/>
- Official documentation: <https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/get-started.html>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `code-analyzer.yml` (custom path can be defined with `SALESFORCE_CODE_ANALYZER_LWC_CONFIG_FILE`)
- Rules index: <https://github.com/salesforce/eslint-plugin-lwc#rules>
- Rules configuration: <https://eslint.org/docs/latest/use/configure>
- How to disable rules inline: <https://eslint.org/docs/latest/use/configure/rules#disabling-rules>
- Error line format (regex): `Found ([0-9]+) violation\(s\)`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `SALESFORCE_CODE_ANALYZER_LWC` to fully disable this linter
  - `SALESFORCE_CODE_ANALYZER_LWC_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `SALESFORCE_CODE_ANALYZER_LWC_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `SALESFORCE_CODE_ANALYZER_LWC_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `SALESFORCE_CODE_ANALYZER_LWC_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `SALESFORCE_CODE_ANALYZER_LWC_ERROR_CONFIG_INVALID`
  - `SALESFORCE_CODE_ANALYZER_LWC_ERROR_NO_TARGET_FILES`
<!-- generated-descriptor-info-end -->

## Fix instructions

Salesforce Code Analyzer (eslint engine) runs `@lwc/eslint-plugin-lwc` rules on Lightning Web Components
JavaScript. Fix each violation according to its rule category:

- **LWC correctness** (`valid-api`, `valid-wire`, `no-deprecated`): correct decorator usage — public
  properties must be valid `@api` fields, `@wire` must target an adapter with proper config, and
  deprecated LWC APIs must be replaced by their documented successors.
- **Best practices** (`no-inner-html`, `no-leaky-event-listeners`): replace `innerHTML` assignments
  with `textContent` or template rendering, and remove event listeners you add (avoid anonymous
  handlers that cannot be removed).
- **SSR-specific** (`ssr-no-unsupported-properties` and similar): guard browser-only APIs so components
  stay server-side renderable.
- A few rules are ESLint auto-fixable (e.g. `consistent-component-name`); running ESLint directly with
  `--fix` on the component folder can resolve those, but MegaLinter itself applies no fix for this linter.

## Inline disable

The eslint engine honors standard ESLint inline comments; use the plugin-prefixed rule name:

```javascript
// eslint-disable-next-line @lwc/lwc/no-inner-html -- sanitized upstream
element.innerHTML = safeMarkup;
```

Variants: `/* eslint-disable @lwc/lwc/no-deprecated */` ... `/* eslint-enable @lwc/lwc/no-deprecated */`
for a block, or `// eslint-disable-line <rule>` at the end of the offending line. Always append a
`-- reason` description.

## Ignore via configuration

Disable a rule workspace-wide, or lower its severity, in the `rules` section of the configuration file:

```yaml
rules:
  eslint:
    "@lwc/lwc/no-inner-html":
      disabled: true
    "@lwc/lwc/no-deprecated":
      severity: Info
```

Tune the eslint engine itself in the `engines` section, e.g. point it at your project ESLint config or
let it discover one:

```yaml
engines:
  eslint:
    eslint_config_file: eslint.config.js
    auto_discover_eslint_config: true
```

With `eslint_config_file` or `auto_discover_eslint_config` set, file exclusions from your own ESLint
config and ignore files are applied. Keep the configuration file lean: only list the rules you
override, because its values take priority over engine-specific configs.

## When disabling is legitimate

- Compat-performance rules (e.g. `no-async-await`, `no-for-of`) target legacy browsers such as IE11;
  disable them when your org does not support those browsers.
- SSR-specific rules are irrelevant for components that will never be server-side rendered.
- `no-inner-html` on markup that is provably sanitized or built from static strings — prefer an inline
  disable with a justification over a global one.
- Generated or vendored JavaScript bundled inside an LWC folder that you do not maintain.

Disabling the whole linter at MegaLinter level (`DISABLE_LINTERS`) is the last resort — prefer
rule-level or file-level exclusions first.
