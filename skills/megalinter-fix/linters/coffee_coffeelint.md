# Fix COFFEE_COFFEELINT errors

<!-- generated-descriptor-info-start -->
- Linter: **coffeelint** (MegaLinter key: `COFFEE_COFFEELINT`)
- Descriptor: **COFFEE** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/coffee_coffeelint/>
- Official documentation: <https://coffeelint.github.io/>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.coffee-lint.json` (custom path can be defined with `COFFEE_COFFEELINT_CONFIG_FILE`)
- Rules index: <https://coffeelint.github.io/#options>
- Rules configuration: <https://coffeelint.github.io/#options>
- How to disable rules inline: <https://coffeelint.github.io/#options>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `COFFEE_COFFEELINT` to fully disable this linter
  - `COFFEE_COFFEELINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `COFFEE_COFFEELINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `COFFEE_COFFEELINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `COFFEE_COFFEELINT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

coffeelint is a style checker that keeps CoffeeScript code clean and consistent. It has no
auto-fix mode, so every reported violation must be corrected manually in the source file.

Fix the most common rule categories as follows:

- `indentation` / `no_tabs`: re-indent the flagged block with 2 spaces per level and replace tab characters with spaces.
- `max_line_length` (default 80 characters): break the line, extract intermediate variables, or shorten string literals.
- `no_trailing_whitespace` / `no_trailing_semicolons`: delete trailing spaces and redundant semicolons at end of lines.
- `camel_case_classes`: rename classes to UpperCamelCase (`class my_widget` -> `class MyWidget`) and update references.
- `duplicate_key`: remove or rename the duplicated key in the object or class.
- `space_operators`: add a single space on each side of the operator (`a+b` -> `a + b`).
- `no_backticks`: replace embedded JavaScript backtick snippets with equivalent CoffeeScript.
- `missing_fat_arrows`: use `=>` instead of `->` when the function body relies on the outer `this`.

To reproduce a finding locally, run `coffeelint path/to/file.coffee` (add `-f <config>` to point
at a specific configuration file). Generate a starter configuration with
`coffeelint --makeconfig > coffeelint.json`.

## Inline disable

Disable a rule for a block with paired comments, and re-enable it right after:

```coffeescript
# coffeelint: disable=max_line_length
foo = "some/huge/line/string/with/embed/#{values}.that/surpasses/the/max/column/width"
# coffeelint: enable=max_line_length
```

Disable all checks for a single line by appending `# noqa` at the end of the line:

```coffeescript
throw "I should be an Error not a string but YOLO" # noqa
```

## Ignore via configuration

In the JSON configuration file named in the block above, set a rule's `level` to `"ignore"` to
disable it, or `"warn"` to keep it reported without failing:

```json
{
  "max_line_length": {
    "value": 100,
    "level": "ignore"
  }
}
```

To exclude files, create a `.coffeelintignore` file at the repository root; it works just like a
`.gitignore` (one glob pattern per line).

## When disabling is legitimate

- Legacy or vendored CoffeeScript that will be migrated to JavaScript/TypeScript rather than restyled.
- Generated `.coffee` files (build output, scaffolding) — exclude them via `.coffeelintignore`.
- A team style that intentionally diverges from a default rule (e.g. longer `max_line_length`): change the rule value in the configuration file instead of sprinkling inline disables.
- `# noqa` on isolated lines where a rule misfires (e.g. an unavoidable long URL in a string).

Disabling the whole linter at MegaLinter level (`DISABLE_LINTERS`) is the last resort — prefer
fixing the code, then rule-level configuration, then file exclusion.
