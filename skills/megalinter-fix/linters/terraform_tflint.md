# Fix TERRAFORM_TFLINT errors

<!-- generated-descriptor-info-start -->
- Linter: **tflint** (MegaLinter key: `TERRAFORM_TFLINT`)
- Descriptor: **TERRAFORM** (tooling_format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/terraform_tflint/>
- Official documentation: <https://github.com/terraform-linters/tflint>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.tflint.hcl` (custom path can be defined with `TERRAFORM_TFLINT_CONFIG_FILE`)
- Rules index: <https://github.com/terraform-linters/tflint-ruleset-terraform/blob/main/docs/rules/README.md>
- Rules configuration: <https://github.com/terraform-linters/tflint/blob/master/docs/user-guide/config.md>
- How to disable rules inline: <https://github.com/terraform-linters/tflint/blob/master/docs/user-guide/annotations.md>
- Error line format (regex): `Error:`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `TERRAFORM_TFLINT` to fully disable this linter
  - `TERRAFORM_TFLINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `TERRAFORM_TFLINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `TERRAFORM_TFLINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `TERRAFORM_TFLINT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

tflint finds possible errors for major cloud providers (invalid instance types, etc.), warns about
deprecated syntax and unused declarations, and enforces best practices and naming conventions.

- Read the rule name in the error message and open its page from the rules index to understand the expected form before editing.
- Deprecated syntax rules (`terraform_deprecated_interpolation`, `terraform_deprecated_index`, `terraform_comment_syntax`): rewrite `"${var.x}"` as `var.x`, dot index as bracket index, `//` comments as `#`.
- Unused declaration rules (`terraform_unused_declarations`, `terraform_unused_required_providers`): delete the unused variable, local, data source or provider requirement, or start using it.
- Documentation/typing rules (`terraform_documented_variables`, `terraform_documented_outputs`, `terraform_typed_variables`): add `description` and `type` attributes to variables and outputs.
- Pinning rules (`terraform_required_version`, `terraform_required_providers`, `terraform_module_pinned_source`, `terraform_module_version`): add version constraints to the `terraform` block, `required_providers`, and module `source`/`version`.
- Provider-plugin errors (e.g. `aws_instance_invalid_type`): fix the invalid value in the resource; these come from plugins declared in `.tflint.hcl` and installed with `tflint --init`.
- Many rules are auto-fixable by tflint itself: run `tflint --fix` locally to apply fixes, then review the diff (MegaLinter does not apply fixes for this linter).

## Inline disable

Add a `tflint-ignore` comment on the line above the offending expression:

```hcl
resource "aws_instance" "foo" {
  # tflint-ignore: aws_instance_invalid_type # not yet known by TFLint
  instance_type = "t1.2xlarge"
}
```

Use a comma-separated list for several rules (`# tflint-ignore: rule_a, rule_b`) or `# tflint-ignore: all`
for every rule. To ignore a whole file, put `# tflint-ignore-file: <rule>` on the very first line of the file
(in JSON files, use a top-level `"//"` property with the same text).

## Ignore via configuration

Disable a rule for the whole project with a `rule` block set to `enabled = false`:

```hcl
rule "terraform_documented_variables" {
  enabled = false
}
```

Skip evaluation of called modules by source in the `config` block:

```hcl
config {
  call_module_type = "all"
  ignore_module = {
    "terraform-aws-modules/vpc/aws" = true
  }
}
```

tflint has no dedicated ignore file for paths; exclude files at MegaLinter level with the filter-regex
variable listed above. A rule can also set `ignorable = false` to forbid inline annotations on it.

## When disabling is legitimate

- The provider plugin does not know a newly released value yet (e.g. a brand-new instance type flagged as invalid): ignore inline with a dated comment and remove it after the plugin update.
- Generated or vendored Terraform code you do not own: use `tflint-ignore-file` or exclude the paths.
- Opinionated rules that conflict with a deliberate team convention (naming convention, documented variables/outputs, standard module structure): disable the specific rule in `.tflint.hcl`.
- Third-party registry modules you cannot change: list them under `ignore_module`.
- Disabling the whole linter at MegaLinter level is the last resort; prefer fixing, then rule-level or file-level exclusions.
