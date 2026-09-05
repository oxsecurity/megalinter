# Fix PYTHON_MYPY errors

<!-- generated-descriptor-info-start -->
- Linter: **mypy** (MegaLinter key: `PYTHON_MYPY`)
- Descriptor: **PYTHON** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/python_mypy/>
- Official documentation: <https://mypy.readthedocs.io/en/stable/>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.mypy.ini` (custom path can be defined with `PYTHON_MYPY_CONFIG_FILE`)
- Rules configuration: <https://mypy.readthedocs.io/en/stable/config_file.html>
- How to disable rules inline: <https://mypy.readthedocs.io/en/stable/inline_config.html#inline-config>
- Error line format (regex): `Found ([0-9]+) error`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `PYTHON_MYPY` to fully disable this linter
  - `PYTHON_MYPY_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `PYTHON_MYPY_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `PYTHON_MYPY_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `PYTHON_MYPY_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `PYTHON_MYPY_ERROR_STUBS_INSTALL_FAILED`
  - `PYTHON_MYPY_ERROR_CONFIG_INVALID`
  - `PYTHON_MYPY_ERROR_DAEMON_CRASH`
<!-- generated-descriptor-info-end -->

## Fix instructions

mypy statically type-checks Python: it validates type annotations, infers types, and reports
incompatibilities between declared and actual types. Fix by error category:

- Missing annotations (`no-untyped-def` family): add parameter and return annotations, e.g.
  `def foo(a: str) -> str:`. Unannotated functions are not type-checked at all, so annotate
  rather than silence — otherwise even blatant type errors pass silently.
- Incompatible types in assignment: a name has a single declared type per scope. Declare the
  common supertype explicitly (`shape: Shape = Circle()` then `shape = Triangle()` is OK) or
  use separate variables for separate types.
- Optional/None errors (`union-attr`, None-related `arg-type`): narrow before use with
  `if x is not None:`, `assert x is not None`, or `assert isinstance(x, str)`. Reach for
  `typing.cast(str, x)` only when narrowing cannot express an invariant you know holds.
- Missing stubs ("Library stubs not installed", `import-untyped`): install the `types-*`
  package mypy suggests (e.g. `python3 -m pip install types-PyYAML`) or run
  `mypy --install-types --non-interactive`. If no stubs exist, set `ignore_missing_imports`
  for that module only (see configuration below) — avoid the global flag.
- `Any` leakage: unannotated parameters become `Any` and disable checking downstream.
  Annotate at the source of the `Any`; use a temporary `reveal_type(expr)` call to inspect
  what mypy infers (remove it before committing).

## Inline disable

Append `# type: ignore[error-code]` to the offending line, using the code mypy prints in
brackets; separate multiple codes with commas. A bare `# type: ignore` silences every error
on the line — prefer the scoped form.

```python
from foolib import foo  # type: ignore[attr-defined]
x = confusing_function()  # type: ignore[assignment, arg-type]
```

To adjust a whole file, add a top-of-file comment such as
`# mypy: disable-error-code="name-defined"` (or `enable-error-code` to re-enable).

## Ignore via configuration

In `.mypy.ini` (or `mypy.ini`/`setup.cfg`), the `[mypy]` section holds global flags;
`[mypy-pattern]` sections override them per module glob:

```ini
[mypy]
disable_error_code = var-annotated, has-type
exclude = (?x)(^tests/.*|^build/.*)

[mypy-somelibrary.*]
ignore_missing_imports = True
```

In `pyproject.toml`, use `[tool.mypy]` and `[[tool.mypy.overrides]]` with a `module` key:

```toml
[tool.mypy]
exclude = ['^tests/.*', '^build/.*']

[[tool.mypy.overrides]]
module = ["somelibrary.*"]
ignore_missing_imports = true
```

## When disabling is legitimate

- Untyped third-party libraries with no stub package: a per-module
  `ignore_missing_imports` override (equivalent to `# type: ignore` on each import of it).
- Gradual typing adoption: relax strictness codes per legacy module via
  `disable_error_code`, while keeping new code fully checked.
- Generated code (protobuf, ORM models, vendored files): list the paths in `exclude`.
- MegaLinter-level disabling (`DISABLE_LINTERS`, `PYTHON_MYPY_DISABLE_ERRORS`) is a last
  resort — prefer scoped inline or per-module configuration so real errors stay visible.
