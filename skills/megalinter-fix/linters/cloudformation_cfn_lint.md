# Fix CLOUDFORMATION_CFN_LINT errors

<!-- generated-descriptor-info-start -->
- Linter: **cfn-lint** (MegaLinter key: `CLOUDFORMATION_CFN_LINT`)
- Descriptor: **CLOUDFORMATION** (tooling_format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/cloudformation_cfn_lint/>
- Official documentation: <https://github.com/aws-cloudformation/cfn-lint>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.cfnlintrc.yml` (custom path can be defined with `CLOUDFORMATION_CFN_LINT_CONFIG_FILE`)
- Rules index: <https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/rules.md>
- Rules configuration: <https://github.com/aws-cloudformation/cfn-lint#configuration>
- How to disable rules inline: <https://github.com/aws-cloudformation/cfn-lint#metadata>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `CLOUDFORMATION_CFN_LINT` to fully disable this linter
  - `CLOUDFORMATION_CFN_LINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `CLOUDFORMATION_CFN_LINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `CLOUDFORMATION_CFN_LINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `CLOUDFORMATION_CFN_LINT_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `CLOUDFORMATION_CFN_LINT_ERROR_SCHEMA_DOWNLOAD`
  - `CLOUDFORMATION_CFN_LINT_ERROR_CUSTOM_RULE_IMPORT`
  - `CLOUDFORMATION_CFN_LINT_ERROR_CONFIG_INVALID`
<!-- generated-descriptor-info-end -->

## Fix instructions

cfn-lint validates CloudFormation templates against the AWS resource provider schemas plus best-practice
checks (valid property values, intrinsic functions, references). There is no auto-fix: correct the template manually.

Rule codes are prefixed by severity (`E` error, `W` warning, `I` informational) and grouped by number range:

- `E0xxx` basic template errors: fix JSON/YAML syntax and top-level section structure first, they mask other findings
- `E1xxx` functions: fix `Ref`/`GetAtt`/`FindInMap`/`Sub` usage so they reference resources/attributes that exist (e.g. `E1010` invalid `GetAtt`)
- `E2xxx` parameters: give parameters valid types, defaults and naming (e.g. `E2001`)
- `E3xxx` resources: fix invalid resource types, missing required properties and invalid property values (e.g. `E3002`); check the property name and allowed values in the AWS resource schema
- `E6xxx`/`E7xxx`/`E8xxx` outputs, mappings, conditions: align structure and names with the schema
- `W-codes` best-practice warnings (e.g. add `NoEcho` on secret parameters): apply the suggested practice rather than suppressing

Property-value validation through nested intrinsic functions is best effort, so verify a reported value is truly
wrong before suppressing. If templates target specific regions, pass `--regions` (via the arguments variable of
the generated block) so region-dependent checks match reality.

## Inline disable

Suppress a rule for a single resource by adding a `Metadata` block on that resource:

```yaml
Resources:
  myInstance:
    Type: AWS::EC2::Instance
    Metadata:
      cfn-lint:
        config:
          ignore_checks:
            - E3030
    Properties:
      InstanceType: nt.x4superlarge
```

Suppress for a whole template with a top-level `Metadata` section:

```yaml
Metadata:
  cfn-lint:
    config:
      ignore_checks:
        - E2530
```

## Ignore via configuration

In the configuration file, disable rules by ID or prefix, or skip whole templates:

```yaml
ignore_checks:
  - E3012
  - W
ignore_templates:
  - codebuild.yaml
include_checks:
  - I
```

Prefixes are hierarchical: `W` disables all warnings, `W2001` only that rule. `I` rules are off by default and
must be enabled with `include_checks: [I]` (CLI `--include-checks I`). Use `configure_rules` (CLI
`--configure-rule RuleId:key=value`) to tune a rule's parameters instead of disabling it. There is no separate
ignore file; the same effect is available on the CLI with `--ignore-checks`.

## When disabling is legitimate

- Best-effort value checks misfire on values built from nested intrinsic functions (`Sub`, `Join`, conditions): suppress on the affected resource only
- A brand-new AWS resource type or property is not yet in the bundled schemas: suppress the specific `E3xxx` rule until cfn-lint updates
- Strict type checks like `E3012` conflict with a deliberate team convention (e.g. quoted numbers): disable the single rule in the configuration file
- Third-party or generated templates you do not own: list them in `ignore_templates` rather than relaxing rules globally

Prefer resource-level Metadata, then template Metadata, then the configuration file; disabling the linter at
MegaLinter level is the last resort.
