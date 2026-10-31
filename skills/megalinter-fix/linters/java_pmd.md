# Fix JAVA_PMD errors

<!-- generated-descriptor-info-start -->
- Linter: **pmd** (MegaLinter key: `JAVA_PMD`)
- Descriptor: **JAVA** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/java_pmd/>
- Official documentation: <https://pmd.github.io/>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `java-pmd-ruleset.xml` (custom path can be defined with `JAVA_PMD_CONFIG_FILE`)
- Rules index: <https://docs.pmd-code.org/pmd-doc-6.55.0/pmd_rules_java.html>
- Rules configuration: <https://docs.pmd-code.org/pmd-doc-6.55.0/pmd_userdocs_configuring_rules.html>
- How to disable rules inline: <https://docs.pmd-code.org/pmd-doc-6.55.0/pmd_userdocs_suppressing_warnings.html>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `JAVA_PMD` to fully disable this linter
  - `JAVA_PMD_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `JAVA_PMD_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `JAVA_PMD_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `JAVA_PMD_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

PMD is a static analyzer that flags Java constructs which are broken, confusing, inefficient or badly designed. It groups rules into eight categories: Best Practices, Code Style, Design, Documentation, Error Prone, Multithreading, Performance and Security. There is no auto-fix: correct each violation manually.

- **Error Prone** (`EmptyCatchBlock`, `CloseResource`): handle or log the exception instead of swallowing it; close resources with try-with-resources.
- **Best Practices** (`UnusedLocalVariable`, `AvoidPrintStackTrace`): delete dead variables and code; replace `printStackTrace()` with a logger call.
- **Design** (`CyclomaticComplexity`, `GodClass`, `TooManyMethods`): split large methods and classes into smaller, single-responsibility units.
- **Code Style** (`ControlStatementBraces`, `UnnecessaryImport`): add braces to control statements, remove duplicate or unused imports, follow naming conventions.
- **Performance** (`AvoidInstantiatingObjectsInLoops`, string concatenation rules): hoist object creation out of loops, use `StringBuilder` for repeated concatenation.
- **Multithreading** (`DoubleCheckedLocking`, `NonThreadSafeSingleton`): use safe initialization idioms (holder class, `enum` singleton) instead of hand-rolled locking.

Look up the exact rule name from the error message in the rules index (link above) — each rule page explains the problem and shows compliant code.

## Inline disable

Suppress a specific rule with `@SuppressWarnings` using the `PMD.` prefix (use `"PMD"` alone to suppress all rules, or an array for several rules):

```java
@SuppressWarnings("PMD.UnusedLocalVariable")
public class Bar {
    void bar() {
        int foo;
    }
}
```

For a single line, append a `//NOPMD` comment (a trailing justification is allowed):

```java
catch (FileNotFoundException e) {} // NOPMD - cannot happen, file checked above
```

## Ignore via configuration

In the ruleset XML file, reference a whole category and exclude specific rules:

```xml
<rule ref="category/java/codestyle.xml">
    <exclude name="ControlStatementBraces"/>
</rule>
```

Exclude files with `<exclude-pattern>` at ruleset level (an `<include-pattern>` re-includes matches):

```xml
<exclude-pattern>.*/generated/.*</exclude-pattern>
```

Narrow a single rule instead of disabling it, either by tuning its properties (e.g. `reportLevel` for complexity rules) or with `violationSuppressRegex` / `violationSuppressXPath` properties to suppress only matching violations:

```xml
<rule ref="category/java/design.xml/NPathComplexity">
    <properties>
        <property name="reportLevel" value="150"/>
    </properties>
</rule>
```

PMD has no separate ignore file: all exclusions live in the ruleset XML.

## When disabling is legitimate

- Generated or third-party sources (protobuf, JAXB, vendored code): exclude their directories with `<exclude-pattern>` rather than editing generated files.
- Rules whose default thresholds do not fit the project (e.g. `CyclomaticComplexity`, `TooManyMethods`): tune the rule properties before excluding the rule.
- Documented false positives on a specific line: use `//NOPMD` or `@SuppressWarnings("PMD.RuleName")` with a justification comment, never a blanket `"PMD"` suppression.
- Opinionated Documentation or Code Style rules the team has explicitly decided against: exclude them once in the ruleset so the decision is versioned.

Disabling the linter at MegaLinter level (`DISABLE_LINTERS`, `JAVA_PMD_DISABLE_ERRORS`) is the last resort — prefer ruleset-level exclusions.
