# Fix CSS_STYLELINT errors

<!-- generated-descriptor-info-start -->
- Linter: **stylelint** (MegaLinter key: `CSS_STYLELINT`)
- Descriptor: **CSS** (format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/css_stylelint/>
- Official documentation: <https://stylelint.io>
- Auto-fix support: **yes** — add `CSS_STYLELINT` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter CSS_STYLELINT --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `.stylelintrc.json` (custom path can be defined with `CSS_STYLELINT_CONFIG_FILE`)
- Rules index: <https://stylelint.io/user-guide/rules/list>
- Rules configuration: <https://stylelint.io/user-guide/configure>
- How to disable rules inline: <https://stylelint.io/user-guide/ignore-code>
- Error line format (regex): `([0-9]+) errors`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `CSS_STYLELINT` to fully disable this linter
  - `CSS_STYLELINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `CSS_STYLELINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `CSS_STYLELINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `CSS_STYLELINT_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `CSS_STYLELINT_ERROR_PLUGIN_NOT_FOUND`
  - `CSS_STYLELINT_ERROR_CONFIG_NOT_FOUND`
  - `CSS_STYLELINT_ERROR_CUSTOM_SYNTAX_NOT_FOUND`
  - `CSS_STYLELINT_ERROR_NO_CONFIG`
<!-- generated-descriptor-info-end -->

## Fix instructions

stylelint checks CSS (and, via custom syntaxes, SCSS/Less) against 100+ rules split into two families: "avoid errors" (invalid syntax, duplicates, empty blocks, unknown properties/functions/selectors) and "enforce conventions" (notation, naming patterns, specificity and nesting limits).

- Run the auto-fix first: many rules are fixable (`stylelint --fix "**/*.css"`, or use the MegaLinter auto-fix described above). `--fix` defaults to `strict` (fixes only when the file has no syntax errors); pass `--fix=lax` to fix as much as possible despite syntax errors.
- For "avoid errors" rules, treat each report as a real bug: remove duplicate declarations, delete empty blocks, correct unknown property/function/selector names.
- For notation rules (e.g. `color-hex-length`, `color-function-notation`), rely on the auto-fix rather than editing by hand.
- For pattern rules (e.g. `selector-class-pattern`), rename the selector to match the configured convention — these are not auto-fixable.
- For `no-descending-specificity`, reorder rules so lower-specificity selectors come first, or restructure the selectors.
- For `declaration-no-important`, remove `!important` and raise the selector's specificity or fix the cascade order instead.
- For limit rules (`max-nesting-depth` and similar), flatten nesting or split the selector.

## Inline disable

Use stylelint comment directives, optionally scoped to specific rules and with a `--` description:

```css
#id {
  /* stylelint-disable-next-line declaration-no-important -- overrides vendor CSS */
  color: pink !important;
}

.legacy { color: pink !important; } /* stylelint-disable-line declaration-no-important */

/* stylelint-disable selector-max-id, declaration-no-important */
#id { color: pink !important; }
/* stylelint-enable selector-max-id, declaration-no-important */
```

A bare `/* stylelint-disable */` (until `/* stylelint-enable */` or end of file) turns off all rules — always prefer scoping to named rules on a single line.

## Ignore via configuration

In the configuration file, set a rule to `null` to turn it off, tune its secondary options, or downgrade it to a warning; use `ignoreFiles` and `overrides` to scope:

```json
{
  "extends": "stylelint-config-standard",
  "rules": {
    "selector-class-pattern": null,
    "number-max-precision": [2, { "severity": "warning" }]
  },
  "ignoreFiles": ["dist/**", "**/*.min.css"],
  "overrides": [
    { "files": ["*.scss"], "customSyntax": "postcss-scss" }
  ]
}
```

A `.stylelintignore` file (gitignore syntax, e.g. `vendor/**/*.css`) excludes whole files; an alternate path can be given with `--ignore-path`. Set `"reportNeedlessDisables": true` in the configuration to flag disable comments that no longer suppress anything.

## When disabling is legitimate

- Minified, vendored, or generated stylesheets (build output, third-party libraries) — exclude the files rather than disabling rules.
- Stylistic pattern rules (`selector-class-pattern`, notation choices) that conflict with an established project convention such as BEM — override the rule in the configuration with the project's pattern, or set it to `null`.
- `no-descending-specificity` false positives in files where source order is intentional (e.g. utility layers) — disable inline with a `--` description.
- SCSS/Less files reported as syntax errors because no `customSyntax` is configured — fix the configuration (`overrides` + `postcss-scss`) instead of disabling the linter.
- Disabling at MegaLinter level (`DISABLE_LINTERS` / `CSS_STYLELINT_DISABLE_ERRORS`) is the last resort — prefer fixing, then rule/file scoping in the stylelint configuration.
