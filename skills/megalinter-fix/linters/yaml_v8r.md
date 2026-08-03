# Fix YAML_V8R errors

<!-- generated-descriptor-info-start -->
- Linter: **v8r** (MegaLinter key: `YAML_V8R`)
- Descriptor: **YAML** (format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/yaml_v8r/>
- Official documentation: <https://github.com/chris48s/v8r>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.v8rrc.yml` (custom path can be defined with `YAML_V8R_CONFIG_FILE`)
- Rules index: <https://www.schemastore.org/>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `YAML_V8R` to fully disable this linter
  - `YAML_V8R_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `YAML_V8R_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `YAML_V8R_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `YAML_V8R_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

v8r validates YAML (and JSON/TOML) files against JSON Schemas auto-detected from Schema Store based on the filename. There is no auto-fix: edit each file until it conforms to its schema.

- Read each reported error: it names the offending document path and the schema constraint violated (wrong type, missing required property, value not in enum, unknown property). Fix the value or key in the YAML file to match what the schema expects.
- If the wrong schema was auto-detected for a file, pin the correct one explicitly: `v8r my-file.yml --schema https://json.schemastore.org/<schema>.json` (locally) or via `YAML_V8R_ARGUMENTS`.
- If a file has no matching schema in Schema Store ("missing schema" error), either register a schema for it in a custom catalog (see below), or exclude the file from validation.
- For network/HTTP errors fetching schemas (proxy, offline CI), fix connectivity or point `location` in a custom catalog to a local schema file.
- In multi-document YAML files, errors are reported per document as `file.yml[0]`, `file.yml[1]`, etc.; all documents in one file must conform to the same schema.
- Exit code 99 means a file was validated and is invalid (fix the file); exit code 1 means validation could not run (missing schema, HTTP error, malformed file); exit code 98 means the patterns matched no files.

## Inline disable

v8r has no inline suppression syntax: errors come from the JSON Schema, not from named rules, so nothing in a YAML comment can silence them. The closest alternative is excluding the file via the `.v8rignore` file or the configuration file (see below).

## Ignore via configuration

Exclude files with ignore patterns. By default v8r reads gitignore-syntax patterns from a `.v8rignore` file at the project root, and also respects `.gitignore`:

```gitignore
# .v8rignore
generated/**
chart/templates/*.yaml
```

Additional ignore files can be declared with `ignorePatternFiles` in the configuration file, and a custom catalog can map files to the right (or local) schema:

```yaml
# .v8rrc.yml
ignorePatternFiles:
  - .lint-ignore
customCatalog:
  schemas:
    - name: My internal config
      fileMatch: ["*.myapp.yml"]
      location: schemas/myapp-schema.json
```

The `ignoreErrors: true` option (or `--ignore-errors`) makes v8r always exit 0; prefer targeted excludes over this global switch.

## When disabling is legitimate

- The file has no published schema in Schema Store and writing a custom catalog entry is not worth it (one-off internal file).
- The auto-detected schema is wrong or stricter than the tool actually consuming the file (e.g. templated Helm/CI YAML that is not valid before rendering).
- Generated or vendored YAML you do not control diverges from the upstream schema.
- The schema itself lags behind the tool (a newly released key is valid but not yet in the published schema); exclude temporarily and re-enable once the schema is updated.

Disabling the linter at MegaLinter level is the last resort: prefer fixing the file, pinning the right schema, or a targeted ignore pattern.
