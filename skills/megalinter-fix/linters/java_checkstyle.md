# Fix JAVA_CHECKSTYLE errors

<!-- generated-descriptor-info-start -->
- Linter: **checkstyle** (MegaLinter key: `JAVA_CHECKSTYLE`)
- Descriptor: **JAVA** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/java_checkstyle/>
- Official documentation: <https://checkstyle.org/>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `sun_checks.xml` (custom path can be defined with `JAVA_CHECKSTYLE_CONFIG_FILE`)
- Rules index: <https://checkstyle.org/checks.html>
- Rules configuration: <https://checkstyle.org/config.html>
- How to disable rules inline: <https://checkstyle.org/checks/annotation/suppresswarnings.html#SuppressWarnings>
- Error line format (regex): `Checkstyle ends with ([0-9]+) errors`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `JAVA_CHECKSTYLE` to fully disable this linter
  - `JAVA_CHECKSTYLE_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `JAVA_CHECKSTYLE_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `JAVA_CHECKSTYLE_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `JAVA_CHECKSTYLE_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `JAVA_CHECKSTYLE_ERROR_OUT_OF_MEMORY`
  - `JAVA_CHECKSTYLE_ERROR_UNABLE_TO_PARSE_CONFIGURATION`
  - `JAVA_CHECKSTYLE_ERROR_CANNOT_INITIALIZE_MODULE`
<!-- generated-descriptor-info-end -->

## Fix instructions

Checkstyle enforces a Java coding standard: naming conventions, imports, whitespace, Javadoc,
sizes/metrics, blocks, class design and coding pitfalls. It has no auto-fix: fix code manually.

- Read each violation as `file:line:column: message [CheckName]` and look up the check name
  in the rules index to understand the expected style before editing.
- Naming checks (`MemberName`, `MethodName`, `ConstantName`...): rename the identifier to
  match the check's required pattern.
- Import checks (`AvoidStarImport`, `UnusedImports`, `RedundantImport`): replace wildcard
  imports with explicit ones and delete unused or duplicate imports.
- Whitespace and blocks checks (`WhitespaceAround`, `NeedBraces`, `LeftCurly`...): reformat
  the offending line; running an IDE formatter aligned with the Checkstyle config fixes most
  of these in bulk.
- Javadoc checks (`JavadocMethod`, `JavadocType`, `MissingJavadocMethod`...): add or complete
  the Javadoc comment with the required tags.
- Sizes/metrics checks (`LineLength`, `MethodLength`): wrap long lines, extract methods.

## Inline disable

Suppress with `@SuppressWarnings` using the check name (case-insensitive, without the `Check`
suffix) or the `checkstyle:` prefix. This requires `SuppressWarningsHolder` (in `TreeWalker`)
and `SuppressWarningsFilter` (in `Checker`) in the configuration:

```java
@SuppressWarnings("checkstyle:membername")
int J; // violation suppressed

@SuppressWarnings({"MemberName", "NoWhitespaceAfter"})
int[] ARRAY; // both violations suppressed
```

If `SuppressionCommentFilter` is enabled instead, use comment pairs:

```java
// CHECKSTYLE:OFF
problematicCode();
// CHECKSTYLE:ON
```

## Ignore via configuration

In the Checkstyle XML configuration, drop a rule by removing its `<module>` element, or keep
it visible but non-failing by lowering its severity:

```xml
<module name="LineLength">
  <property name="severity" value="ignore"/>
</module>
```

To exclude specific files or file patterns per check, declare a `SuppressionFilter` pointing
to a suppressions file:

```xml
<module name="SuppressionFilter">
  <property name="file" value="suppressions.xml"/>
</module>
```

```xml
<suppressions>
  <suppress checks="LineLength" files=".*Generated.*"/>
</suppressions>
```

## When disabling is legitimate

- Generated Java sources (protobuf, JAXB, annotation processors): exclude them via
  `SuppressionFilter` file patterns rather than editing generated code.
- Deliberate divergence from the default `sun_checks.xml` standard (e.g. a project using the
  Google style): switch to a custom configuration file instead of suppressing rule by rule.
- Legacy code where mass renaming (naming checks) or retro-documenting (Javadoc checks) would
  create risky, noisy diffs: suppress narrowly on the affected files.
- Test code intentionally violating style to exercise edge cases (odd identifiers, long
  literals): suppress inline on the specific member.

Disabling at MegaLinter level (`DISABLE_LINTERS`, `..._DISABLE_ERRORS`, filter variables) is
the last resort: prefer fixing the code or tuning the Checkstyle configuration itself.
