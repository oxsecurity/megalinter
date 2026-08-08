# Fix TYPESCRIPT_PRETTIER errors

<!-- generated-descriptor-info-start -->
- Linter: **prettier** (MegaLinter key: `TYPESCRIPT_PRETTIER`)
- Descriptor: **TYPESCRIPT** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/typescript_prettier/>
- Official documentation: <https://prettier.io/>
- Auto-fix support: **yes** — add `TYPESCRIPT_PRETTIER` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter TYPESCRIPT_PRETTIER --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `.prettierrc.json` (custom path can be defined with `TYPESCRIPT_PRETTIER_CONFIG_FILE`)
- Rules index: <https://prettier.io/docs/en/options.html>
- Rules configuration: <https://prettier.io/docs/en/configuration.html>
- How to disable rules inline: <https://prettier.io/docs/en/ignore.html#javascript>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `TYPESCRIPT_PRETTIER` to fully disable this linter
  - `TYPESCRIPT_PRETTIER_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `TYPESCRIPT_PRETTIER_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `TYPESCRIPT_PRETTIER_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `TYPESCRIPT_PRETTIER_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

Prettier is an opinionated code formatter: it does not report code-quality rules, only formatting
differences (line width, quotes, semicolons, trailing commas, indentation...). Every reported file
is fully auto-fixable.

- Preferred: let MegaLinter auto-fix (see the `APPLY_FIXES` line above), or run Prettier directly:

```bash
npx prettier . --write          # rewrite all files with proper formatting
npx prettier . --check          # verify only (exit code 1 if files need formatting)
npx prettier . --list-different # print the files that differ, useful in CI
```

- Never hand-edit whitespace to satisfy Prettier: run `--write` and commit the result.
- If the output style is undesirable, change the option in the configuration file (e.g.
  `printWidth`, `singleQuote`, `semi`, `trailingComma`) rather than fighting the formatter.
- Quote glob patterns (`npx prettier "**/*.ts" --write`) so Prettier expands them, not the shell.

## Inline disable

Place a `// prettier-ignore` comment on the line before the statement to keep its manual formatting:

```typescript
// prettier-ignore
const matrix = [
  1, 0, 0,
  0, 1, 0,
  0, 0, 1,
];
```

In JSX/TSX use `{/* prettier-ignore */}` before the element. In Markdown/HTML files, range ignores
are available with `<!-- prettier-ignore-start -->` / `<!-- prettier-ignore-end -->` (each preceded
by a blank line); there is no range-ignore syntax in TypeScript itself.

## Ignore via configuration

Exclude whole files with a `.prettierignore` file at the repository root (gitignore syntax;
`node_modules` and VCS directories are skipped by default, and `.gitignore` is respected):

```text
build
coverage
**/*.generated.ts
```

Adjust or relax formatting per file pattern with `overrides` in the configuration file:

```json
{
  "singleQuote": true,
  "overrides": [
    { "files": "legacy/**/*.ts", "options": { "tabWidth": 4 } }
  ]
}
```

`overrides` entries require `files` and accept `excludeFiles`; never set `parser` at the top level
of the configuration, only inside an override.

## When disabling is legitimate

- Hand-aligned data structures (matrices, lookup tables, ASCII art) where alignment carries meaning
  — use `// prettier-ignore` on that statement only.
- Generated or vendored files (build output, generated clients, minified bundles) — list them in
  `.prettierignore` instead of reformatting them.
- Directories intentionally following a different style (imported legacy code) — use an
  `overrides` block or `.prettierignore` entry scoped to that path.
- Prettier has no false positives in the usual sense: a diff only means the file is not formatted,
  so prefer running the auto-fix; disabling at MegaLinter level is the last resort.
