# Fix PYTHON_PYRIGHT errors

<!-- generated-descriptor-info-start -->
- Linter: **pyright** (MegaLinter key: `PYTHON_PYRIGHT`)
- Descriptor: **PYTHON** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/python_pyright/>
- Official documentation: <https://github.com/Microsoft/pyright>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `pyrightconfig.json` (custom path can be defined with `PYTHON_PYRIGHT_CONFIG_FILE`)
- Rules index: <https://github.com/microsoft/pyright#type-checking-features>
- Rules configuration: <https://github.com/microsoft/pyright/blob/main/docs/configuration.md>
- How to disable rules inline: <https://github.com/microsoft/pyright/blob/main/docs/comments.md#file-level-type-controls>
- Error line format (regex): `([0-9]+) errors,`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `PYTHON_PYRIGHT` to fully disable this linter
  - `PYTHON_PYRIGHT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `PYTHON_PYRIGHT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `PYTHON_PYRIGHT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `PYTHON_PYRIGHT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

pyright is a standards-based static type checker for Python: it verifies type annotations,
inferred types, imports and API usage against typeshed and installed packages. Each diagnostic
carries a rule name such as `reportMissingImports` or `reportGeneralTypeIssues` — fix the code
or the annotations rather than silencing the rule:

- `reportMissingImports` / `reportMissingTypeStubs`: install the missing package (and its
  `types-*` or `-stubs` stub package) in the analysis environment, or fix the import path.
- Incompatible type errors (`reportGeneralTypeIssues`, argument/assignment mismatches): correct
  the annotation, narrow the type with `isinstance()` checks, or fix the value actually passed.
- `Optional` access errors (e.g. `reportOptionalCall`): guard with `if value is not None:`
  before use, or change the annotation so the value can no longer be `None`.
- `reportUnusedVariable`: delete the dead assignment or prefix the name with `_`.
- `reportPrivateUsage`: use the public API instead of an underscore-prefixed member.

pyright has no fix command; all corrections are manual. Reproduce diagnostics locally with
`pyright <path>` and iterate until the error count reaches zero. If strict mode is too noisy,
lower `typeCheckingMode` (`off` < `basic` < `standard` < `strict`) instead of ignoring output.

## Inline disable

Suppress a single line with the PEP 484 comment `# type: ignore`, or preferably with the
pyright-specific form which can target rule names in square brackets:

```python
value = legacy_call()  # pyright: ignore [reportGeneralTypeIssues, reportPrivateUsage]
```

File-level comments at the top of a module set the mode or override rules for the whole file:

```python
# pyright: strict, reportPrivateUsage=false
```

Enable `reportUnnecessaryTypeIgnoreComment` to have pyright flag suppression comments that are
no longer needed.

## Ignore via configuration

In the configuration file (or a `[tool.pyright]` section of `pyproject.toml`, which the JSON
file takes precedence over), tune rule severities with `"none"`, `"warning"`, `"error"` or a
boolean, and control analyzed paths:

```json
{
  "typeCheckingMode": "basic",
  "reportMissingTypeStubs": false,
  "reportUnusedVariable": "warning",
  "exclude": ["**/node_modules", "build"],
  "ignore": ["src/legacy"]
}
```

`exclude` removes paths from analysis entirely, while `ignore` still analyzes them but
suppresses their diagnostics. pyright has no separate ignore file: use these keys.

## When disabling is legitimate

- A third-party dependency ships no type information and no stub package exists: set
  `reportMissingTypeStubs` to `false` rather than annotating around it.
- Generated code (protobuf output, ORM models, vendored files) that will be regenerated:
  list it under `exclude` or `ignore` in the configuration.
- A dynamic pattern (metaclasses, monkey-patching, `__getattr__` magic) that pyright cannot
  model: use a targeted `# pyright: ignore [ruleName]` on the specific line, never a bare
  file-wide suppression.
- A gradual-typing migration where `strict` is the goal but not yet reachable: lower
  `typeCheckingMode` per directory instead of disabling rules globally.

Disabling the linter at MegaLinter level is the last resort, after inline and configuration
options have been ruled out.
