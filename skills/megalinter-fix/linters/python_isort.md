# Fix PYTHON_ISORT errors

<!-- generated-descriptor-info-start -->
- Linter: **isort** (MegaLinter key: `PYTHON_ISORT`)
- Descriptor: **PYTHON** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/python_isort/>
- Official documentation: <https://pycqa.github.io/isort/>
- Auto-fix support: **yes** — add `PYTHON_ISORT` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter PYTHON_ISORT --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `.isort.cfg` (custom path can be defined with `PYTHON_ISORT_CONFIG_FILE`)
- Rules configuration: <https://pycqa.github.io/isort/docs/configuration/config_files.html>
- How to disable rules inline: <https://pycqa.github.io/isort/docs/configuration/action_comments.html>
- Error line format (regex): `\@\@ (.*) \@\@`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `PYTHON_ISORT` to fully disable this linter
  - `PYTHON_ISORT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `PYTHON_ISORT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `PYTHON_ISORT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `PYTHON_ISORT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

isort is a formatter: it sorts Python imports alphabetically and separates them into sections by type (future, standard library, third-party, local). Errors are reported as diffs (`@@ ... @@` hunks) showing the expected import order.

- Prefer the auto-fix: enable MegaLinter auto-fix (see generated block above) or run `isort .` locally (a specific file: `isort myfile.py`) to rewrite imports in place.
- To preview changes without modifying files, run `isort --check-only --diff .`.
- If the project also uses Black and the two tools fight over import formatting, set `profile = black` in the isort configuration so isort matches Black's style.
- Manual fixes are rarely worth it; if needed, reorder imports to match the reported diff (grouped by section, alphabetical within each group).

## Inline disable

Use isort action comments:

- `# isort: skip` — leave a single import line untouched.
- `# isort: skip_file` — skip the whole file (place near the top).
- `# isort: off` / `# isort: on` — leave a block of lines unchanged.
- `# isort: split` — end the current sort section and start a new grouping.

```python
import sys  # isort: skip

# isort: off
import z_must_come_first
import a_after_it
# isort: on
```

## Ignore via configuration

In the configuration file (section `[settings]`), exclude files or directories with `skip`, `skip_glob`, or `extend_skip`:

```ini
[settings]
profile = black
skip = build,.tox,venv
skip_glob = */generated/*
```

The same options work in `pyproject.toml` under `[tool.isort]`, or in `setup.cfg` / `tox.ini` under `[isort]`. isort uses the first configuration file it finds and never merges several files. There is no separate ignore file; use these skip options instead.

## When disabling is legitimate

- Import order is load-bearing: side-effect imports, monkey-patching, or `sys.path` manipulation that must run before other imports (use `# isort: skip` or `off`/`on`).
- Generated code (protobuf stubs, auto-generated clients) that will be overwritten anyway (use `skip_glob` or `# isort: skip_file`).
- Intentional style divergence from another formatter: prefer configuring `profile = black` (or another profile) over disabling.
- Disabling the linter at MegaLinter level (`DISABLE_LINTERS` or `PYTHON_ISORT_DISABLE_ERRORS`) is the last resort — prefer inline action comments or skip configuration.
