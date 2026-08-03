# Fix MARKDOWN_MARKDOWNLINT errors

<!-- generated-descriptor-info-start -->
- Linter: **markdownlint** (MegaLinter key: `MARKDOWN_MARKDOWNLINT`)
- Descriptor: **MARKDOWN** (format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/markdown_markdownlint/>
- Official documentation: <https://github.com/DavidAnson/markdownlint>
- Auto-fix support: **yes** — add `MARKDOWN_MARKDOWNLINT` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter MARKDOWN_MARKDOWNLINT --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `.markdownlint.json` (custom path can be defined with `MARKDOWN_MARKDOWNLINT_CONFIG_FILE`)
- Rules index: <https://github.com/DavidAnson/markdownlint#rules--aliases>
- Rules configuration: <https://github.com/igorshubovych/markdownlint-cli#configuration>
- How to disable rules inline: <https://github.com/DavidAnson/markdownlint#configuration>
- How to ignore files and directories: <https://github.com/igorshubovych/markdownlint-cli#ignoring-files>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `MARKDOWN_MARKDOWNLINT` to fully disable this linter
  - `MARKDOWN_MARKDOWNLINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `MARKDOWN_MARKDOWNLINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `MARKDOWN_MARKDOWNLINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `MARKDOWN_MARKDOWNLINT_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `MARKDOWN_MARKDOWNLINT_ERROR_CONFIG_PARSE`
<!-- generated-descriptor-info-end -->

## Fix instructions

markdownlint statically analyzes Markdown/CommonMark files against a library of rules
enforcing standards and consistency (heading structure, blank lines, line length, HTML usage, etc.).

Fix strategy per common rule:

- **Auto-fixable rules** (e.g. MD012, MD022, MD032 and other rules marked "Fixable"): run `markdownlint --fix <files>` locally — it applies all fixes reported by the active rules and reports remaining issues. Not every rule supports fixing, so review the leftover errors manually.
- **MD013 (line-length)** — not auto-fixable: rewrap prose so each line stays under the configured limit; break long sentences at clause boundaries. For unbreakable content (long URLs, tables), use a reference-style link or raise `line_length` in configuration.
- **MD033 (no-inline-html)** — not auto-fixable: replace inline HTML with Markdown equivalents (`**bold**` instead of `<b>`, Markdown images instead of `<img>`). If a tag is genuinely required (e.g. `<br>` in tables), add it to the rule's `allowed_elements` list.
- **MD041 (first-line-h1)** — not auto-fixable: make the first line of the file a top-level heading (`# Title`), or adjust the `level` parameter if the project starts files at another heading level.
- **MD012 (no-multiple-blanks)** — auto-fixable: collapse consecutive blank lines to a single one (or the configured `maximum`).
- **MD022 (blanks-around-headings)** — auto-fixable: add a blank line above and below every heading.
- **MD032 (blanks-around-lists)** — auto-fixable: add a blank line before the first item and after the last item of every list.

## Inline disable

Disable a rule for a block, then re-enable it:

```markdown
<!-- markdownlint-disable MD013 -->
A very long line that intentionally exceeds the configured line length limit...
<!-- markdownlint-enable MD013 -->
```

Other forms:

- `<!-- markdownlint-disable-next-line MD033 -->` — disable listed rules on the next line only
- `<!-- markdownlint-disable-line MD033 -->` — disable on the current line
- `<!-- markdownlint-disable-file MD041 -->` — disable for the whole file (rule list optional)
- `<!-- markdownlint-capture -->` / `<!-- markdownlint-restore -->` — save and restore the current configuration around a temporary disable
- `<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->` — tune a rule's parameters for the file

Rule aliases work too, e.g. `<!-- markdownlint-disable line-length -->`.

## Ignore via configuration

Tune or disable rules in `.markdownlint.json` (JSONC, YAML, INI and TOML variants are also auto-discovered):

```json
{
  "default": true,
  "MD013": { "line_length": 200 },
  "MD033": { "allowed_elements": ["br"] },
  "MD041": false
}
```

`"default": true` keeps all rules enabled; setting a rule to `false` disables it; an object tunes its parameters.

Exclude files with a `.markdownlintignore` file using gitignore-style patterns:

```text
CHANGELOG.md
docs/generated/**
```

## When disabling is legitimate

- Generated Markdown (changelogs, API docs, tables built by tooling) that cannot follow style rules — ignore the files rather than disabling rules globally.
- MD013 on prose-heavy docs where the team prefers one-sentence-per-line or unwrapped paragraphs — raise `line_length` or disable the rule in configuration.
- MD033 when specific HTML tags are required by the docs renderer — prefer `allowed_elements` over disabling the whole rule.
- MegaLinter-level tuning (`DISABLE_LINTERS`, `MARKDOWN_MARKDOWNLINT_DISABLE_ERRORS`) is a last resort: prefer fixing, then inline disables, then rule configuration.
