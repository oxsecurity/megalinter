# Fix PYTHON_RUFF_FORMAT errors

<!-- generated-descriptor-info-start -->
- Linter: **ruff-format** (MegaLinter key: `PYTHON_RUFF_FORMAT`)
- Descriptor: **PYTHON** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/python_ruff_format/>
- Official documentation: <https://github.com/astral-sh/ruff>
- Auto-fix support: **yes** — add `PYTHON_RUFF_FORMAT` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter PYTHON_RUFF_FORMAT --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `.ruff.toml` (custom path can be defined with `PYTHON_RUFF_FORMAT_CONFIG_FILE`)
- Rules index: <https://docs.astral.sh/ruff/rules/>
- Rules configuration: <https://docs.astral.sh/ruff/configuration/>
- How to disable rules inline: <https://docs.astral.sh/ruff/linter/#error-suppression>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `PYTHON_RUFF_FORMAT` to fully disable this linter
  - `PYTHON_RUFF_FORMAT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `PYTHON_RUFF_FORMAT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `PYTHON_RUFF_FORMAT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `PYTHON_RUFF_FORMAT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

ruff-format is a formatter (a drop-in replacement for Black), not a rule-based linter: it only checks that Python files match its canonical formatting (indentation, quotes, line wrapping). There are no individual rules to fix.

- Enable the MegaLinter auto-fix (see the auto-fix line in the block above) so files are rewritten in place, or run the formatter locally: `ruff format` (a path or single file can be passed as argument).
- `ruff format --check` reproduces the MegaLinter behavior: it reports files that would be reformatted without modifying them.
- Never hand-edit code to satisfy the formatter — always let the tool rewrite the files, then review and commit the diff.
- If the formatter reports a file it cannot process, ensure the file parses as valid Python first: invalid syntax is skipped, not formatted.

## Inline disable

Use the formatter pragma comments to protect a region or statement from reformatting:

```python
# fmt: off
matrix = [
    1, 0,
    0, 1,
]
# fmt: on

result = call(arg1 , arg2)  # fmt: skip
```

- `# fmt: off` / `# fmt: on` disable formatting for the statements between them (they have no effect inside an expression).
- `# fmt: skip` at the end of a line preserves a specific statement, decorator, class or function header.
- `# yapf: disable` / `# yapf: enable` are also honored as YAPF-compatible equivalents.

## Ignore via configuration

In the configuration file named in the block above (same syntax under `[tool.ruff]` in `pyproject.toml`), exclude files globally or for the formatter only:

```toml
extend-exclude = ["generated/*.py"]

[format]
exclude = ["*.pyi"]
quote-style = "double"
```

- `exclude` replaces Ruff's default exclusion list (`.git`, `.venv`, `build`, `dist`, ...); prefer `extend-exclude` to add patterns to it.
- Files ignored by `.gitignore` are skipped by default (`respect-gitignore = false` disables this).
- Style disagreements should be settled with `[format]` options (`quote-style`, `indent-style`, `line-length`, `docstring-code-format`) rather than exclusions.

## When disabling is legitimate

- Generated or vendored Python files (protobuf stubs, auto-generated clients) that will be regenerated: exclude them via `extend-exclude`.
- Hand-aligned data literals (matrices, tables, ASCII layouts) where formatting destroys readability: keep them under `# fmt: off` / `# fmt: on`.
- Repositories already standardized on another formatter (e.g. Black with diverging options): configure `[format]` to match, or keep only one formatter active.
- Disabling the linter at MegaLinter level is the last resort — prefer inline pragmas or configuration exclusions.
