# Fix TYPESCRIPT_STANDARD errors

<!-- generated-descriptor-info-start -->
- Linter: **ts-standard** (MegaLinter key: `TYPESCRIPT_STANDARD`)
- Descriptor: **TYPESCRIPT** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/typescript_ts_standard/>
- Official documentation: <https://standardjs.com/>
- Auto-fix support: **yes** — add `TYPESCRIPT_STANDARD` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter TYPESCRIPT_STANDARD --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Rules index: <https://standardjs.com/rules.html>
- Rules configuration: <https://github.com/standard/ts-standard#readme>
- How to disable rules inline: <https://standardjs.com/#how-do-i-disable-a-rule>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `TYPESCRIPT_STANDARD` to fully disable this linter
  - `TYPESCRIPT_STANDARD_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `TYPESCRIPT_STANDARD_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `TYPESCRIPT_STANDARD_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `TYPESCRIPT_STANDARD_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

ts-standard applies the JavaScript Standard Style guide to TypeScript (`*.ts`, `*.tsx`) via ESLint and `@typescript-eslint/parser`. It is opinionated and non-configurable: there is no rule tuning, only fixing, ignoring or disabling.

- Run the auto-fixer first: `ts-standard --fix` (or MegaLinter auto-fix as described above). Most findings are mechanical style issues it corrects automatically: 2-space indentation, single quotes for strings, no semicolons, spacing after keywords/commas and around operators, space after `//` in comments.
- Fix the remaining non-fixable errors by hand, most commonly:
  - `no-unused-vars`: delete the unused variable, import or parameter (or use it).
  - `eqeqeq`: replace `==` / `!=` with `===` / `!==`.
  - camelCase naming: rename identifiers that use snake_case or PascalCase for variables/functions.
- ts-standard needs a TypeScript project file: it looks for `tsconfig.eslint.json` then `tsconfig.json` in the working directory. If files are reported as not covered by the project, point to the right config with the `--project path/to/tsconfig.json` flag (pass it through the arguments tuning variable) or a `"ts-standard": { "project": "..." }` entry in `package.json`.

## Inline disable

ts-standard uses ESLint disable comments (Standard Style documents this mechanism):

```ts
const file = 'I know what I am doing' // eslint-disable-line no-unused-vars

/* eslint-disable no-use-before-define */
console.log(offendingCode)
/* eslint-enable no-use-before-define */
```

Prefer the single-line form with an explicit rule name over blanket `// eslint-disable-line`.

## Ignore via configuration

There is no dedicated rc file: configuration lives in the `ts-standard` section of `package.json`. Use its `ignore` property to exclude files or folders:

```json
{
  "ts-standard": {
    "project": "tsconfig.eslint.json",
    "ignore": ["dist", "src/**/*.js"]
  }
}
```

`node_modules/`, `coverage/`, `vendor/`, `*.min.js`, dot-folders and paths listed in the project root `.gitignore` are ignored automatically. Rules themselves cannot be turned off in configuration — that is by design of Standard Style.

## When disabling is legitimate

- Generated or vendored TypeScript (build output, API clients, protobuf stubs) that will be regenerated: add it to the `ignore` list rather than fixing it.
- The project deliberately follows another style (semicolons, Prettier, a custom ESLint config): running ts-standard alongside it produces pure noise; disable one of the two at MegaLinter level.
- Intentional non-camelCase identifiers required by an external API contract: suppress with a targeted `// eslint-disable-line` and the exact rule name.
- Variables that must stay declared for typing or documentation purposes despite `no-unused-vars`: prefix-rename or suppress inline instead of disabling the rule globally.

Disabling the linter at MegaLinter level (`DISABLE_LINTERS` / `..._DISABLE_ERRORS`) is the last resort — fix, auto-fix or scope an ignore first.
