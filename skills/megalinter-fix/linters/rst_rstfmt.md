# Fix RST_RSTFMT errors

<!-- generated-descriptor-info-start -->
- Linter: **rstfmt** (MegaLinter key: `RST_RSTFMT`)
- Descriptor: **RST** (format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/rst_rstfmt/>
- Official documentation: <https://github.com/dzhu/rstfmt>
- Auto-fix support: **yes** — add `RST_RSTFMT` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter RST_RSTFMT --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Rules configuration: <https://github.com/dzhu/rstfmt#usage>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `RST_RSTFMT` to fully disable this linter
  - `RST_RSTFMT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `RST_RSTFMT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `RST_RSTFMT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `RST_RSTFMT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

rstfmt is an opinionated formatter (in the spirit of Black or gofmt) for reStructuredText files. It has no individual rules: an error simply means the file is not formatted the way rstfmt would write it (indentation, blank lines, paragraph wrapping at 72 columns by default, directive layout).

The fix is always to reformat, never to tweak style by hand:

- Preferred: let MegaLinter auto-fix by enabling `APPLY_FIXES` as described in the block above.
- Locally, rewrite files in place with the tool itself:

```bash
rstfmt file.rst          # format one file in place
rstfmt docs/             # format all .rst files in a directory
rstfmt -w 100 docs/      # use a 100-column wrap width instead of the default 72
```

`rstfmt --check <file>` (what MegaLinter runs) only reports; `rstfmt --diff <file>` shows the exact changes it wants, which helps understand a failure before applying it.

If a custom wrap width is used locally, pass the same `-w <width>` to MegaLinter through the extra-arguments variable listed above so check and fix agree.

If rstfmt crashes on a file (docutils parse error), fix the invalid reStructuredText syntax first — rstfmt only formats documents it can parse, and its README warns that not all reST constructs are covered.

## Inline disable

rstfmt has no inline suppression mechanism — there is no comment or directive to skip a block or a line. The only alternative is to exclude the whole file from this linter via the exclusion regex variable listed in the block above.

## Ignore via configuration

rstfmt has no configuration file and no ignore file: it is deliberately option-free apart from the CLI flags (`-w`, `--ext`). To skip files, use MegaLinter-level exclusion, for example in `.mega-linter.yml`:

```yaml
RST_RSTFMT_FILTER_REGEX_EXCLUDE: "(docs/generated/|CHANGES\\.rst)"
```

## When disabling is legitimate

- The file uses reST constructs rstfmt does not support and reformatting corrupts or crashes on them (the tool is self-described as early-stage).
- The `.rst` files are generated (e.g. by `sphinx-apidoc`) and will be overwritten at the next generation.
- The project already enforces another reST style (different wrap width or layout mandated by an upstream doc toolchain) that a plain `-w` change cannot reproduce.
- Otherwise, prefer running the formatter: disabling at MegaLinter level is the last resort.
