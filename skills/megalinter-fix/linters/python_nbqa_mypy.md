# Fix PYTHON_NBQA_MYPY errors

<!-- generated-descriptor-info-start -->
- Linter: **nbqa** (MegaLinter key: `PYTHON_NBQA_MYPY`)
- Descriptor: **PYTHON** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/python_nbqa/>
- Official documentation: <https://github.com/nbQA-dev/nbQA>
- Auto-fix support: no (errors must be fixed manually)
- Rules index: <https://github.com/nbQA-dev/nbQA>
- Error line format (regex): `Found ([0-9]+) error`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `PYTHON_NBQA_MYPY` to fully disable this linter
  - `PYTHON_NBQA_MYPY_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `PYTHON_NBQA_MYPY_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `PYTHON_NBQA_MYPY_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `PYTHON_NBQA_MYPY_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `PYTHON_NBQA_MYPY_ERROR_NOTEBOOK_INVALID`
  - `PYTHON_NBQA_MYPY_ERROR_TOOL_CRASH`
<!-- generated-descriptor-info-end -->

## Fix instructions

This linter runs `nbqa mypy notebook.ipynb`: nbqa extracts the code cells of Jupyter
notebooks (handling IPython magics robustly) and type-checks them with mypy. Errors
reference notebook cells and must be fixed in the notebook source; there is no auto-fix.

- `name-defined` / `attr-defined`: fix typos, add the missing import or attribute, or
  restructure cells so a symbol is defined before the cell that uses it.
- Missing annotations: unannotated functions are not type-checked; add parameter and
  return type annotations (e.g. `def foo(a: str) -> str:`).
- Untyped third-party imports: install the stub package (`pip install types-<package>`),
  or set `ignore_missing_imports = True` for that module in the mypy configuration.
- Optional/`None` errors: declare `str | None` style unions and narrow with `if x is not None:`
  before use.
- `arg-type` / `assignment` invariance errors: annotate with the broader type explicitly, or
  accept immutable types such as `Sequence[A]` instead of `list[A]`.
- Redefinition with an incompatible type: annotate the first assignment with the broader
  type (`shape: Shape = Circle()`), a frequent pattern when notebook cells reuse names.

Reproduce locally with `nbqa mypy my_notebook.ipynb` before pushing.

## Inline disable

Use mypy's standard suppression comment inside the notebook cell, with the error code
in brackets so only that error is silenced on that line:

```python
from foolib import foo  # type: ignore[attr-defined]
x = compute()  # type: ignore[arg-type, assignment]
```

A file-level comment in the first cell can tune codes for the whole notebook, e.g.
`# mypy: enable-error-code="truthy-bool, ignore-without-code"`. To skip entire cells,
tag them in the cell metadata and declare the tag under `[tool.nbqa.skip_celltags]`.

## Ignore via configuration

nbqa reads mypy settings from `setup.cfg`, `tox.ini` or `pyproject.toml`; disable codes
per module in the mypy section:

```ini
[mypy-tests.*]
disable_error_code = var-annotated, has-type
ignore_missing_imports = True
```

nbqa-specific behavior lives in `pyproject.toml`:

```toml
[tool.nbqa.addopts]
mypy = ["--disable-error-code=name-defined"]

[tool.nbqa.exclude]
mypy = "^notebooks/poc_"

[tool.nbqa.config]
mypy = ".mypy.ini"
```

`[tool.nbqa.files]` restricts checking to matching notebooks, and the same patterns can
be passed on the CLI with `--nbqa-files` / `--nbqa-exclude`.

## When disabling is legitimate

- Notebook cells legitimately redefine names with new types during exploration; prefer a
  broader annotation or a targeted `# type: ignore[assignment]` over disabling the linter.
- Third-party libraries without stubs: `ignore_missing_imports` per module is the accepted
  remediation, not a code change.
- Cells relying on symbols injected by IPython magics or notebook execution context may
  raise `name-defined` false positives; skip those cells via `skip_celltags`.
- Scratch or demo notebooks not meant to be typed can be excluded with `[tool.nbqa.exclude]`.

Disabling at MegaLinter level (`DISABLE_LINTERS`, `PYTHON_NBQA_MYPY_DISABLE_ERRORS`) is
the last resort, only after inline and configuration options have been ruled out.
