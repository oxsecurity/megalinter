# Fix SNAKEMAKE_SNAKEFMT errors

<!-- generated-descriptor-info-start -->
- Linter: **snakefmt** (MegaLinter key: `SNAKEMAKE_SNAKEFMT`)
- Descriptor: **SNAKEMAKE** (tooling_format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/snakemake_snakefmt/>
- Official documentation: <https://github.com/snakemake/snakefmt>
- Auto-fix support: **yes** — add `SNAKEMAKE_SNAKEFMT` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter SNAKEMAKE_SNAKEFMT --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `.snakefmt.toml` (custom path can be defined with `SNAKEMAKE_SNAKEFMT_CONFIG_FILE`)
- Rules configuration: <https://github.com/snakemake/snakefmt#configuration>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `SNAKEMAKE_SNAKEFMT` to fully disable this linter
  - `SNAKEMAKE_SNAKEFMT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `SNAKEMAKE_SNAKEFMT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `SNAKEMAKE_SNAKEFMT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `SNAKEMAKE_SNAKEFMT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

snakefmt is the "uncompromising" Black-style formatter for `Snakefile` and `.smk` files: it wraps lines longer than `line_length` (default 88), normalizes strings, enforces newlines after keywords, adds trailing commas, sorts rule directives (default since v1.x, opt out with `--no-sort`), and formats `shell:` blocks with shfmt (disable with `-F`). Errors are never rule violations to fix by hand — they mean the file differs from the canonical format.

- Fix everything at once: run `snakefmt <path>` (in-place) on the reported files or directory, or use the MegaLinter auto-fix described above.
- Preview before applying: `snakefmt --diff <path>` (or `--compact-diff`) prints the changes without writing; `snakefmt --check <path>` only returns a status (0 clean, 1 would reformat, 123 internal error — a 123 usually means the file has a syntax error snakefmt cannot parse: fix the Snakemake/Python syntax first).
- Do not hand-edit code to satisfy the formatter; if the output is undesirable for a region, use an inline directive instead.

## Inline disable

Directives must be standalone comment lines (an inline `input: # fmt: off` is treated as a plain comment and has no effect), and `# fmt: off` / `# fmt: on` must sit at the same indentation level.

```python
# fmt: off
rule aligned_table:
    input:
        "a.txt",   "b.txt",   "c.txt"
# fmt: on
```

- `# fmt: off` / `# fmt: on` — disables all formatting for the enclosed region (passed through to Black inside `run:` blocks).
- `# fmt: off[sort]` / `# fmt: on[sort]` — keeps directives in their original order while still applying all other formatting.
- `# fmt: off[next]` — leaves only the next Snakemake keyword block (`rule`, `checkpoint`, `use rule`...) unformatted.
- `# fmt: skip` — preserves a single line as written, but only works on plain Python lines outside rule/checkpoint blocks.

## Ignore via configuration

The configuration file uses the same TOML layout as a `pyproject.toml`: put options under `[tool.snakefmt]` (Black passthrough options go under `[tool.black]`). There is no dedicated ignore file; exclude files with the `exclude` regex (or `--exclude` on the CLI via the extra-arguments variable).

```toml
[tool.snakefmt]
line_length = 100
exclude = 'legacy/.*\.smk$'
sort_directives = false
format_shell = false

[tool.black]
skip_string_normalization = true
```

Without an explicit config, snakefmt searches parent directories of the formatted files for a `pyproject.toml`.

## When disabling is legitimate

- Hand-aligned inputs, matrices, or wildcard tables whose vertical alignment aids readability — wrap them in a `# fmt: off` region rather than fighting the formatter.
- Rules where directive order is intentionally meaningful for readers — use `# fmt: off[sort]` or set `sort_directives = false` instead of disabling formatting entirely.
- Generated or vendored Snakemake workflows that will be regenerated — exclude their paths via the `exclude` regex (or the MegaLinter filter variable) instead of formatting them.
- A project-wide line-length or string-quote convention that differs from the defaults — encode it in `line_length` / `[tool.black]` options rather than turning the linter off.

Disabling the linter at MegaLinter level is the last resort — prefer inline directives or configuration scoped to the offending files.
