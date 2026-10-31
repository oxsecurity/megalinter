# Fix SALESFORCE_CODE_ANALYZER_FLOW errors

<!-- generated-descriptor-info-start -->
- Linter: **code-analyzer-flow** (MegaLinter key: `SALESFORCE_CODE_ANALYZER_FLOW`)
- Descriptor: **SALESFORCE** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/salesforce_code_analyzer_flow/>
- Official documentation: <https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/engine-flow.html>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `code-analyzer-flow.yml` (custom path can be defined with `SALESFORCE_CODE_ANALYZER_FLOW_CONFIG_FILE`)
- Rules index: <https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/rules-flow.html>
- Rules configuration: <https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/config.html>
- Error line format (regex): `Found ([0-9]+) violation\(s\)`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `SALESFORCE_CODE_ANALYZER_FLOW` to fully disable this linter
  - `SALESFORCE_CODE_ANALYZER_FLOW_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `SALESFORCE_CODE_ANALYZER_FLOW_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `SALESFORCE_CODE_ANALYZER_FLOW_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `SALESFORCE_CODE_ANALYZER_FLOW_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `SALESFORCE_CODE_ANALYZER_FLOW_ERROR_CONFIG_INVALID`
  - `SALESFORCE_CODE_ANALYZER_FLOW_ERROR_NO_TARGET_FILES`
  - `SALESFORCE_CODE_ANALYZER_FLOW_ERROR_PYTHON_MISSING`
<!-- generated-descriptor-info-end -->

## Fix instructions

The Flow Scanner engine of Salesforce Code Analyzer audits `*.flow-meta.xml` files for security and
reliability issues. There is no auto-fix: open each flagged Flow in Flow Builder (or edit the XML) and
apply the fix matching the rule. List all rules and their details with
`sf code-analyzer rules --rule-selector flow --view detail`.

- **CyclicSubflow** (Critical): break circular subflow references — a flow must not (transitively) call itself as a subflow.
- **DbInLoop** (High): move Get/Create/Update/Delete Records elements out of Loop elements; accumulate records in a collection variable inside the loop, then run a single bulk data element after the loop.
- **MissingFaultHandler** (High): add a fault path (fault connector) to every element that can fail (data operations, actions), routing to error handling such as a notification or error screen.
- **PreventPassingUserDataIntoElementWithoutSharing** (High) / **PreventPassingUserDataIntoElementWithSharing** (Low): stop letting user-controlled input decide which records a CRUD element selects or modifies while the flow runs in system context; run the flow in user context with sharing enforced, or validate/constrain the input before the data element.
- **HardcodedId** (Moderate): replace hardcoded Salesforce record IDs with Get Records lookups, custom metadata, or custom labels so the flow works across orgs.
- **DefaultCopy** (Moderate): rename copied elements that still carry placeholder "copy" labels.
- **MissingDescription** (Low): fill in the description field of the flow and of flagged elements.

## Inline disable

Flow metadata XML has no inline suppression: Code Analyzer's `// Code-analyzer-suppress(...)`
comment markers apply to code files, not to `.flow-meta.xml`. Use the `suppressions` section of the
configuration file instead (see below).

## Ignore via configuration

The configuration file uses the standard Code Analyzer v5 `code-analyzer.yml` format. Suppress
expected violations per file with a documented reason:

```yaml
suppressions:
  "force-app/main/default/flows/Legacy_Order_Sync.flow-meta.xml":
    - rule_selector: "flow:MissingDescription"
      reason: "Legacy flow scheduled for rework - JIRA-1234"
```

Tune a rule globally under the `rules` section (override its `severity` or `tags`), and configure
the engine itself under `engines.flow` (`disable_engine`, `python_command`):

```yaml
rules:
  flow:
    MissingDescription:
      severity: Info
engines:
  flow:
    python_command: python3
```

## When disabling is legitimate

- The flagged Flow is auto-generated or vendor-managed (e.g. shipped by an installed package) and cannot be edited in your repo.
- `PreventPassingUserDataIntoElement*` fires on input that is already constrained upstream (picklist, validated record variable), making the data-injection scenario impossible.
- `MissingDescription` or `DefaultCopy` on throwaway or sandbox-only flows where documentation polish adds no value.
- A rule contradicts a deliberate, reviewed design decision (e.g. an intentional system-context flow with its own access checks).

Prefer a scoped `suppressions` entry with a `reason` in the configuration file; disabling the linter
or the rule at MegaLinter level is the last resort.
