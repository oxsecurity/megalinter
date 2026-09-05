# Fix PHP_PSALM errors

<!-- generated-descriptor-info-start -->
- Linter: **psalm** (MegaLinter key: `PHP_PSALM`)
- Descriptor: **PHP** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/php_psalm/>
- Official documentation: <https://psalm.dev>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `psalm.xml` (custom path can be defined with `PHP_PSALM_CONFIG_FILE`)
- Rules index: <https://psalm.dev/docs/running_psalm/issues/>
- Rules configuration: <https://psalm.dev/docs/running_psalm/configuration/>
- How to disable rules inline: <https://psalm.dev/docs/running_psalm/dealing_with_code_issues/#docblock-suppression>
- Error line format (regex): `([0-9]+) error`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `PHP_PSALM` to fully disable this linter
  - `PHP_PSALM_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `PHP_PSALM_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `PHP_PSALM_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `PHP_PSALM_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `PHP_PSALM_ERROR_MEMORY_EXHAUSTED`
  - `PHP_PSALM_ERROR_CONFIG_INVALID`
<!-- generated-descriptor-info-end -->

## Fix instructions

Psalm is a static analysis tool for PHP that finds type errors, null-safety problems, undefined
references and (optionally) tainted-input security issues. Fix errors by category:

- Type violations (`InvalidReturnType`, `InvalidArgument`, `MissingReturnType`, `MissingParamType`): add or correct native type declarations and docblock types so the declared type matches the actual value.
- Null/false safety (`PossiblyNullReference`, `PossiblyNullArgument`, `PossiblyFalseOperand`): guard the value with a `null`/`false` check (or assertion) before using it, instead of suppressing.
- Undefined references (`UndefinedVariable`, `UndefinedClass`, `UndefinedMethod`): fix the typo, add the missing `use` import, or initialize the variable on all code paths.
- Taint issues (`TaintedSql`, `TaintedInput`, `TaintedShell`): sanitize or parameterize the user-controlled input; never suppress these.

Psalm's companion tool Psalter can auto-fix 21 issue types (mostly missing/incorrect types and
unused code). Preview then apply:

```bash
vendor/bin/psalter --issues=all --dry-run
vendor/bin/psalter --issues=MissingReturnType,MissingParamType
```

`vendor/bin/psalm --alter` is an equivalent entry point. Note that MegaLinter does not run this
auto-fix for you: run it locally, review the diff, and commit.

## Inline disable

Use a `@psalm-suppress` docblock annotation on the statement, function, class or property. Use
`@psalm-suppress all` to suppress every issue in the scope (avoid it).

```php
/**
 * @psalm-suppress InvalidReturnType
 */
function foo(int $a): string {
    /** @psalm-suppress InvalidReturnStatement */
    return $a;
}
```

## Ignore via configuration

In the configuration file, tune reporting with `<issueHandlers>`: set an issue's `errorLevel` to
`suppress` (never reported), `info` (reported but non-blocking) or `error`, globally or restricted
to directories, files or referenced symbols. Exclude paths from analysis entirely with
`<ignoreFiles>` inside `<projectFiles>`.

```xml
<psalm errorLevel="4">
  <projectFiles>
    <directory name="src" />
    <ignoreFiles>
      <directory name="src/Generated" />
    </ignoreFiles>
  </projectFiles>
  <issueHandlers>
    <MissingPropertyType errorLevel="suppress" />
    <InvalidReturnType>
      <errorLevel type="suppress">
        <file name="legacy/some_bad_file.php" />
      </errorLevel>
    </InvalidReturnType>
  </issueHandlers>
</psalm>
```

The `errorLevel` attribute (1 = strictest, 8 = most permissive) sets the global detection level.
For legacy codebases, generate a baseline so only new issues are reported: run
`vendor/bin/psalm --set-baseline=psalm-baseline.xml`, reference it with
`<psalm errorBaseline="./psalm-baseline.xml">`, and refresh it with
`vendor/bin/psalm --update-baseline`.

## When disabling is legitimate

- False positives on magic methods, dynamic properties, or framework containers Psalm cannot resolve: prefer a targeted `@psalm-suppress` or a stub over lowering `errorLevel`.
- Generated or vendored code (proxies, compiled templates, stubs): exclude the directory with `<ignoreFiles>` rather than annotating each file.
- Adopting Psalm on a legacy codebase: use a baseline file so existing debt is frozen while new code stays strictly checked.
- Never suppress taint/security issues (`Tainted*`); fix the data flow instead. Disabling at MegaLinter level (`DISABLE_LINTERS`, `PHP_PSALM_DISABLE_ERRORS`) is the last resort.
