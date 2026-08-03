# Fix PYTHON_BLACK errors

<!-- generated-descriptor-info-start -->
- Linter: **black** (MegaLinter key: `PYTHON_BLACK`)
- Descriptor: **PYTHON** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/python_black/>
- Official documentation: <https://black.readthedocs.io/en/stable/>
- Auto-fix support: **yes** — add `PYTHON_BLACK` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter PYTHON_BLACK --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `pyproject.toml` (custom path can be defined with `PYTHON_BLACK_CONFIG_FILE`)
- Rules configuration: <https://black.readthedocs.io/en/stable/usage_and_configuration/the_basics.html#configuration-format>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `PYTHON_BLACK` to fully disable this linter
  - `PYTHON_BLACK_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `PYTHON_BLACK_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `PYTHON_BLACK_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `PYTHON_BLACK_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

black is an opinionated Python code formatter: it checks nothing but formatting (line length, quotes, spacing, trailing commas...), so every error means "this file is not formatted the way black would write it".

- Do not hand-edit the reported lines: run the formatter and let it rewrite the files. Locally: `black <file_or_directory>` (fix mode is the default). In MegaLinter, use the auto-fix option listed in the block above.
- MegaLinter runs black in check-only mode (`--check` returns exit code 1 when files would be reformatted). To preview the exact changes without applying them, run `black --diff <path>`, optionally combined with `--check`.
- If black's output diverges from the project's expectations, align settings (`line-length`, `target-version`, `skip-string-normalization`...) in the `[tool.black]` section of the configuration file instead of fighting individual lines.

## Inline disable

Use black's format-control comments (there are no per-rule codes since black has a single behavior):

- `# fmt: skip` at the end of a line prevents reformatting of that single line. It can be combined with other pragmas, e.g. `# fmt: skip # noqa`.
- `# fmt: off` / `# fmt: on` around a block prevent reformatting of the whole block. Both comments must be at the same indentation level, in the same block, with no unindent beyond that level between them.

```python
# fmt: off
custom_matrix = [
    1, 0, 0,
    0, 1, 0,
    0, 0, 1,
]
# fmt: on

magic = { "a":1, "b":2 }  # fmt: skip
```

## Ignore via configuration

Configure black in the `[tool.black]` section of its configuration file. Config keys are the CLI option names without the leading `--`:

```toml
[tool.black]
line-length = 88
target-version = ["py311"]
extend-exclude = '''
(
  ^/migrations/
  | .*_pb2\.py
)
'''
```

- `extend-exclude` adds a regex of paths to skip on top of the defaults (recommended).
- `exclude` replaces the default exclusions entirely; `force-exclude` skips files even when they are passed explicitly on the command line.
- black has no dedicated ignore file: by default it automatically skips paths listed in `.gitignore`, unless `exclude` is set (which disables that behavior — prefer `extend-exclude` to keep it).

## When disabling is legitimate

- Hand-aligned data blocks (matrices, tables, lookup dicts) whose visual layout carries meaning: wrap them in `# fmt: off` / `# fmt: on`.
- Generated code (protobuf `*_pb2.py`, migrations, vendored code): exclude the paths via `extend-exclude` rather than reformatting churn.
- Projects that deliberately use another formatter (e.g. an autopep8 or ruff-format style baseline): keep one formatter only and disable the other to avoid ping-pong reformatting.
- Disabling the linter at MegaLinter level is the last resort — prefer inline pragmas or configuration exclusions.
