# Fix ARM_ARM_TTK errors

<!-- generated-descriptor-info-start -->
- Linter: **arm-ttk** (MegaLinter key: `ARM_ARM_TTK`)
- Descriptor: **ARM** (tooling_format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/arm_arm_ttk/>
- Official documentation: <https://github.com/Azure/arm-ttk>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.arm-ttk.psd1` (custom path can be defined with `ARM_ARM_TTK_CONFIG_FILE`)
- Rules configuration: <https://docs.microsoft.com/en-us/azure/azure-resource-manager/templates/test-toolkit#customize-tests>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `ARM_ARM_TTK` to fully disable this linter
  - `ARM_ARM_TTK_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `ARM_ARM_TTK_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `ARM_ARM_TTK_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `ARM_ARM_TTK_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

arm-ttk (`Test-AzTemplate`) checks Azure Resource Manager JSON templates against Microsoft's
recommended practices: author intent (unused parameters/variables), security (secrets in plain
text), and correct use of ARM template language constructs. Fix each failed test manually:

- `apiVersions Should Be Recent`: bump the resource `apiVersion` to one of the "Valid Api
  Versions" listed in the error message (must be latest or under 2 years old).
- `Location Should Not Be Hardcoded` / `Resources Should Have Location`: replace literal regions
  with a `location` parameter defaulting to `[resourceGroup().location]`.
- `adminUsername Should Not Be A Literal` / `Password params must be secure` /
  `Secure String Parameters Cannot Have Default`: make credential parameters `secureString`
  (or `secureObject`) and remove their default values.
- `Outputs Must Not Contain Secrets` / `CommandToExecute Must Use ProtectedSettings For Secrets`:
  never emit secrets in `outputs`; move secret arguments into `protectedSettings`.
- `Parameters Must Be Referenced` / `Variables Must Be Referenced`: delete unused parameters and
  variables, or reference them where intended.
- `DeploymentTemplate Schema Is Correct`: update the `$schema` value to a current, non-deprecated
  deployment template schema.
- `DeploymentTemplate Must Not Contain Hardcoded Uri`: build URIs with environment/reference
  functions instead of hard-coded endpoint strings.

Reproduce locally with PowerShell: `Import-Module ./arm-ttk.psd1` then
`Test-AzTemplate -TemplatePath ./folder` (add `-Test "Test Name"` to re-run a single test).

## Inline disable

arm-ttk has no inline suppression syntax inside ARM template JSON files. The closest alternative
is skipping tests via the `.arm-ttk.psd1` configuration file (see below), or excluding the file
from the linter with `ARM_ARM_TTK_FILTER_REGEX_EXCLUDE`.

## Ignore via configuration

The configuration file is a PowerShell data file whose keys are splatted as `Test-AzTemplate`
parameters: `Test` (run only these tests), `Skip` (skip these tests), and `SkipByFile`
(hashtable of filename wildcards mapped to lists of test wildcards to skip for those files).

```powershell
@{
    Skip = @(
        'apiVersions Should Be Recent'
    )
    SkipByFile = @{
        '*legacy*.json' = @('Location Should Not Be Hardcoded')
    }
}
```

To remove a test permanently from a self-managed arm-ttk install, delete its `*.test.ps1` file
from the relevant `testcases` folder; adding your own `*.test.ps1` file creates a custom test.

## When disabling is legitimate

- `apiVersions Should Be Recent` on templates that must pin an older, still-supported API version
  for behavioral compatibility.
- Marketplace- or createUiDefinition-specific tests on templates never published to Azure
  Marketplace.
- Legacy or generated templates kept only for reference, better skipped per file with
  `SkipByFile` than fixed.
- Since arm-ttk v0.10 new rule investment targets the Bicep linter, so a rule gap affecting a
  modern pattern may justify a targeted `Skip`.

Prefer fixing the template, then a targeted `Skip`/`SkipByFile` entry; disabling at MegaLinter
level (`DISABLE_LINTERS`, `ARM_ARM_TTK_DISABLE_ERRORS`) is the last resort.
