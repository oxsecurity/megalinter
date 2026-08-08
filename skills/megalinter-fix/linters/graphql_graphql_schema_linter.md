# Fix GRAPHQL_GRAPHQL_SCHEMA_LINTER errors

<!-- generated-descriptor-info-start -->
- Linter: **graphql-schema-linter** (MegaLinter key: `GRAPHQL_GRAPHQL_SCHEMA_LINTER`)
- Descriptor: **GRAPHQL** (format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/graphql_graphql_schema_linter/>
- Official documentation: <https://github.com/cjoudrey/graphql-schema-linter>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.graphql-schema-linterrc` (custom path can be defined with `GRAPHQL_GRAPHQL_SCHEMA_LINTER_CONFIG_FILE`)
- Rules index: <https://github.com/cjoudrey/graphql-schema-linter#built-in-rules>
- Rules configuration: <https://github.com/cjoudrey/graphql-schema-linter#configuration-file>
- How to disable rules inline: <https://github.com/cjoudrey/graphql-schema-linter#inline-rule-overrides>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `GRAPHQL_GRAPHQL_SCHEMA_LINTER` to fully disable this linter
  - `GRAPHQL_GRAPHQL_SCHEMA_LINTER_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `GRAPHQL_GRAPHQL_SCHEMA_LINTER_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `GRAPHQL_GRAPHQL_SCHEMA_LINTER_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `GRAPHQL_GRAPHQL_SCHEMA_LINTER_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `GRAPHQL_GRAPHQL_SCHEMA_LINTER_ERROR_CUSTOM_RULE_NOT_FOUND`
<!-- generated-descriptor-info-end -->

## Fix instructions

graphql-schema-linter validates GraphQL Schema Definition Language (SDL) files against style and
documentation rules. It has no auto-fix: edit the `.graphql` schema files manually.

Fix by error category:

- Missing descriptions (`types-have-descriptions`, `fields-have-descriptions`, `arguments-have-descriptions`, `enum-values-have-descriptions`, `input-object-values-have-descriptions`): add a description string (`"..."` above the type, field, argument or enum value).
- Capitalization (`types-are-capitalized`, `descriptions-are-capitalized`, `enum-values-all-caps`): rename types to start with an uppercase letter, start descriptions with a capital letter, write enum values in ALL_CAPS.
- Naming (`fields-are-camel-cased`, `input-object-values-are-camel-cased`): rename fields and input values to camelCase.
- Ordering (`type-fields-sorted-alphabetically`, `interface-fields-sorted-alphabetically`, `input-object-fields-sorted-alphabetically`, `enum-values-sorted-alphabetically`): reorder members alphabetically.
- `defined-types-are-used`: remove the unused type or reference it from the schema.
- `deprecations-have-a-reason`: add a reason, e.g. `@deprecated(reason: "Use newField instead")`.
- Relay rules (`relay-connection-types-spec`, `relay-connection-arguments-spec`): make `*Connection` types expose `edges` and `pageInfo`, and paginated fields accept `first`/`after` (forward) or `last`/`before` (backward) arguments.

## Inline disable

Four comment directives are supported: `lint-disable`, `lint-enable` (from that line until end of
file or re-enable), `lint-disable-line` and `lint-enable-line` (single line), each followed by a
comma-separated rule list.

```graphql
# lint-disable types-have-descriptions, fields-have-descriptions
type Query {
  field: String
}
# lint-enable types-have-descriptions, fields-have-descriptions

type Mutation {
  doIt: Boolean # lint-disable-line fields-have-descriptions
}
```

## Ignore via configuration

In the configuration file (JSON, also accepted under a `graphql-schema-linter` key in
`package.json`), `rules` restricts linting to only the listed rules, and `rulesOptions` tunes them:

```json
{
  "rules": ["enum-values-sorted-alphabetically", "fields-have-descriptions"],
  "rulesOptions": {
    "enum-values-sorted-alphabetically": { "sortOrder": "lexicographical" }
  }
}
```

There is no ignore file, but errors on specific schema members can be silenced with the `--ignore`
CLI option (pass it through the linter arguments variable):

```bash
--ignore '{"fields-have-descriptions":["Obvious","Query.obvious"]}'
```

## When disabling is legitimate

- Generated SDL (e.g. schemas emitted by code-first frameworks): exclude the files or disable description/ordering rules, since regeneration would erase manual fixes.
- Self-explanatory members flagged by description rules (`Query.id`, trivial enum values): prefer a targeted `lint-disable-line` or the `--ignore` member list over dropping the rule globally.
- Intentional non-Relay pagination design: disable the two `relay-*` rules if the API does not follow the Relay Connections spec.
- Sorting rules conflicting with a deliberate logical grouping of fields: disable the specific `*-sorted-alphabetically` rule.
- Disabling the whole linter at MegaLinter level is the last resort; prefer rule-level or member-level suppression first.
