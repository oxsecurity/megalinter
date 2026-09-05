# Fix PHP_PHPCS errors

<!-- generated-descriptor-info-start -->
- Linter: **phpcs** (MegaLinter key: `PHP_PHPCS`)
- Descriptor: **PHP** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/php_phpcs/>
- Official documentation: <https://github.com/PHPCSStandards/PHP_CodeSniffer>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `phpcs.xml` (custom path can be defined with `PHP_PHPCS_CONFIG_FILE`)
- Rules index: <https://gist.github.com/tmsnvd/057ef1cf4fd412e8c8e866e5ba5119bc>
- Rules configuration: <https://github.com/PHPCSStandards/PHP_CodeSniffer/wiki/Advanced-Usage#using-a-default-configuration-file>
- How to disable rules inline: <https://github.com/PHPCSStandards/PHP_CodeSniffer/wiki/Advanced-Usage#ignoring-parts-of-a-file>
- How to ignore files and directories: <https://github.com/PHPCSStandards/PHP_CodeSniffer/wiki/Advanced-Usage#ignoring-files-and-folders>
- Error line format (regex): `FOUND ([0-9]+) ERRORS?`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `PHP_PHPCS` to fully disable this linter
  - `PHP_PHPCS_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `PHP_PHPCS_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `PHP_PHPCS_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `PHP_PHPCS_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `PHP_PHPCS_ERROR_STANDARD_NOT_INSTALLED`
  - `PHP_PHPCS_ERROR_REFERENCED_SNIFF_NOT_FOUND`
<!-- generated-descriptor-info-end -->

## Fix instructions

phpcs (PHP_CodeSniffer) tokenizes PHP files and reports violations of a coding standard (PSR12 by default; PEAR, Squiz and custom rulesets are also supported). Most findings are formatting and style issues: indentation, spacing, brace placement, line length, naming conventions and missing documentation.

- Read each violation's sniff code (e.g. `Generic.Commenting.Todo.Found`) to understand which rule fired, then adjust the code to match the active standard.
- Although MegaLinter does not auto-fix with this linter, PHP_CodeSniffer ships a companion fixer: run `phpcbf /path/to/code` (same standard and ruleset resolution as phpcs) to automatically correct all fixable violations, then re-run `phpcs` to fix the remaining ones manually.
- Check the code against the same standard locally with `phpcs --standard=PSR12 /path/to/code` (or rely on the project ruleset file, auto-detected as `.phpcs.xml`, `phpcs.xml`, `.phpcs.xml.dist` or `phpcs.xml.dist`).

## Inline disable

Use `phpcs:` comment annotations, optionally scoped to sniff codes and followed by a `-- note`:

```php
// phpcs:disable Generic.Commenting.Todo.Found -- legacy code
$xmlPackage->send();
// phpcs:enable

$foo = [1,2,3]; // phpcs:ignore Squiz.Arrays.ArrayDeclaration.SingleLineNotAllowed
```

To skip an entire file, put `// phpcs:ignoreFile` right after the opening `<?php` tag.

## Ignore via configuration

In the ruleset file, exclude sniffs or silence a single message, and exclude paths with `<exclude-pattern>`:

```xml
<?xml version="1.0"?>
<ruleset name="CustomStandard">
  <rule ref="PSR12">
    <exclude name="Squiz.PHP.CommentedOutCode"/>
  </rule>
  <rule ref="Squiz.Strings.DoubleQuoteUsage.ContainsVar">
    <severity>0</severity>
  </rule>
  <exclude-pattern>*/vendor/*</exclude-pattern>
  <exclude-pattern>*/tests/*</exclude-pattern>
</ruleset>
```

There is no separate ignore file; use `<exclude-pattern>` entries (or the `--ignore=*/tests/*,*/data/*` CLI argument) to skip files and folders.

## When disabling is legitimate

- Third-party, vendored or generated PHP code that must not be reformatted (`<exclude-pattern>` on `vendor/`, generated folders).
- A team standard that intentionally diverges from the chosen ruleset (e.g. allowing double-quoted strings): disable that sniff globally with `<exclude>` or `<severity>0</severity>` rather than sprinkling inline comments.
- A single line where the compliant form is genuinely less readable (long array literals, aligned data tables): use a scoped `phpcs:ignore` with a `--` justification.
- Legacy files pending migration to the standard: `phpcs:ignoreFile` temporarily, with a tracking issue to clean them up.

Disabling the linter at MegaLinter level is the last resort; prefer fixing the code, then narrowing scope via ruleset or inline annotations.
