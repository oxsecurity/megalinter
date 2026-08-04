# Fix JSON_PRETTIER errors

<!-- generated-descriptor-info-start -->
- Linter: **prettier** (MegaLinter key: `JSON_PRETTIER`)
- Descriptor: **JSON** (format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/json_prettier/>
- Official documentation: <https://prettier.io/>
- Auto-fix support: **yes** — add `JSON_PRETTIER` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter JSON_PRETTIER --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `.prettierrc.json` (custom path can be defined with `JSON_PRETTIER_CONFIG_FILE`)
- Rules index: <https://prettier.io/docs/en/options.html>
- Rules configuration: <https://prettier.io/docs/en/configuration.html>
- How to disable rules inline: <https://prettier.io/docs/en/ignore.html#javascript>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `JSON_PRETTIER` to fully disable this linter
  - `JSON_PRETTIER_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `JSON_PRETTIER_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `JSON_PRETTIER_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `JSON_PRETTIER_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

Prettier is an opinionated formatter: on JSON files it checks only formatting
(indentation, line width, quoting, spacing), not JSON validity or content.
Any reported error means the file differs from Prettier's canonical output.

- Do not fix formatting by hand: run the MegaLinter auto-fix described above,
  or locally `npx prettier --write "**/*.json"` to rewrite the files.
- Use `npx prettier --check "**/*.json"` to list non-compliant files without
  modifying them.
- If the expected style differs from Prettier defaults (`printWidth: 80`,
  `tabWidth: 2`, `useTabs: false`), change the option in the configuration
  file instead of fighting the formatter, then re-run the fix command.
- If a file fails to parse, it is usually invalid strict JSON (comments,
  trailing commas): fix the syntax, or format it with a laxer parser
  (`json5`, `jsonc`) through a configuration override (see below).

## Inline disable

Plain JSON does not allow comments, so there is no inline suppression for
`.json` files: exclude the file via `.prettierignore` or
`JSON_PRETTIER_FILTER_REGEX_EXCLUDE` instead. In files parsed with the
`jsonc` parser (comments allowed), a `// prettier-ignore` comment keeps the
next node formatted as written:

```jsonc
{
  // prettier-ignore
  "matrix": [1, 0, 0,   0, 1, 0,   0, 0, 1]
}
```

## Ignore via configuration

Set options globally in the configuration file, and use `overrides` to apply
different options (or another parser) to specific JSON files only:

```json
{
  "tabWidth": 2,
  "overrides": [
    {
      "files": ["*.jsonc", ".vscode/*.json"],
      "options": { "parser": "jsonc", "tabWidth": 4 }
    }
  ]
}
```

To exclude files entirely, create a `.prettierignore` file at the repository
root (gitignore syntax):

```text
dist
package-lock.json
**/generated/*.json
```

Prettier already ignores `node_modules` and version-control directories by
default.

## When disabling is legitimate

- Machine-generated or machine-managed JSON (lock files, build output,
  exported schemas) that is rewritten by a tool with its own layout.
- Fixture or golden files whose exact byte layout is part of a test.
- Files with alignment-based layouts (matrices, tables) that Prettier would
  collapse, when readability genuinely suffers.
- JSON-with-comments files owned by another tool with conflicting formatting,
  when a `jsonc` parser override is not enough.

Prefer `.prettierignore` or a configuration override; disabling the linter at
MegaLinter level is the last resort.
