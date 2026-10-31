# Fix MARKDOWN_RUMDL errors

<!-- generated-descriptor-info-start -->
- Linter: **rumdl** (MegaLinter key: `MARKDOWN_RUMDL`)
- Descriptor: **MARKDOWN** (format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/markdown_rumdl/>
- Official documentation: <https://github.com/rvben/rumdl>
- Auto-fix support: **yes** — add `MARKDOWN_RUMDL` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter MARKDOWN_RUMDL --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `.rumdl.toml` (custom path can be defined with `MARKDOWN_RUMDL_CONFIG_FILE`)
- Rules index: <https://github.com/rvben/rumdl/blob/main/docs/RULES.md>
- Rules configuration: <https://github.com/rvben/rumdl/blob/main/docs/global-settings.md>
- How to disable rules inline: <https://github.com/rvben/rumdl/blob/main/docs/inline-configuration.md>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `MARKDOWN_RUMDL` to fully disable this linter
  - `MARKDOWN_RUMDL_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `MARKDOWN_RUMDL_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `MARKDOWN_RUMDL_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `MARKDOWN_RUMDL_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

rumdl is a fast Rust reimplementation of markdownlint: it enforces 81 Markdown style rules
(MD001-MD060+ IDs) covering headings, lists, whitespace, code blocks, links/images, tables and
front matter. Most violations are mechanical formatting issues, so fix them in this order:

- Run the built-in auto-fix first: `rumdl check --fix <paths>` (or MegaLinter auto-fix). Preview
  changes without writing with `rumdl check --diff .`; `rumdl fmt <paths>` formats and always
  exits 0, which is convenient for local cleanup.
- Fix remaining non-fixable findings manually by rule ID: restructure heading levels so they
  increment one at a time (MD001), give the document a single top-level heading (MD041), add a
  language to fenced code blocks (MD040), fill in empty links (MD042), and reflow or shorten
  lines over the limit (MD013).
- Inspect any rule with `rumdl rule MD013` (replace the ID) to see its rationale and options
  before deciding between fixing and configuring.

## Inline disable

Use HTML comments with rule IDs (aliases like `line-length` also work, case-insensitive):

```markdown
<!-- rumdl-disable-next-line MD013 -->
A single very long line that is intentionally kept as-is for this table of raw data.

<!-- rumdl-disable MD033 -->
<div>Raw HTML block allowed in this section only.</div>
<!-- rumdl-enable MD033 -->
```

Other forms: `<!-- rumdl-disable-line MD013 -->` (current line),
`<!-- rumdl-disable-file MD013 MD033 -->` (whole file), and
`<!-- rumdl-configure-file { "MD013": { "line_length": 120 } } -->` (per-file options).
Existing `<!-- markdownlint-disable ... -->` comments are honored for compatibility.

## Ignore via configuration

In the configuration file, disable rules globally, tune them per rule, or exclude paths
(keys are kebab-case; glob patterns supported):

```toml
[global]
disable = ["MD013", "MD033"]
exclude = ["node_modules", "docs/generated/**"]

[MD013]
line-length = 120
code-blocks = false

[per-file-ignores]
"CHANGELOG.md" = ["MD024"]
"docs/api/**/*.md" = ["MD013", "MD041"]
```

There is no dedicated ignore file, but rumdl respects `.gitignore` by default
(`respect-gitignore = true`); `[per-file-ignores]` plus `exclude` cover per-path needs.
Settings can also live in `pyproject.toml` under `[tool.rumdl]`.

## When disabling is legitimate

- Generated Markdown (changelogs, API docs, tables produced by tooling) that will be overwritten
  on the next generation run — use `exclude` or `[per-file-ignores]` instead of editing output.
- Deliberate raw HTML (MD033) or duplicated headings (MD024) required by the target renderer,
  e.g. badges, collapsible `<details>` blocks, or per-version changelog sections.
- Long unbreakable lines (MD013) such as URLs, reference tables or badge definitions — prefer
  raising `line-length` or disabling `code-blocks` checking over blanket disabling.
- Style rules that conflict with another Markdown dialect in use — set the matching `flavor`
  (gfm, mkdocs, mdx, quarto) in `[global]` before disabling individual rules.

Prefer inline comments, then rule/file scoping in the configuration file; disabling the linter
at MegaLinter level is the last resort.
