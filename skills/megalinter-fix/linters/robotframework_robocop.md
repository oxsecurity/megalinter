# Fix ROBOTFRAMEWORK_ROBOCOP errors

<!-- generated-descriptor-info-start -->
- Linter: **robocop** (MegaLinter key: `ROBOTFRAMEWORK_ROBOCOP`)
- Descriptor: **ROBOTFRAMEWORK** (tooling_format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/robotframework_robocop/>
- Official documentation: <https://github.com/MarketSquare/robotframework-robocop>
- Auto-fix support: **yes** — add `ROBOTFRAMEWORK_ROBOCOP` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter ROBOTFRAMEWORK_ROBOCOP --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `robocop.toml` (custom path can be defined with `ROBOTFRAMEWORK_ROBOCOP_CONFIG_FILE`)
- Rules index: <https://robocop.dev/stable/rules_list/>
- Rules configuration: <https://robocop.dev/stable/configuration/>
- How to disable rules inline: <https://robocop.dev/stable/configuration/disablers/>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `ROBOTFRAMEWORK_ROBOCOP` to fully disable this linter
  - `ROBOTFRAMEWORK_ROBOCOP_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `ROBOTFRAMEWORK_ROBOCOP_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `ROBOTFRAMEWORK_ROBOCOP_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `ROBOTFRAMEWORK_ROBOCOP_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `ROBOTFRAMEWORK_ROBOCOP_ERROR_CONFIG_INVALID`
<!-- generated-descriptor-info-end -->

## Fix instructions

Robocop performs static analysis of Robot Framework code (`.robot` / `.resource`) using the official Robot Framework parsing API. Rules are grouped by category, reflected in the rule id prefix (e.g. `DOC01` = documentation group): documentation, naming, lengths, spacing, duplications, tags, arguments, imports, errors, comments, misc.

- Run `robocop check --fix` to apply safe auto-fixes (spacing, indentation, deprecated syntax with direct replacements, formatting normalization); MegaLinter auto-fix does the equivalent. Review before adding `--unsafe-fixes`. List fixable rules with `robocop check list rules --with-fix`.
- Complement with `robocop format` for formatting concerns not covered by `--fix`.
- Documentation rules (`missing-doc-*`): add a `[Documentation]` setting to the flagged keyword, test case or suite.
- Naming rules: rename keywords, tests and variables to match the expected casing/pattern reported by the rule.
- Length rules (e.g. `line-too-long`): split long lines and keywords, or tune the limit via `--configure line-too-long.line_length=140` (or `configure` in the config file).
- Duplication rules: remove or merge duplicated test cases, keywords and variables.
- Understand any rule by its id or name in the rules index before changing code.

## Inline disable

Use `# robocop: off` comment disablers (rule name and rule id are interchangeable):

```robotframework
Some Keyword  # robocop: off              # disable all rules for this line
Some Keyword  # robocop: off=rule1, rule2 # disable specific rules
```

Placed on its own line, a disabler applies to the rest of the current block (keyword, test case, loop, `IF`) or until `# robocop: on=rule1`. Placed in the first comment section of the file, it disables the rule(s) for the whole file:

```robotframework
# robocop: off=missing-doc-test-case

*** Test Cases ***
Some Test
    Keyword 1
```

Formatters have their own disablers: `# robocop: fmt: off=FormatterName`.

## Ignore via configuration

In the configuration file (also supported in `pyproject.toml` under the same `[tool.robocop]` tables):

```toml
[tool.robocop]
exclude = ["deprecated.robot", "tmp_dir"]

[tool.robocop.lint]
ignore = ["missing-doc-keyword", "duplicated-test-case"]
select = ["missing-doc-keyword"]  # alternative: allowlist only these rules
configure = ["line-too-long.line_length=110"]
threshold = "W"  # report only warnings and errors
```

Robocop has no dedicated ignore file, but it automatically honors `.gitignore` patterns (opt out with `skip-gitignore = true`).

## When disabling is legitimate

- Generated or vendored Robot Framework files (e.g. exported from test recorders): exclude the paths rather than fixing churned code.
- Project conventions that intentionally diverge, such as a longer line length or different naming scheme: prefer `configure` to tune the rule over ignoring it entirely.
- Documentation rules on trivial private keywords where docs add no value: disable per block or per file with an inline disabler, keeping the rule active elsewhere.
- Rules conflicting with a required Robot Framework version's syntax in your suites.

Disabling the linter at MegaLinter level is the last resort — prefer fixing, then rule-level or file-level exclusions in Robocop's own configuration.
