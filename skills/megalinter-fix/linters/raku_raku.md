# Fix RAKU_RAKU errors

<!-- generated-descriptor-info-start -->
- Linter: **raku** (MegaLinter key: `RAKU_RAKU`)
- Descriptor: **RAKU** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/raku_raku/>
- Official documentation: <https://raku.org/>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `META6.json` (custom path can be defined with `RAKU_RAKU_CONFIG_FILE`)
- Rules configuration: <https://docs.raku.org/language/pragmas>
- How to disable rules inline: <https://docs.raku.org/language/pragmas#no>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `RAKU_RAKU` to fully disable this linter
  - `RAKU_RAKU_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `RAKU_RAKU_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `RAKU_RAKU_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `RAKU_RAKU_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

This linter is the Raku (Rakudo) compiler itself in compile-check mode: MegaLinter runs
`raku -I ./lib -c <file>`, which validates syntax and compile-time semantics without executing the code.
There is no auto-fix; correct the source until the file compiles.

- Read the compiler message first: it includes the file, line number and usually a suggestion; fix the exact construct it points at.
- For "Variable ... is not declared" errors, declare the variable with `my` (Raku is `strict` by default: every variable must be declared before use).
- For "Could not find module" errors, ensure the module is listed in the `depends` section of `META6.json` (MegaLinter runs `zef install --deps-only --/test .` before linting when that file is present) or that it lives under `./lib`, which is already on the include path via `-I ./lib`.
- For code in non-standard directories, add the path with the `lib` pragma, e.g. `use lib <lib /opt/lib>;`.
- Fix compile-time warnings (worries) as well: they are emitted by the same check and usually reveal real issues.
- Reproduce locally with the exact same command: `raku -I ./lib -c myfile.raku`.

## Inline disable

Compile **errors** cannot be suppressed: the code must be fixed. Compile-time **warnings**
(worries) can be disabled lexically with the `no worries` pragma, effective for the enclosing
block or file:

```raku
{
    no worries;
    say :foo<>.Pair;   # warning suppressed inside this block only
}
```

`use worries` re-enables warnings in an inner scope. Similarly, `no strict` lifts the
mandatory-declaration rule for a scope, but prefer declaring variables properly.

## Ignore via configuration

The Raku compiler has no lint-rule configuration and no ignore file. `META6.json` is the
module distribution metadata: it is used here to install dependencies before the check, not
to tune rules. Keep its `depends` list accurate so imports resolve:

```json
{
    "name": "My::Module",
    "depends": [ "JSON::Fast" ]
}
```

To skip files, use the MegaLinter file-exclusion tuning variables listed in the block above.

## When disabling is legitimate

- The file depends on a native library or external service that cannot be installed in the lint container, so module resolution can never succeed there.
- The file is generated or vendored Raku code you do not maintain (exclude it via the filter regex rather than editing it).
- A warning is a known false alarm for intentional code; scope a `no worries` block as narrowly as possible instead of disabling the linter.
- Disabling `RAKU_RAKU` at MegaLinter level is the last resort: it leaves Raku files with no compile validation at all.
