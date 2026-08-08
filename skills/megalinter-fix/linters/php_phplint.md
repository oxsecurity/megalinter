# Fix PHP_PHPLINT errors

<!-- generated-descriptor-info-start -->
- Linter: **phplint** (MegaLinter key: `PHP_PHPLINT`)
- Descriptor: **PHP** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/php_phplint/>
- Official documentation: <https://github.com/overtrue/phplint>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.phplint.yml` (custom path can be defined with `PHP_PHPLINT_CONFIG_FILE`)
- Rules configuration: <https://github.com/overtrue/phplint/blob/main/docs/configuration.md#configuration>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `PHP_PHPLINT` to fully disable this linter
  - `PHP_PHPLINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `PHP_PHPLINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `PHP_PHPLINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `PHP_PHPLINT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

phplint checks PHP files for syntax (parse) errors only, by running several `php -l`
processes in parallel. It has no style or logic rules and no auto-fix: every reported
error is a fatal parse error that must be fixed by hand at the reported file and line.

- Read the reported message: it is the raw PHP parser error (e.g.
  `unexpected token`, `syntax error`), with the file and line where parsing stopped.
- Fix the usual culprits at or just before that line: missing semicolon or comma,
  unmatched brace/parenthesis/quote, stray characters, unclosed string or heredoc.
- If the code uses newer PHP syntax (e.g. enums, readonly, named arguments), the error
  means the PHP runtime executing the lint is older than the syntax requires: either
  rewrite for the older runtime or align the PHP version used to lint.
- Verify locally with `php -l path/to/file.php` or re-run
  `vendor/bin/phplint path/to/file.php` until it exits cleanly.
- With `warning: true` enabled in the configuration, PHP warnings are also surfaced;
  fix them the same way (they point to deprecated or fragile constructs).

## Inline disable

phplint has no inline suppression mechanism: a syntax error is fatal for the PHP
parser, so it cannot be ignored with a comment. The only alternative is to exclude
the file via the configuration file (see below) or fix the syntax.

## Ignore via configuration

Exclude paths in the configuration file with the `exclude` key (paths are relative to
the scanned base path). Other useful keys: `path` (what to scan), `extensions`
(file extensions checked, default `php`) and `jobs` (parallel processes).

```yaml
path: ./src
jobs: 10
extensions:
  - php
exclude:
  - vendor
  - legacy/generated
warning: false
```

There is no separate ignore file: all exclusions live in this YAML file (or are
passed on the command line, e.g. via a custom `--configuration` path).

## When disabling is legitimate

- Vendored or third-party PHP code (`vendor/`, bundled libraries) that you do not
  maintain: exclude the directory rather than patching upstream syntax.
- Generated PHP files (template caches, code generators) that are rebuilt on each
  run and may embed placeholders that are not valid standalone PHP.
- Template or fixture files with a `.php` extension that are intentionally partial
  PHP (test fixtures for parsers, mixed-content templates): exclude them or narrow
  `extensions`/`path`.
- Files written for a newer PHP version than the linting runtime, when upgrading the
  runtime is planned but not yet done: exclude temporarily and remove the exclusion
  after the upgrade.

Excluding in `.phplint.yml` keeps the rest of the repository covered; disabling the
linter at MegaLinter level is the last resort.
