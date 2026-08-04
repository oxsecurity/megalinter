# Fix JAVASCRIPT_ES errors

<!-- generated-descriptor-info-start -->
- Linter: **eslint** (MegaLinter key: `JAVASCRIPT_ES`)
- Descriptor: **JAVASCRIPT** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/javascript_eslint/>
- Official documentation: <https://eslint.org>
- Auto-fix support: **yes** — add `JAVASCRIPT_ES` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter JAVASCRIPT_ES --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `eslint.config.js` (custom path can be defined with `JAVASCRIPT_ES_CONFIG_FILE`)
- Rules index: <https://eslint.org/docs/latest/rules/>
- Rules configuration: <https://eslint.org/docs/latest/use/configure>
- How to disable rules inline: <https://eslint.org/docs/latest/use/configure/rules#disabling-rules>
- How to ignore files and directories: <https://eslint.org/docs/latest/use/configure/ignore#the-eslintignore-file>
- Error line format (regex): `✖ ([0-9]+) problem`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `JAVASCRIPT_ES` to fully disable this linter
  - `JAVASCRIPT_ES_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `JAVASCRIPT_ES_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `JAVASCRIPT_ES_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `JAVASCRIPT_ES_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `JAVASCRIPT_ES_ERROR_PLUGIN_NOT_FOUND`
  - `JAVASCRIPT_ES_ERROR_CONFIG_NOT_FOUND`
  - `JAVASCRIPT_ES_ERROR_PARSER_NOT_FOUND`
  - `JAVASCRIPT_ES_ERROR_FLAT_CONFIG_MODULE_NOT_FOUND`
  - `JAVASCRIPT_ES_ERROR_OUT_OF_MEMORY`
<!-- generated-descriptor-info-end -->

## Fix instructions

ESLint statically analyzes JavaScript for possible problems (logic errors), suggestions
(better coding patterns), and layout/formatting issues. Fix by error category:

- Auto-fixable rules (marked with a wrench in the rules index): run `eslint --fix`
  (or the MegaLinter auto-fix option from the section above) and review the diff.
  Most layout/formatting and many suggestion rules are corrected this way.
- Correctness rules ("possible problems") usually need a manual fix — change the logic,
  never silence them blindly:
  - `no-unused-vars`: delete the unused variable, import, or parameter, or actually use it.
  - `no-undef`: declare or import the missing identifier; for genuine runtime globals,
    register them in the configuration (`languageOptions.globals` in flat config,
    `globals`/`env` in legacy `.eslintrc.*`) instead of disabling the rule.
- Plugin rules are namespaced with the plugin prefix (e.g. `import/order`,
  `@typescript-eslint/no-explicit-any`): look up the rule in that plugin's own
  documentation; ordering/style plugin rules are often auto-fixable with `--fix`.
- Rules can also carry manual editor suggestions (lightbulb icon) that are not applied
  by `--fix`; apply those changes by hand.

## Inline disable

Reference: <https://eslint.org/docs/latest/use/configure/rules#disabling-rules>. Always
name the rule(s) — a bare `eslint-disable` disables everything. Add a reason after `--`.

```javascript
// eslint-disable-next-line no-alert -- user-facing confirmation required here
alert("foo");
alert("bar"); // eslint-disable-line no-alert, no-console

/* eslint-disable no-console */
console.log("debug section");
/* eslint-enable no-console */
```

A `/* eslint-disable no-alert */` block comment at the top of a file (without a matching
`eslint-enable`) disables the rule for the whole file.

## Ignore via configuration

Turn a rule off, or tune it per file glob. Flat config (`eslint.config.js`):

```javascript
import { defineConfig, globalIgnores } from "eslint/config";
export default defineConfig([
  globalIgnores(["dist/", "**/*.min.js"]),
  { rules: { eqeqeq: "off", "prefer-const": ["error", { ignoreReadBeforeAssign: true }] } },
  { files: ["test/**/*"], rules: { "no-console": "off" } },
]);
```

Legacy `.eslintrc.*` equivalents: same `rules` object, per-glob blocks go in an
`overrides` array (`{ files: ["test/**/*"], rules: { ... } }`), and files are excluded
via an `ignorePatterns` property or a `.eslintignore` file (one gitignore-style pattern
per line, e.g. `config/*`). Note flat config needs a `**/` prefix to match a bare file
name anywhere (`**/temp.js`), and directories are ignored with a trailing slash.

## When disabling is legitimate

- Generated, vendored, or minified code you do not maintain: ignore the paths in the
  ESLint config (or `JAVASCRIPT_ES_FILTER_REGEX_EXCLUDE`) rather than disabling rules.
- A rule conflicts with a formatter or another tool that owns that concern (e.g. Prettier
  handling layout): turn the layout rule off in the shared config for the whole repo.
- A documented false positive or intentional exception: prefer a single
  `eslint-disable-next-line <rule> -- reason` over widening the configuration.
- Disable the linter at MegaLinter level (`DISABLE_LINTERS` /
  `JAVASCRIPT_ES_DISABLE_ERRORS`) only as a last resort, e.g. while migrating a legacy
  codebase where per-rule cleanup is planned but not yet done.
