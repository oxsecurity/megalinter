# Fix YAML_YAMLLINT errors

<!-- generated-descriptor-info-start -->
- Linter: **yamllint** (MegaLinter key: `YAML_YAMLLINT`)
- Descriptor: **YAML** (format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/yaml_yamllint/>
- Official documentation: <https://yamllint.readthedocs.io/>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.yamllint.yml` (custom path can be defined with `YAML_YAMLLINT_CONFIG_FILE`)
- Rules index: <https://yamllint.readthedocs.io/en/stable/rules.html>
- Rules configuration: <https://yamllint.readthedocs.io/en/stable/configuration.html#configuration>
- How to disable rules inline: <https://yamllint.readthedocs.io/en/stable/disable_with_comments.html>
- Error line format (regex): `[0-9]+:[0-9]+:?\s*(?:\[?warning\]?|\[?error\]?)|(?:::warning file=|::error file=)`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `YAML_YAMLLINT` to fully disable this linter
  - `YAML_YAMLLINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `YAML_YAMLLINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `YAML_YAMLLINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `YAML_YAMLLINT_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `YAML_YAMLLINT_ERROR_CONFIG_INVALID`
<!-- generated-descriptor-info-end -->

## Fix instructions

yamllint checks YAML files for syntax validity and for cosmetic or structural problems
(indentation, line length, trailing spaces, duplicated keys, ambiguous booleans).
yamllint has no auto-fix: fix findings manually, or run a formatter such as prettier on
the files first — it resolves most style findings automatically.

- `line-length`: break the line under the configured maximum (default 80 characters),
  e.g. with a folded (`>-`) or literal (`|-`) block scalar. Long unbreakable words such
  as URLs are tolerated by default (`allow-non-breakable-words: true`); otherwise raise
  `max` in the configuration.
- `indentation`: re-indent with a width that is consistent across the file (default
  `spaces: consistent`) and indent block sequences under their parent mapping key
  (`indent-sequences: true` by default).
- `truthy`: replace boolean-like values (`yes`, `no`, `on`, `off`, `True`, ...) with
  `true` or `false` (the default `allowed-values`), or quote them (`"yes"`) when a
  string is intended. For keys such as `on:` in GitHub Actions workflows, quote the key
  or set `check-keys: false`.
- `document-start`: add `---` as the first line of the document (required by default,
  `present: true`).
- `trailing-spaces`: delete whitespace at the end of lines; configure the editor to trim
  trailing whitespace on save.
- `key-duplicates`: remove or rename duplicated keys in the same mapping and keep only
  the intended entry — parsers silently keep a single value.

## Inline disable

Add a comment on the offending line (or the line above); several rules can be chained,
and omitting `rule:` disables all rules:

```yaml
long_url: https://example.com/very/long/path  # yamllint disable-line rule:line-length
# yamllint disable rule:colons rule:indentation
- Lorem       : ipsum
  dolor       : sit amet
# yamllint enable rule:colons rule:indentation
```

To skip a whole file (e.g. a Jinja template that is not valid YAML), put
`# yamllint disable-file` on its first line.

## Ignore via configuration

Create `.yamllint.yml` at the repository root, extend the built-in `default` (or
`relaxed`) profile, then tune or disable rules and ignore paths with gitignore-style
patterns, globally or per rule:

```yaml
extends: default
rules:
  line-length:
    max: 120
    level: warning
  comments-indentation: disable
  trailing-spaces:
    ignore:
      - /generated/*.yaml
ignore: |
  node_modules/
  *.template.yaml
```

## When disabling is legitimate

- Generated or vendored YAML that will be overwritten: list it under `ignore:` in
  `.yamllint.yml` or in `YAML_YAMLLINT_FILTER_REGEX_EXCLUDE`.
- Templated files (Jinja, Helm, ...) that are not parseable YAML: use
  `# yamllint disable-file`.
- Team-wide style choices (longer lines, no `---` marker): tune the rule in
  `.yamllint.yml` rather than disabling the linter.
- Use `DISABLE_LINTERS` or `YAML_YAMLLINT_DISABLE_ERRORS` only as a last resort when the
  repository cannot realistically converge on the checks.
