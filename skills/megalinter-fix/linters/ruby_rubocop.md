# Fix RUBY_RUBOCOP errors

<!-- generated-descriptor-info-start -->
- Linter: **rubocop** (MegaLinter key: `RUBY_RUBOCOP`)
- Descriptor: **RUBY** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/ruby_rubocop/>
- Official documentation: <https://rubocop.org/>
- Auto-fix support: **yes** — add `RUBY_RUBOCOP` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter RUBY_RUBOCOP --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `.ruby-lint.yml` (custom path can be defined with `RUBY_RUBOCOP_CONFIG_FILE`)
- Rules index: <https://docs.rubocop.org/rubocop/cops.html>
- Rules configuration: <https://docs.rubocop.org/rubocop/configuration.html>
- How to disable rules inline: <https://docs.rubocop.org/rubocop/configuration.html#disabling-cops-within-source-code>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `RUBY_RUBOCOP` to fully disable this linter
  - `RUBY_RUBOCOP_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `RUBY_RUBOCOP_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `RUBY_RUBOCOP_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `RUBY_RUBOCOP_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `RUBY_RUBOCOP_ERROR_UNABLE_TO_LOAD_PLUGIN`
  - `RUBY_RUBOCOP_ERROR_INVALID_CONFIG`
  - `RUBY_RUBOCOP_ERROR_OBSOLETE_CONFIG`
<!-- generated-descriptor-info-end -->

## Fix instructions

RuboCop checks Ruby code against the community Ruby Style Guide through "cops" grouped in departments:
`Layout` (formatting), `Style` (idioms), `Lint` (likely bugs), `Metrics` (complexity), `Naming`, `Security`.

- Prefer auto-fix first: run `rubocop -a` (safe corrections only, won't change code semantics), or use the MegaLinter auto-fix described in the block above. `rubocop -x` applies layout-only fixes.
- `rubocop -A` also applies unsafe corrections that may change semantics: review the diff and run the test suite afterwards.
- `Layout` and most `Style` offenses are auto-correctable; apply the fix rather than editing by hand.
- `Metrics` offenses (`MethodLength`, `AbcSize`, `CyclomaticComplexity`...) have no autocorrect: refactor by extracting smaller methods/classes, or raise the cop's `Max` in configuration when the team agrees.
- `Lint` offenses usually flag real bugs (useless assignment, duplicated condition, shadowed variable): fix the underlying logic instead of suppressing.
- For offenses that cannot be auto-corrected, `rubocop -a --disable-uncorrectable` inserts `# rubocop:todo` comments to suppress them for later cleanup.
- To adopt RuboCop on a legacy codebase, run `rubocop --auto-gen-config`: it generates a `.rubocop_todo.yml` baseline of current offenses to burn down over time.

## Inline disable

Use `# rubocop:disable <Department/CopName>` comments, and re-enable with `# rubocop:enable` in block form:

```ruby
for x in (0..19) # rubocop:disable Style/For

# rubocop:disable Layout/LineLength, Style/StringLiterals
long_line_or_legacy_code
# rubocop:enable Layout/LineLength, Style/StringLiterals
```

Details:

- Accepts one or several cop names, a whole department (`Metrics`), or `all`.
- `# rubocop:todo` is an alias of `disable` for offenses to fix later.
- Append a justification after `--`: `# rubocop:disable Layout/LineLength -- URL cannot be split`.

## Ignore via configuration

In the RuboCop configuration file, disable a cop or exclude files per cop or globally:

```yaml
Style/Encoding:
  Enabled: false

Metrics/MethodLength:
  Exclude:
    - "app/models/problematic.rb"

AllCops:
  Exclude:
    - "db/**/*"
    - "vendor/**/*"
```

RuboCop has no separate ignore file; instead, inherit a generated baseline from the config file:

```yaml
inherit_from: .rubocop_todo.yml
```

## When disabling is legitimate

- Generated or vendored code (schema/migrations under `db/`, `vendor/`, scaffolded files): exclude via `AllCops: Exclude`.
- A `Metrics` threshold that the team deliberately sets higher than the default: raise `Max` in configuration rather than sprinkling inline disables.
- A line that cannot comply, such as an unsplittable URL exceeding `Layout/LineLength`: single-line inline disable with a `--` justification.
- Unsafe cops producing false positives on metaprogramming-heavy code: disable the specific cop for the affected files only.
- Disabling the whole linter at MegaLinter level is the last resort — prefer fixing, then inline disable, then configuration exclusion.
