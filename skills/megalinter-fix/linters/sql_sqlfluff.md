# Fix SQL_SQLFLUFF errors

<!-- generated-descriptor-info-start -->
- Linter: **sqlfluff** (MegaLinter key: `SQL_SQLFLUFF`)
- Descriptor: **SQL** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/sql_sqlfluff/>
- Official documentation: <https://www.sqlfluff.com/>
- Auto-fix support: **yes** — add `SQL_SQLFLUFF` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter SQL_SQLFLUFF --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `.sqlfluff` (custom path can be defined with `SQL_SQLFLUFF_CONFIG_FILE`)
- Rules index: <https://docs.sqlfluff.com/en/stable/rules.html>
- Rules configuration: <https://docs.sqlfluff.com/en/stable/configuration/index.html>
- Error line format (regex): `L:(.*)P:(.*)`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `SQL_SQLFLUFF` to fully disable this linter
  - `SQL_SQLFLUFF_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `SQL_SQLFLUFF_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `SQL_SQLFLUFF_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `SQL_SQLFLUFF_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `SQL_SQLFLUFF_ERROR_DIALECT_NOT_SET`
  - `SQL_SQLFLUFF_ERROR_TEMPLATING_FAILED`
  - `SQL_SQLFLUFF_ERROR_CONFIG_INVALID`
<!-- generated-descriptor-info-end -->

## Fix instructions

sqlfluff is a dialect-flexible SQL linter and auto-formatter (25+ dialects, plus Jinja and dbt
templating). Rules are grouped in coded bundles: aliasing (`AL`), ambiguous (`AM`),
capitalisation (`CP`), convention (`CV`), jinja (`JJ`), layout (`LT`), references (`RF`),
structure (`ST`) and dialect-specific bundles (tsql, postgres, oracle).

- Run the auto-fix first: most violations (layout, capitalisation, aliasing, convention) are
  fixable with `sqlfluff fix <path> --dialect <dialect>` or the MegaLinter auto-fix, then review
  the diff.
- `CP` capitalisation errors: make keywords/identifiers match the configured policy (auto-fixable).
- `LT` layout errors (indentation, spacing, line length): auto-fixable; long lines may need a
  manual split when no safe fix exists.
- `AL` aliasing and `RF` reference errors: add or remove table/column aliases as required and
  qualify column references so they are unambiguous.
- `AM` ambiguous and `ST` structure errors usually need a manual rewrite of the query (explicit
  `JOIN` conditions, distinct handling, subquery simplification) — do not expect auto-fix.
- Parse (`PRS`) or templating errors are not rule violations: fix the SQL syntax, set the correct
  `dialect`, or provide the missing Jinja/dbt template context.

## Inline disable

Append a `-- noqa` comment on the offending line:

```sql
SELECT col_a a FROM foo -- noqa: AL02
SELECT col_a a, col_b b FROM foo -- noqa: CP02,CP03
SELECT broken_syntax FROM foo -- noqa: PRS
```

A bare `-- noqa` ignores every rule on that line. For a range of lines, use
`-- noqa: disable=AL02` (or `disable=all`) and re-enable later with `-- noqa: enable=all`.

## Ignore via configuration

In the configuration file, exclude rules globally and tune individual rules:

```ini
[sqlfluff]
dialect = ansi
exclude_rules = AL02,LT05

[sqlfluff:rules:capitalisation.keywords]
capitalisation_policy = upper
```

Exclude files with a `.sqlfluffignore` file using gitignore-style patterns:

```text
/temp/
generated/*.sql
```

The `ignore_paths` key in the config file accepts the same patterns, and `ignore = templating`
(or `lexing`, `parsing`, `linting`) silences whole error categories.

## When disabling is legitimate

- Generated or vendored SQL (dbt `target/`, migration tools) — exclude the paths via
  `.sqlfluffignore` rather than fixing files that will be regenerated.
- Templated Jinja/dbt sections that sqlfluff cannot fully render — keep
  `ignore_templated_areas = True` or ignore `templating` errors instead of rewriting templates.
- Dialect constructs not yet supported by the parser (`PRS` errors on valid vendor SQL) — suppress
  with `-- noqa: PRS` on the affected statement.
- Intentional style divergence from a rule's policy (e.g. a house aliasing or capitalisation
  convention) — configure or exclude that rule project-wide instead of sprinkling inline noqa.

Disabling the linter at MegaLinter level is the last resort.
