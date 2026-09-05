# Fix SALESFORCE_CODE_ANALYZER_APEX errors

<!-- generated-descriptor-info-start -->
- Linter: **code-analyzer-apex** (MegaLinter key: `SALESFORCE_CODE_ANALYZER_APEX`)
- Descriptor: **SALESFORCE** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/salesforce_code_analyzer_apex/>
- Official documentation: <https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/get-started.html>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `code-analyzer.yml` (custom path can be defined with `SALESFORCE_CODE_ANALYZER_APEX_CONFIG_FILE`)
- Rules index: <https://docs.pmd-code.org/latest/pmd_rules_apex.html>
- Rules configuration: <https://docs.pmd-code.org/latest/pmd_userdocs_making_rulesets.html>
- How to disable rules inline: <https://docs.pmd-code.org/latest/pmd_userdocs_suppressing_warnings.html>
- Error line format (regex): `Found ([0-9]+) violation\(s\)`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `SALESFORCE_CODE_ANALYZER_APEX` to fully disable this linter
  - `SALESFORCE_CODE_ANALYZER_APEX_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `SALESFORCE_CODE_ANALYZER_APEX_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `SALESFORCE_CODE_ANALYZER_APEX_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `SALESFORCE_CODE_ANALYZER_APEX_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `SALESFORCE_CODE_ANALYZER_APEX_ERROR_CONFIG_INVALID`
<!-- generated-descriptor-info-end -->

## Fix instructions

Salesforce Code Analyzer runs the PMD engine on Apex classes and triggers, reporting violations
grouped by category. There is no auto-fix: correct each violation manually by category.

- **Security** (`ApexCRUDViolation`, `ApexSOQLInjection`, `ApexSharingViolations`): enforce CRUD/FLS
  before DML and SOQL (user-mode operations or `Security.stripInaccessible`), use bind variables
  instead of string-built queries, and declare `with sharing` on classes.
- **Performance** (`OperationWithLimitsInLoop`, `AvoidNonRestrictiveQueries`): move SOQL, DML and
  other limit-consuming operations out of loops; bulkify by collecting records and operating on
  lists once. Add selective `WHERE`/`LIMIT` clauses to queries.
- **Error Prone** (`AvoidHardcodingId`, `EmptyCatchBlock`, `ApexCSRF`): replace hardcoded record Ids
  with queries or custom metadata, and handle or log exceptions instead of swallowing them.
- **Best Practices** (`ApexUnitTestClassShouldHaveAsserts`, `AvoidLogicInTrigger`,
  `AvoidGlobalModifier`): add assertions to every test method and move trigger logic into handler
  classes.
- **Design / Code Style / Documentation** (`CyclomaticComplexity`, `ClassNamingConventions`,
  `ApexDoc`): extract methods to reduce complexity, follow naming conventions, and add ApexDoc
  comments on classes, methods and properties.

## Inline disable

Use the PMD `@SuppressWarnings` annotation with **single quotes** (Apex syntax, unlike Java) on a
class or method, listing rules comma-separated in one string, or a `//NOPMD` comment on the
violating line:

```apex
@SuppressWarnings('PMD.UnusedLocalVariable, PMD.ApexDoc')
public class MyClass {
    private Integer bar; //NOPMD
}
```

`@SuppressWarnings('PMD')` suppresses all PMD rules for the annotated element — avoid it.

## Ignore via configuration

In the configuration file, override rules per engine under the `rules` section: set
`disabled: true` to ignore a rule everywhere, or adjust its `severity`/`tags`. Exclude files with
the `ignores` section (glob paths relative to the workspace):

```yaml
rules:
  pmd:
    ApexDoc:
      disabled: true
    CyclomaticComplexity:
      severity: Info
ignores:
  files:
    "force-app/legacy/**"
```

Only list the rules you override: Code Analyzer prioritizes this file over engine-specific
configuration such as a PMD XML ruleset, so a lean file avoids unintended overrides.

## When disabling is legitimate

- CRUD/FLS or sharing rules on service classes that intentionally run in system context
  (documented elevated-permission code paths).
- Documentation and naming rules (`ApexDoc`, naming conventions) on large legacy codebases where
  retrofitting is a separate effort.
- Generated or third-party code (managed package extensions, generated wrappers) — prefer the
  `ignores` file globs over disabling rules globally.
- Test-only patterns flagged by production-oriented rules, when the rule offers no test exclusion.

Disabling at MegaLinter level (`DISABLE_LINTERS` or `SALESFORCE_CODE_ANALYZER_APEX_DISABLE_ERRORS`)
is the last resort — prefer fixing, then inline suppression, then configuration-level ignores.
