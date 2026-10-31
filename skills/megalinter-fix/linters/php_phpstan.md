# Fix PHP_PHPSTAN errors

<!-- generated-descriptor-info-start -->
- Linter: **phpstan** (MegaLinter key: `PHP_PHPSTAN`)
- Descriptor: **PHP** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/php_phpstan/>
- Official documentation: <https://phpstan.org/>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `phpstan.neon.dist` (custom path can be defined with `PHP_PHPSTAN_CONFIG_FILE`)
- Rules configuration: <https://phpstan.org/config-reference#neon-format>
- How to disable rules inline: <https://phpstan.org/user-guide/ignoring-errors#ignoring-in-code-using-phpdocs>
- Error line format (regex): `Found ([0-9]+) error`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `PHP_PHPSTAN` to fully disable this linter
  - `PHP_PHPSTAN_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `PHP_PHPSTAN_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `PHP_PHPSTAN_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `PHP_PHPSTAN_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `PHP_PHPSTAN_ERROR_MEMORY_EXHAUSTED`
  - `PHP_PHPSTAN_ERROR_CONFIG_INVALID`
<!-- generated-descriptor-info-end -->

## Fix instructions

PHPStan is a static analyser: it finds type errors, calls to unknown symbols, wrong argument
counts and dead code without running the PHP code. There is no auto-fix; correct the code manually.

- Undefined variable / class / function / method (levels 0-2): fix the typo, add the missing
  `use` import, or make sure the dependency is autoloadable by PHPStan.
- Wrong argument count or argument type (levels 0 and 5): align the call site with the real
  signature, or fix the signature/PHPDoc if it is the one that is wrong.
- Return type and property assignment mismatches (level 3): make the returned/assigned value
  match the declared type, or correct the declaration.
- Dead code, always-false `instanceof`, unreachable statements (level 4): delete the dead branch
  or fix the condition that makes it unreachable.
- Missing typehints (level 6+): add native parameter/return/property types, or `@param`/`@return`
  PHPDoc with generics where native types are not expressive enough.
- Calls on nullable types (level 8): guard with a null check (`if ($x !== null)`) or use the
  nullsafe operator `?->` when null propagation is acceptable.

Levels are cumulative (0 = loosest, 10 = strictest, `max` = highest). When adopting PHPStan on a
legacy codebase, keep the configured level and snapshot existing errors in a baseline instead of
fixing everything at once: `vendor/bin/phpstan analyse --generate-baseline` writes
`phpstan-baseline.neon`, which you then reference in the `includes:` section of the config file.

## Inline disable

Append `// @phpstan-ignore <identifier>` (preferred, targets one error identifier), or use
`@phpstan-ignore-line` / `@phpstan-ignore-next-line` to silence every error on a line:

```php
echo $foo; // @phpstan-ignore variable.undefined (defined dynamically by the framework)

// @phpstan-ignore-next-line
echo $bar;
```

Multiple identifiers are comma-separated, and a parenthesised comment after the identifier
documents why the error is ignored.

## Ignore via configuration

In the NEON configuration file, ignore errors by message regex, identifier and/or path, and
exclude files from analysis with `excludePaths` (patterns use `fnmatch()` syntax):

```neon
parameters:
    ignoreErrors:
        - '#Call to an undefined method [a-zA-Z0-9\\_]+::doFoo\(\)#'
        -
            identifier: property.notFound
            path: src/Legacy/*
    excludePaths:
        - tests/*/data/*
```

If an ignore entry no longer matches anything, PHPStan fails the run; set
`reportUnmatchedIgnoredErrors: false` or remove the stale entry. For bulk legacy debt, prefer the
baseline mechanism described above over long `ignoreErrors` lists.

## When disabling is legitimate

- The error comes from framework magic (dynamic properties, `__call`/`__get`) that PHPStan cannot
  see; prefer installing the framework's PHPStan extension before ignoring.
- The code is generated or vendored third-party code: exclude it with `excludePaths`.
- Legacy debt on an existing codebase: capture it in `phpstan-baseline.neon` so new code stays
  clean while old errors are fixed progressively.
- The reported pattern is intentional and type-safe in context (e.g. checked by a runtime
  assertion): ignore the specific identifier inline with a justification comment.

Disabling the linter or a rule at MegaLinter level is the last resort: prefer fixing the code,
then inline ignores, then PHPStan configuration.
