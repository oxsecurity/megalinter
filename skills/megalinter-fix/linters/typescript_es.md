# Fix TYPESCRIPT_ES errors

<!-- generated-descriptor-info-start -->
- Linter: **eslint** (MegaLinter key: `TYPESCRIPT_ES`)
- Descriptor: **TYPESCRIPT** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/typescript_eslint/>
- Official documentation: <https://typescript-eslint.io/>
- Auto-fix support: **yes** — add `TYPESCRIPT_ES` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter TYPESCRIPT_ES --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `eslint.config.js` (custom path can be defined with `TYPESCRIPT_ES_CONFIG_FILE`)
- Rules index: <https://typescript-eslint.io/rules/>
- Rules configuration: <https://typescript-eslint.io/getting-started/#configuration-values>
- How to disable rules inline: <https://eslint.org/docs/latest/use/configure/rules#disabling-rules>
- How to ignore files and directories: <https://eslint.org/docs/latest/use/configure/ignore#the-eslintignore-file>
- Error line format (regex): `✖ ([0-9]+) problem`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `TYPESCRIPT_ES` to fully disable this linter
  - `TYPESCRIPT_ES_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `TYPESCRIPT_ES_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `TYPESCRIPT_ES_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `TYPESCRIPT_ES_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `TYPESCRIPT_ES_ERROR_PLUGIN_NOT_FOUND`
  - `TYPESCRIPT_ES_ERROR_CONFIG_NOT_FOUND`
  - `TYPESCRIPT_ES_ERROR_PARSER_NOT_FOUND`
  - `TYPESCRIPT_ES_ERROR_FLAT_CONFIG_MODULE_NOT_FOUND`
  - `TYPESCRIPT_ES_ERROR_OUT_OF_MEMORY`
<!-- generated-descriptor-info-end -->

## Fix instructions

eslint with typescript-eslint lints TypeScript sources: code-quality and stylistic rules, plus type-aware rules that use the TypeScript type checker. Apply fixes per category:

- Auto-fixable rules (marked fixable in the rules index): run `eslint --fix` (or the MegaLinter auto-fix option above) before fixing anything by hand, then handle only the remaining errors.
- Type-aware rules (`*TypeChecked` presets): they require type information — configure `parserOptions.projectService: true` (or the older `parserOptions.project`) under `languageOptions` in `eslint.config.js`. A "parsing error about type information" means the file is not covered by the tsconfig, not a code bug: fix the config or tsconfig inclusion, do not touch the code.
- `@typescript-eslint/no-unused-vars`: delete the unused variable/import, or prefix intentionally unused names with `_` when `argsIgnorePattern`/`varsIgnorePattern` are set to `"^_"`. When enabling this rule, turn the base ESLint `no-unused-vars` off — it reports incorrect errors on TypeScript.
- `@typescript-eslint/no-explicit-any`: replace `any` with a specific interface/union type when the shape is known, otherwise with `unknown` and narrow before use. The optional `fixToUnknown` auto-fix is off by default because it can surface new type errors.
- `@typescript-eslint/ban-ts-comment`: remove `@ts-ignore`/`@ts-nocheck` and fix the underlying type error. If suppression is truly needed, use `// @ts-expect-error` followed by a description (at least 3 characters by default) on the same line.

## Inline disable

Use ESLint disable comments with the fully qualified rule name and a `--` justification:

```typescript
// eslint-disable-next-line @typescript-eslint/no-explicit-any -- third-party API has no types
function parse(payload: any): Config {
```

Variants: `// eslint-disable-line <rule>` on the offending line itself, or `/* eslint-disable <rule> */` ... `/* eslint-enable <rule> */` around a block. Note that `@ts-ignore` comments silence the TypeScript compiler, not ESLint — they do not remove ESLint errors and are themselves flagged by `ban-ts-comment`; prefer eslint-disable comments for lint findings.

## Ignore via configuration

In `eslint.config.js`, set a rule to `"off"` (or tune its options) globally, restrict overrides to a glob via `files`, and exclude paths with `globalIgnores()`:

```javascript
import { defineConfig, globalIgnores } from "eslint/config";

export default defineConfig([
  globalIgnores(["dist/", "**/*.generated.ts"]),
  {
    files: ["**/*.spec.ts"],
    rules: { "@typescript-eslint/no-explicit-any": "off" },
  },
]);
```

The legacy `.eslintignore` file is superseded by `globalIgnores()` in flat config; `--ignore-pattern` works on the command line.

## When disabling is legitimate

- Generated or vendored TypeScript (build output, API clients): exclude the paths via `globalIgnores()` or `TYPESCRIPT_ES_FILTER_REGEX_EXCLUDE` rather than disabling rules.
- Test files often legitimately relax rules like `no-explicit-any` — scope the relaxation with a `files` glob, never globally.
- A rule that conflicts with an adopted project convention: turn it off in `eslint.config.js` with a comment explaining why, so the decision applies uniformly.
- Use `DISABLE_LINTERS` or `TYPESCRIPT_ES_DISABLE_ERRORS` only as a last resort, e.g. while a large legacy codebase is being migrated incrementally.
