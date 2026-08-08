# Fix JSON_JSONLINT errors

<!-- generated-descriptor-info-start -->
- Linter: **jsonlint** (MegaLinter key: `JSON_JSONLINT`)
- Descriptor: **JSON** (format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/json_jsonlint/>
- Official documentation: <https://github.com/prantlf/jsonlint>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.jsonlintrc` (custom path can be defined with `JSON_JSONLINT_CONFIG_FILE`)
- Rules index: <https://github.com/prantlf/jsonlint#configuration>
- Rules configuration: <https://github.com/prantlf/jsonlint#configuration>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `JSON_JSONLINT` to fully disable this linter
  - `JSON_JSONLINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `JSON_JSONLINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `JSON_JSONLINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `JSON_JSONLINT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

jsonlint (prantlf fork) is a JSON syntax checker: it reports parse errors with the exact
line and column, and can optionally validate against a JSON Schema and flag duplicate keys.

- Read the error excerpt: output like `Parse error on line 1, column 14: ... Unexpected token "?"`
  points at the offending character. Fix the syntax at that position: add missing commas,
  quotes or braces, remove stray characters, and double-quote all keys and string values.
- Comments (`//`, `/* */`) are invalid in strict JSON: remove them, or if the file is meant
  to be JSON-with-comments, run jsonlint with `--comments` (or `--mode cjson`).
- Single-quoted strings and trailing commas are invalid in strict JSON: replace single
  quotes with double quotes and delete the trailing comma, or enable `--single-quoted-strings`,
  `--trailing-commas` or `--mode json5` when the file is intentionally JSON5.
- Duplicate keys reported with `--no-duplicate-keys`: keep one occurrence of the key and
  merge or delete the redundant ones.
- Schema validation errors (when run with `--validate <schema>`): fix the data so it matches
  the schema (types, required properties), not the schema itself, unless the schema is wrong.
- jsonlint can rewrite files itself: `jsonlint --in-place --pretty-print file.json` reformats,
  and `--prune-comments` / `--trim-trailing-commas` strip constructs that strict JSON forbids.
  MegaLinter does not apply these automatically, so run them manually when useful.

## Inline disable

jsonlint has no inline suppression mechanism: a comment inside a JSON file is itself a syntax
error in strict mode. Relax the parser globally instead (options such as `comments`,
`trailing-commas` in the configuration file) or exclude the file via configuration.

## Ignore via configuration

Put parser options and file patterns in the configuration file (options accept kebab-case or
camelCase; a pattern starting with `!` excludes files):

```json
{
  "comments": true,
  "trailing-commas": true,
  "duplicate-keys": false,
  "patterns": ["**/*.json", "!**/node_modules"]
}
```

There is no dedicated ignore file; exclusion is done with `!` patterns as above, or in
MegaLinter with `JSON_JSONLINT_FILTER_REGEX_EXCLUDE`.

## When disabling is legitimate

- The file is intentionally JSONC/JSON5 (comments, trailing commas, single quotes), e.g.
  `tsconfig.json` or VS Code settings: enable the matching parser options rather than "fixing"
  the file to strict JSON.
- The file is generated or vendored (lock files, exported fixtures) and will be overwritten:
  exclude it with a `!` pattern or `JSON_JSONLINT_FILTER_REGEX_EXCLUDE`.
- Duplicate keys are consumed by a tool that relies on last-key-wins behavior: leave
  `duplicate-keys` at its default instead of failing the build.

Disabling the linter at MegaLinter level (`DISABLE_LINTERS` or
`JSON_JSONLINT_DISABLE_ERRORS`) is the last resort, after fixing or scoped exclusion.
