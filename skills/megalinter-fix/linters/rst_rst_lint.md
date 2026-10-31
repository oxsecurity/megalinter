# Fix RST_RST_LINT errors

<!-- generated-descriptor-info-start -->
- Linter: **rst-lint** (MegaLinter key: `RST_RST_LINT`)
- Descriptor: **RST** (format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/rst_rst_lint/>
- Official documentation: <https://github.com/twolfson/restructuredtext-lint>
- Auto-fix support: no (errors must be fixed manually)
- Rules configuration: <https://github.com/twolfson/restructuredtext-lint#cli-utility>
- How to disable rules inline: <https://docutils.sourceforge.io/docs/ref/rst/directives.html#raw-data-pass-through>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `RST_RST_LINT` to fully disable this linter
  - `RST_RST_LINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `RST_RST_LINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `RST_RST_LINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `RST_RST_LINT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

rst-lint validates the structural correctness of reStructuredText documents (originally to catch
errors that would break rendering, e.g. on PyPI). There is no auto-fix: correct the source manually.

Fix strategy by common error category:

- **Title/section underline problems** (e.g. "Title underline too short"): make the underline (and
  overline) of `=`, `-`, `~`... characters at least as long as the title text, and keep the same
  adornment character for the same section level throughout the file.
- **Unknown directive type / unknown interpreted text role**: rst-lint uses plain docutils, so
  Sphinx-specific directives and roles (`.. toctree::`, `:ref:`, ...) are reported as errors. Either
  rename to a valid docutils directive, or exclude Sphinx-only files from this linter (see below).
- **Malformed hyperlinks**: check target definitions (`.. _name: https://...`) and references
  (`` `name`_ ``); every reference must resolve, and duplicate target names must be removed.
- **Undefined substitutions**: define every `|substitution|` used, or pass shared definitions to all
  files with `--rst-prolog "..."` (add it through the linter arguments variable of the generated
  block above).
- **Unknown lexer in `code` / `code-block`**: use a language name Pygments knows, or drop the
  language argument.
- **Noise from low-severity messages**: reproduce locally with `rst-lint myfile.rst` and raise the
  reported minimum with `--level error` (levels: debug, info, warning, error, severe) to focus on
  blocking issues first.

## Inline disable

rst-lint has no inline suppression comment: docutils reports errors while parsing, before any
comment could be interpreted. The closest workaround for a block that must stay verbatim is the
docutils `raw` pass-through directive, which skips reST parsing of its content:

```rst
.. raw:: html

   <p>Content passed through without reST validation</p>
```

Otherwise, exclude the file via configuration (below) instead of suppressing a single message.

## Ignore via configuration

rst-lint has no configuration file and no ignore file of its own; everything goes through CLI
arguments. In `.mega-linter.yml`, tune it with the variables listed in the generated block:

```yaml
RST_RST_LINT_ARGUMENTS: "--level error"
RST_RST_LINT_FILTER_REGEX_EXCLUDE: "(docs/sphinx/|CHANGELOG\\.rst)"
```

Use the exclude regex for whole files or directories (typical for Sphinx documentation trees), and
`--level` to silence info/warning-severity messages globally.

## When disabling is legitimate

- The file uses Sphinx directives or roles: rst-lint runs plain docutils and cannot know them, so
  these are structural false positives — exclude Sphinx doc trees rather than rewriting valid docs.
- The `.rst` file is generated (API docs, changelogs emitted by tooling): fix the generator or
  exclude the output.
- Info/warning-severity messages that do not break rendering can be filtered with `--level error`
  instead of disabling the linter.
- A custom Pygments lexer or non-builtin substitution is only available in your build environment:
  exclude the affected files.

Disabling the linter entirely at MegaLinter level (`DISABLE_LINTERS`) is the last resort.
