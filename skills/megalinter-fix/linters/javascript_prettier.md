# Fix JAVASCRIPT_PRETTIER errors

<!-- generated-descriptor-info-start -->
- Linter: **prettier** (MegaLinter key: `JAVASCRIPT_PRETTIER`)
- Descriptor: **JAVASCRIPT** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/javascript_prettier/>
- Official documentation: <https://prettier.io/>
- Auto-fix support: **yes** — add `JAVASCRIPT_PRETTIER` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter JAVASCRIPT_PRETTIER --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `.prettierrc.json` (custom path can be defined with `JAVASCRIPT_PRETTIER_CONFIG_FILE`)
- Rules index: <https://prettier.io/docs/en/options.html>
- Rules configuration: <https://prettier.io/docs/en/configuration.html>
- How to disable rules inline: <https://prettier.io/docs/en/ignore.html#javascript>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `JAVASCRIPT_PRETTIER` to fully disable this linter
  - `JAVASCRIPT_PRETTIER_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `JAVASCRIPT_PRETTIER_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `JAVASCRIPT_PRETTIER_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `JAVASCRIPT_PRETTIER_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

prettier is an opinionated code formatter: it does not report logic issues, it only flags files whose layout (line width, quotes, semicolons, commas, indentation) differs from its canonical output. Every error is fixable automatically — never reformat by hand.

- Preferred: enable MegaLinter auto-fix (see the generated block above), or run `npx prettier . --write` (shorthand `-w`) to rewrite files in place.
- To only list non-conforming files without changing them, run `npx prettier . --check` (exit code 1 means at least one file needs formatting).
- If a whole class of "errors" reflects a deliberate team style (e.g. tabs, single quotes, 120-char lines), do not touch the code: set the matching option (`printWidth`, `tabWidth`, `useTabs`, `semi`, `singleQuote`, `trailingComma`, `endOfLine`, ...) in the configuration file, then re-run the fix so the codebase converges on that style.
- Cross-platform line-ending failures (CRLF vs LF) are governed by the `endOfLine` option (default `lf`); align it with the repository's git settings rather than editing files.

## Inline disable

Place a `// prettier-ignore` comment on the line just before the statement to keep it exactly as written:

```javascript
// prettier-ignore
matrix(  1, 0, 0,  0, 1, 0,  0, 0, 1,);
```

In JSX use `{/* prettier-ignore */}`; in CSS `/* prettier-ignore */`; in HTML/Markdown `<!-- prettier-ignore -->` (Markdown also supports `<!-- prettier-ignore-start -->` / `<!-- prettier-ignore-end -->` range markers, with blank lines around them); in YAML `# prettier-ignore`.

## Ignore via configuration

prettier has no per-rule disabling — options can only be changed, not switched off. In the configuration file, use the `overrides` section to apply different options (or `excludeFiles`) to specific globs:

```json
{
  "semi": false,
  "overrides": [
    { "files": ["legacy/**/*.js"], "options": { "tabWidth": 4 } }
  ]
}
```

To exclude files entirely, add a `.prettierignore` file at the repository root (gitignore syntax; `node_modules`, version-control directories and `.gitignore` entries are already ignored by default):

```text
dist/
**/*.min.js
```

## When disabling is legitimate

- Hand-aligned data structures (matrices, lookup tables, ASCII art) whose readability depends on manual spacing — use `// prettier-ignore` on that statement only.
- Generated or vendored files (bundles, minified assets, lockfiles, code produced by generators) — list them in `.prettierignore` instead of reformatting output that will be overwritten.
- Fixtures that intentionally contain unformatted code (formatter tests, before/after examples) — exclude the fixture directory.
- Style disagreements are never a reason to disable: change the option in the configuration file instead. Disabling at MegaLinter level (`DISABLE_LINTERS` / `JAVASCRIPT_PRETTIER_DISABLE_ERRORS`) is the last resort.
