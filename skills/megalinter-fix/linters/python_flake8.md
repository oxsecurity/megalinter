# Fix PYTHON_FLAKE8 errors

<!-- generated-descriptor-info-start -->
- Linter: **flake8** (MegaLinter key: `PYTHON_FLAKE8`)
- Descriptor: **PYTHON** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/python_flake8/>
- Official documentation: <https://flake8.pycqa.org>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.flake8` (custom path can be defined with `PYTHON_FLAKE8_CONFIG_FILE`)
- Rules index: <https://flake8.pycqa.org/en/latest/user/error-codes.html>
- Rules configuration: <https://flake8.pycqa.org/en/latest/user/configuration.html#project-configuration>
- How to disable rules inline: <https://flake8.pycqa.org/en/3.1.1/user/ignoring-errors.html#in-line-ignoring-errors>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `PYTHON_FLAKE8` to fully disable this linter
  - `PYTHON_FLAKE8_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `PYTHON_FLAKE8_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `PYTHON_FLAKE8_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `PYTHON_FLAKE8_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `PYTHON_FLAKE8_ERROR_PLUGIN_LOAD`
  - `PYTHON_FLAKE8_ERROR_CONFIG_INVALID`
<!-- generated-descriptor-info-end -->

## Fix instructions

flake8 wraps pycodestyle, pyflakes and mccabe to check Python style, logical
errors and complexity. Every violation code belongs to one of four classes,
and each class calls for a different fix approach:

- `E***` (pycodestyle errors) and `W***` (pycodestyle warnings): style issues
  such as indentation, whitespace and line length. Rewrite the offending lines
  to follow PEP 8; a PEP 8 formatter applied to the file resolves most of them.
- `F***` (pyflakes): logical problems such as unused imports, unused variables
  and undefined names. Delete dead imports/variables, or fix the typo or add
  the missing import for undefined names — do not silence these, they often
  reveal real bugs.
- `C901` (mccabe, reported only when `max-complexity` is set): the function is
  too complex. Extract helper functions or simplify branching to bring the
  complexity under the configured threshold.

Fix the first reported error in a file before chasing later ones: an early
syntax or indentation error can cascade into spurious follow-up violations.

## Inline disable

Append a `# noqa` comment to the offending line. Always list the specific
code(s); a bare `# noqa` silences every violation on the line:

```python
import config_loader  # noqa: F401  (imported for its side effects)
callback = lambda x: x + 1  # noqa: E731,E501
```

The directive is case-insensitive and can be followed by another comment,
e.g. `# noqa: E731  # TODO: refactor to def`.

## Ignore via configuration

In the `[flake8]` section of the configuration file (also read from
`setup.cfg` or `tox.ini`), use `extend-ignore` to add codes to the default
ignore list, `extend-exclude` to skip paths, and `per-file-ignores` to scope
codes to specific files:

```ini
[flake8]
max-line-length = 120
extend-ignore = E203
extend-exclude = build,dist,*_pb2.py
per-file-ignores =
    __init__.py: F401
    tests/*: E501
```

Prefer `extend-ignore`/`extend-exclude` over `ignore`/`exclude`: the plain
options replace flake8's default lists instead of adding to them. Only
whole-line comments are parsed in the config file — inline comments are not.
flake8 has no dedicated ignore file; use `exclude` options instead.

## When disabling is legitimate

- `E203` (whitespace before `:`) conflicts with the output of the Black
  formatter; projects formatted with Black conventionally extend-ignore it
  (flake8's own configuration does).
- `F401` in `__init__.py`: imports re-exported as the package's public API are
  intentionally "unused" — scope the ignore with `per-file-ignores`.
- Generated code (protobuf stubs, migrations) should be excluded via
  `extend-exclude` rather than fixed by hand.
- Disabling at MegaLinter level (`DISABLE_LINTERS`, `PYTHON_FLAKE8_DISABLE_ERRORS`)
  is the last resort — prefer fixing, then inline `# noqa`, then flake8
  configuration.
