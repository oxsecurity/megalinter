# Fix PYTHON_RUFF errors

<!-- generated-descriptor-info-start -->
- Linter: **ruff** (MegaLinter key: `PYTHON_RUFF`)
- Descriptor: **PYTHON** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/python_ruff/>
- Official documentation: <https://github.com/astral-sh/ruff>
- Auto-fix support: **yes** — add `PYTHON_RUFF` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter PYTHON_RUFF --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `.ruff.toml` (custom path can be defined with `PYTHON_RUFF_CONFIG_FILE`)
- Rules index: <https://docs.astral.sh/ruff/rules/>
- Rules configuration: <https://docs.astral.sh/ruff/configuration/>
- How to disable rules inline: <https://docs.astral.sh/ruff/linter/#error-suppression>
- Error line format (regex): `Found ([0-9]+) error`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `PYTHON_RUFF` to fully disable this linter
  - `PYTHON_RUFF_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `PYTHON_RUFF_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `PYTHON_RUFF_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `PYTHON_RUFF_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `PYTHON_RUFF_ERROR_CONFIG_PARSE`
  - `PYTHON_RUFF_ERROR_UNKNOWN_RULE`
<!-- generated-descriptor-info-end -->

## Fix instructions

ruff is an extremely fast Python linter implementing 900+ rules from Pyflakes, pycodestyle, isort, pyupgrade, flake8 plugins and more. Many rules have automatic fixes.

- Run `ruff check --fix` first: it applies every available safe fix (safe fixes preserve runtime behavior and comments). Rules marked with the 🛠️ symbol in the rules index are auto-fixable.
- If violations remain that have only unsafe fixes, review them and run `ruff check --fix --unsafe-fixes`; unsafe fixes may alter runtime behavior or remove comments, so re-read the diff and re-run the tests afterwards.
- Fix the remaining rules by family:
  - **F (Pyflakes)** — real logical errors (unused imports/variables, undefined names): delete the dead code or define/import the missing name; never silence F821-style undefined names.
  - **E/W (pycodestyle)** — style errors/warnings such as line length (E501): reflow the code manually or run `ruff format` for formatting-style concerns; ruff intentionally omits stylistic rules that a formatter already handles.
  - **I (isort)** — import ordering: auto-fixed by `ruff check --fix`, or reorder imports into stdlib / third-party / local blocks.
  - **UP (pyupgrade)** — outdated syntax for the target Python version: accept the auto-fix (e.g. modern type annotations, f-strings).
  - **B (flake8-bugbear)** — likely bugs and design problems (e.g. mutable default arguments): fix the underlying logic, not the message.
  - **C4 / SIM** — comprehension and simplification suggestions: mostly auto-fixable rewrites to simpler equivalents.
  - **S (flake8-bandit)** — security findings: replace the dangerous call; only suppress with a justification comment when the usage is provably safe.
  - **N / D** — naming and docstring conventions: rename symbols or adjust docstrings to the convention the project selected.
- Which rules run is driven by `select` / `extend-select` in the configuration; a violation you cannot map to code logic may come from a rule family the project opted into deliberately — read that rule's page in the rules index before changing code.

## Inline disable

- Append `# noqa` to a line to ignore all violations on it, or `# noqa: <RULE>` for specific rules (comma-separated for several).
- Add `# ruff: noqa` (or `# ruff: noqa: <RULE>`) at the top of a file for file-level suppression; ruff also honors `# flake8: noqa`.

```python
import os  # noqa: F401  (re-exported for package API)
l = get_length()  # noqa: E741, F841
```

- For multi-line constructs, place the `noqa` comment at the end of the first line (imports) or after the closing quotes (docstrings).

## Ignore via configuration

- In `.ruff.toml`, use `[lint] ignore` to disable rules globally, `[lint.per-file-ignores]` for path-specific exemptions, and top-level `exclude` / `extend-exclude` to skip files entirely. In `pyproject.toml`, prefix the same sections with `tool.ruff` (e.g. `[tool.ruff.lint]`).

```toml
[lint]
ignore = ["E501"]

[lint.per-file-ignores]
"__init__.py" = ["E402"]
"**/{tests,docs}/*" = ["E402"]
```

- `.ruff.toml` takes precedence over `ruff.toml`, which takes precedence over `pyproject.toml` in the same directory.

## When disabling is legitimate

- False positives, e.g. an import flagged F401 that is intentionally re-exported as public API, or a bandit S rule firing on provably safe usage — suppress inline with the specific rule code and a short justification.
- Deliberate project style divergence (line length, docstring convention, naming scheme): encode it once in `ignore` / `select` in the configuration file rather than sprinkling `# noqa`.
- Generated or vendored code that must not be hand-edited: use `exclude` or `per-file-ignores` instead of modifying the files.
- Prefer fixing, then rule-level configuration; MegaLinter-level disabling (tuning variables in the block above) is the last resort since it hides real errors from the whole repository.
