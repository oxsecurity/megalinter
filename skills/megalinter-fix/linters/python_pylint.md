# Fix PYTHON_PYLINT errors

<!-- generated-descriptor-info-start -->
- Linter: **pylint** (MegaLinter key: `PYTHON_PYLINT`)
- Descriptor: **PYTHON** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/python_pylint/>
- Official documentation: <https://pylint.readthedocs.io>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.pylintrc` (custom path can be defined with `PYTHON_PYLINT_CONFIG_FILE`)
- Rules index: <https://pylint.readthedocs.io/en/stable/user_guide/messages/index.html>
- Rules configuration: <https://pylint.readthedocs.io/en/stable/user_guide/configuration/index.html>
- How to disable rules inline: <https://pylint.readthedocs.io/en/stable/user_guide/messages/message_control.html>
- Error line format (regex): `:([0-9]+):([0-9]+):`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `PYTHON_PYLINT` to fully disable this linter
  - `PYTHON_PYLINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `PYTHON_PYLINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `PYTHON_PYLINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `PYTHON_PYLINT_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `PYTHON_PYLINT_ERROR_CONFIG_PARSE`
  - `PYTHON_PYLINT_ERROR_PLUGIN_LOAD`
  - `PYTHON_PYLINT_ERROR_ASTROID_CRASH`
<!-- generated-descriptor-info-end -->

## Fix instructions

Pylint is a static analyzer that infers types (via astroid) without running the code, reporting errors,
enforced coding standards and code smells. There is no auto-fix: every message must be fixed manually.

Messages are prefixed by a category letter — fix them in this priority order:

- `F` (fatal) and `E` (error): real defects such as `no-member` or `undefined-variable`. Fix the code
  itself (wrong attribute, missing import, bad call signature) — never silence these without proof of a
  false positive.
- `W` (warning): suspicious constructs. Correct the logic (unused variables, dangerous defaults...).
- `C` (convention): naming, layout and documentation standards. Rename or restructure to comply.
- `R` (refactor): code smells like overly complex functions. Split functions/classes or simplify.

Read each message's page in the rules index (it includes problematic/correct code pairs) before editing.
On large legacy codebases, start with `pylint --errors-only`, then progressively re-enable categories
(e.g. drop `--disable=C,R`) as the code is cleaned up.

## Inline disable

Use a pragma comment with the symbolic message name (preferred) or numerical ID:

```python
a, b = ...  # pylint: disable=unbalanced-tuple-unpacking

# pylint: disable-next=no-member
print(self.bla)
```

`# pylint: disable=...` on its own line applies from that point to the end of the current scope (whole
file when placed at module level); restore checking with `# pylint: enable=...`. On a block-opening line
(`if ...:  # pylint: disable=...`) it only covers that line. Accepted identifiers: message names
(`no-member`), IDs (`E1101`), categories (`C`, `R`, `W`, `E`, `F`), checker groups (`pylint --list-groups`)
or `all`.

## Ignore via configuration

Disable messages project-wide in the `[MESSAGES CONTROL]` section, and skip files in `[MAIN]`:

```ini
[MAIN]
ignore=CVS,third_party
ignore-paths=^src/generated/.*$
ignore-patterns=^\.#

[MESSAGES CONTROL]
disable=missing-module-docstring,
        duplicate-code
```

`ignore=` takes base names, `ignore-patterns=` regexes on base names, `ignore-paths=` regexes on full
paths. The same options live under `[tool.pylint.main]` when configuring through `pyproject.toml`.
There is no separate ignore file.

## When disabling is legitimate

- `no-member` / typecheck false positives on dynamically built attributes (C extensions, ORMs) that
  astroid cannot infer — disable inline with a comment explaining why.
- Generated or vendored code (protobuf stubs, migrations): exclude via `ignore-paths` rather than
  littering files with pragmas.
- Convention (`C`) or refactor (`R`) messages that conflict with a deliberate, documented project style —
  disable the specific message in the configuration file, never a whole category inline.
- Test code that intentionally triggers warnings (e.g. accessing protected members) — scope the disable
  to the smallest block possible.

Disabling at MegaLinter level (`DISABLE_LINTERS`, `PYTHON_PYLINT_DISABLE_ERRORS`) is the last resort.
