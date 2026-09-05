# Fix JSON_V8R errors

<!-- generated-descriptor-info-start -->
- Linter: **v8r** (MegaLinter key: `JSON_V8R`)
- Descriptor: **JSON** (format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/json_v8r/>
- Official documentation: <https://github.com/chris48s/v8r>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.v8rrc.yml` (custom path can be defined with `JSON_V8R_CONFIG_FILE`)
- Rules index: <https://www.schemastore.org/>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `JSON_V8R` to fully disable this linter
  - `JSON_V8R_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `JSON_V8R_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `JSON_V8R_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `JSON_V8R_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `JSON_V8R_ERROR_SCHEMASTORE_UNREACHABLE`
<!-- generated-descriptor-info-end -->

## Fix instructions

v8r validates JSON (and YAML/TOML) files against JSON Schemas, auto-detected from Schema Store based on the filename. Errors are schema violations, not style issues, so fix the file content to match the schema:

- Read the reported schema error (missing required property, wrong type, value not in enum, unknown property) and edit the file so it conforms. Check the schema itself via the Schema Store link for the file type to understand the expected structure.
- `✖ Could not find a schema to validate <file>`: either point v8r to a schema explicitly with `--schema <url-or-path>` (via the linter arguments variable), or declare a `customCatalog` mapping in the configuration file (see below). Files without any matching schema are otherwise skipped.
- Files parsed with multiple YAML documents are reported as `file.yml[0]`, `file.yml[1]`: every document must conform to the same schema; fix each reported index.
- Schema Store unreachable / network failures are environment issues, not code issues: retry, or configure a proxy, or raise `cacheTtl` in the configuration file so cached schemas are reused.

There is no auto-fix: every correction is a manual edit of the invalid file.

## Inline disable

v8r has no inline suppression mechanism: you cannot disable a schema check with a comment inside a JSON file (standard JSON does not support comments anyway). The closest alternatives are excluding the file via an ignore pattern file (see below) or, if only some checks are unwanted, validating against a more permissive schema with `--schema` or a `customCatalog` entry.

## Ignore via configuration

Exclude files with ignore pattern files using gitignore syntax. By default v8r reads `.v8rignore` and `.gitignore` (config option `ignorePatternFiles`, CLI flag `--ignore-pattern-files`; `--no-ignore` disables them all):

```gitignore
# .v8rignore
generated/**
package-lock.json
```

In the configuration file you can also scope validated files, tolerate errors, or map files to a specific schema:

```yaml
patterns: ['*.json']
ignoreErrors: true   # exit 0 even when files are invalid
customCatalog:
  schemas:
    - name: Custom Schema
      fileMatch: ["*.geojson"]
      location: foo/bar/geojson-schema.json
```

Custom catalogs are searched before Schema Store, so a `customCatalog` entry also overrides a wrong auto-detected schema.

## When disabling is legitimate

- The file name matches a Schema Store entry by coincidence and the wrong schema is applied: prefer a `customCatalog` override pointing to the correct (or a permissive) schema over disabling.
- Generated or vendored JSON files (lock files, build artifacts) that you do not control: add them to `.v8rignore`.
- The upstream Schema Store schema is outdated or stricter than the actual tool accepts: pin a corrected schema via `--schema` or `customCatalog`, and report the issue to schemastore.org.
- Intentionally non-conforming fixture/test files: exclude just those paths rather than the whole linter.

Disabling the linter at MegaLinter level (`DISABLE_LINTERS` / `JSON_V8R_DISABLE_ERRORS`) is the last resort.
