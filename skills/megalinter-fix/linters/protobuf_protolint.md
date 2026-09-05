# Fix PROTOBUF_PROTOLINT errors

<!-- generated-descriptor-info-start -->
- Linter: **protolint** (MegaLinter key: `PROTOBUF_PROTOLINT`)
- Descriptor: **PROTOBUF** (format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/protobuf_protolint/>
- Official documentation: <https://github.com/yoheimuta/protolint>
- Auto-fix support: **yes** — add `PROTOBUF_PROTOLINT` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter PROTOBUF_PROTOLINT --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `.protolintrc.yml` (custom path can be defined with `PROTOBUF_PROTOLINT_CONFIG_FILE`)
- Rules index: <https://github.com/yoheimuta/protolint#rules>
- Rules configuration: <https://github.com/yoheimuta/protolint#rules>
- How to disable rules inline: <https://github.com/yoheimuta/protolint#configuring>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `PROTOBUF_PROTOLINT` to fully disable this linter
  - `PROTOBUF_PROTOLINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `PROTOBUF_PROTOLINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `PROTOBUF_PROTOLINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `PROTOBUF_PROTOLINT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

protolint enforces the official Google Protocol Buffer style guide on `.proto` files (proto2 and proto3) without needing the compiler: naming conventions, import ordering, indentation, line length, and proto3-specific constraints.

- Run the linter's own auto-fix first: `protolint lint -fix .` — most default rules are fixable, including `ENUM_FIELD_NAMES_UPPER_SNAKE_CASE`, `FIELD_NAMES_LOWER_SNAKE_CASE`, `MESSAGE_NAMES_UPPER_CAMEL_CASE`, `IMPORTS_SORTED`, `INDENT`, `MAX_LINE_LENGTH`, `PACKAGE_NAME_LOWER_CASE`, `RPC_NAMES_UPPER_CAMEL_CASE`, `SERVICE_NAMES_UPPER_CAMEL_CASE` and `ORDER`. MegaLinter auto-fix (see generated block above) applies the same fixes.
- For naming errors, rename the identifier to the convention named by the rule: fields `lower_snake_case`, messages/services/RPCs `UpperCamelCase`, enum values `UPPER_SNAKE_CASE` prefixed with the enum name, zero value ending with `UNSPECIFIED`.
- For `REPEATED_FIELD_NAMES_PLURALIZED`, pluralize the repeated field name (`repeated string name` -> `repeated string names`).
- For `PROTO3_FIELDS_AVOID_REQUIRED` and `PROTO3_GROUPS_AVOID`, remove the `required` label or replace the `group` with a nested message.
- Use `protolint lint -fix -auto_disable=next .` to fix what is fixable and insert disable comments for the remaining problems (bulk-adoption on legacy files only).

## Inline disable

Use `// protolint:disable` comment directives with one or more rule IDs. Append `:next` to suppress the next line or `:this` for the current line; a bare `disable` ... `enable` pair covers a block.

```proto
enum Foo {
  // protolint:disable:next ENUM_FIELD_NAMES_UPPER_SNAKE_CASE
  firstValue = 0;    // no error
  second_value = 1;  // protolint:disable:this ENUM_FIELD_NAMES_UPPER_SNAKE_CASE
  THIRD_VALUE = 2;   // spits out an error
}
```

## Ignore via configuration

In the configuration file (see generated block above), remove rules or exclude files/directories under the `lint` key. `all_default: true` enables every rule, `no_default: true` starts from an empty set that you extend with `add`:

```yaml
lint:
  rules:
    all_default: true
    remove:
      - MAX_LINE_LENGTH
  files:
    exclude:
      - path/to/legacy.proto
  directories:
    exclude:
      - third_party
```

Tune rules instead of removing them when possible, via `rules_option`:

```yaml
lint:
  rules_option:
    max_line_length:
      max_chars: 120
```

protolint has no separate ignore file: file exclusions live in this same configuration file.

## When disabling is legitimate

- Vendored or third-party `.proto` files (e.g. `third_party/`, `google/`) that must stay byte-identical to upstream — exclude the directory.
- Generated proto files produced by another tool whose output style you do not control.
- Published APIs where renaming a field, enum value or RPC would break wire-compatible clients or generated code consumers — suppress the naming rule inline rather than renaming.
- Deliberate team divergence from the Google style guide (e.g. longer lines, custom enum zero-value suffix) — prefer configuring the rule over removing it.

Disabling the linter at MegaLinter level is the last resort — prefer inline directives or configuration-level exclusions.
