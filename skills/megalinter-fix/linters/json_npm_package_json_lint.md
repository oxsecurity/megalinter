# Fix JSON_NPM_PACKAGE_JSON_LINT errors

<!-- generated-descriptor-info-start -->
- Linter: **npm-package-json-lint** (MegaLinter key: `JSON_NPM_PACKAGE_JSON_LINT`)
- Descriptor: **JSON** (format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/json_npm_package_json_lint/>
- Official documentation: <https://npmpackagejsonlint.org/>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.npmpackagejsonlintrc.json` (custom path can be defined with `JSON_NPM_PACKAGE_JSON_LINT_CONFIG_FILE`)
- Ignore file: `.npmpackagejsonlintignore`
- Rules index: <https://npmpackagejsonlint.org/docs/rules>
- Rules configuration: <https://npmpackagejsonlint.org/docs/configuration>
- How to ignore files and directories: <https://npmpackagejsonlint.org/docs/ignore>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `JSON_NPM_PACKAGE_JSON_LINT` to fully disable this linter
  - `JSON_NPM_PACKAGE_JSON_LINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `JSON_NPM_PACKAGE_JSON_LINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `JSON_NPM_PACKAGE_JSON_LINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `JSON_NPM_PACKAGE_JSON_LINT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

npm-package-json-lint validates `package.json` files against configurable rules covering required properties, value types, formats, allowed values, dependency hygiene, scripts and property order. It has no auto-fix: edit the `package.json` manually according to the reported rule name.

- `require-*` errors (e.g. `require-name`, `require-version`, `require-description`, `require-license`, `require-author`): add the missing property to `package.json`.
- `*-type` errors (e.g. `name-type`, `version-type`, `dependencies-type`): change the value to the expected data type (string, object, array...).
- `*-format` errors (e.g. `name-format`, `version-format`, `description-format`): rewrite the value to the expected format (valid npm name, semver version...).
- `valid-values-*` errors (e.g. `valid-values-license`, `valid-values-engines`): replace the value with one of the values allowed by the project configuration.
- Dependency errors (e.g. `no-git-dependencies`, `no-absolute-version-dependencies`, `prefer-alphabetical-dependencies`): fix the version specifier or reorder the `dependencies` / `devDependencies` keys alphabetically.
- Structure errors (`prefer-property-order`, `no-duplicate-properties`): reorder top-level properties as configured and remove duplicated keys.

## Inline disable

npm-package-json-lint has no inline suppression mechanism (`package.json` is strict JSON and cannot carry disable comments). Instead, turn the rule off or downgrade it in the configuration file, optionally scoped to specific files with `overrides` (see below).

## Ignore via configuration

Set a rule severity to `"off"` (or `"warning"` to keep it non-blocking) in the configuration file, and use the `overrides` array to change rules only for matching `package.json` files (useful in monorepos):

```json
{
  "rules": {
    "require-author": "off",
    "valid-values-license": ["error", ["MIT", "Apache-2.0"]]
  },
  "overrides": [
    {
      "patterns": ["./packages/internal-*/package.json"],
      "rules": { "require-license": "off" }
    }
  ]
}
```

Shared configurations can be reused with `"extends": "npm-package-json-lint-config-default"`.

To skip whole files, list gitignore-style patterns in the ignore file at the project root (one pattern per line, e.g. `fixtures/**/package.json`), or point the CLI to another location with `--ignorePath`.

## When disabling is legitimate

- Fixture, template or test `package.json` files that intentionally violate rules: exclude them via the ignore file rather than weakening rules globally.
- Private or internal packages where publication-oriented rules (`require-license`, `require-author`, `valid-values-license`) do not apply: turn those rules off through `overrides`.
- Opinionated `prefer-*` rules (property order, alphabetical dependencies, no-peerDependencies) that conflict with a deliberate project convention: set them to `"off"` in the configuration.
- Prefer rule-level or file-level configuration in the linter itself; disabling at MegaLinter level (`DISABLE_LINTERS`, `..._DISABLE_ERRORS`, `..._FILTER_REGEX_EXCLUDE`) is the last resort.
