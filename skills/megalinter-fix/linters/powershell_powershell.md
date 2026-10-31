# Fix POWERSHELL_POWERSHELL errors

<!-- generated-descriptor-info-start -->
- Linter: **powershell** (MegaLinter key: `POWERSHELL_POWERSHELL`)
- Descriptor: **POWERSHELL** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/powershell_powershell/>
- Official documentation: <https://github.com/PowerShell/PSScriptAnalyzer>
- Auto-fix support: **yes** — add `POWERSHELL_POWERSHELL` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter POWERSHELL_POWERSHELL --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `.powershell-psscriptanalyzer.psd1` (custom path can be defined with `POWERSHELL_POWERSHELL_CONFIG_FILE`)
- Rules index: <https://learn.microsoft.com/en-us/powershell/utility-modules/psscriptanalyzer/rules/readme?view=ps-modules>
- Rules configuration: <https://learn.microsoft.com/en-us/powershell/utility-modules/psscriptanalyzer/using-scriptanalyzer?view=ps-modules#explicit>
- How to disable rules inline: <https://learn.microsoft.com/en-us/powershell/utility-modules/psscriptanalyzer/using-scriptanalyzer?view=ps-modules#suppressing-rules>
- Error line format (regex): `(?m)^\s*(Information|Warning|Error|ParseError)\s`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `POWERSHELL_POWERSHELL` to fully disable this linter
  - `POWERSHELL_POWERSHELL_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `POWERSHELL_POWERSHELL_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `POWERSHELL_POWERSHELL_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `POWERSHELL_POWERSHELL_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

PSScriptAnalyzer checks PowerShell scripts and modules against best-practice rules (naming, security, style, DSC) and also reports parser errors. Fix strategy by category:

- `ParseError` rows are syntax errors: fix the script code itself first, they cannot be suppressed.
- `PSAvoidUsingCmdletAliases`: replace aliases with full cmdlet names (`ls` → `Get-ChildItem`).
- `PSUseApprovedVerbs` / `PSUseSingularNouns`: rename functions to `ApprovedVerb-SingularNoun` (see `Get-Verb`).
- `PSAvoidUsingWriteHost`: use `Write-Output`, `Write-Verbose` or `Write-Information` instead.
- `PSUseDeclaredVarsMoreThanAssignments`: remove or actually use the assigned variable.
- `PSPossibleIncorrectComparisonWithNull`: put `$null` on the left side (`$null -eq $x`).
- Security errors (`PSAvoidUsingPlainTextForPassword`, `PSAvoidUsingConvertToSecureStringWithPlainText`, `PSAvoidUsingUsernameAndPasswordParams`): switch to `[SecureString]` / `[PSCredential]` parameters instead of plain-text strings.
- Formatting rules (`PSPlaceOpenBrace`, `PSUseConsistentIndentation`, `PSUseConsistentWhitespace`, `PSAvoidTrailingWhitespace`): reformat as reported.

Some rules ship suggested corrections (`AvoidAlias`, `AvoidUsingPlainTextForPassword`, `MisleadingBacktick`, `MissingModuleManifestField`, `UseToExportFieldsInManifest`): apply them with `Invoke-ScriptAnalyzer -Path MyScript.ps1 -Fix` (supports `-WhatIf`), or use the MegaLinter auto-fix described in the block above. Review fixed files: some corrections need manual follow-up and file encoding may change.

## Inline disable

Decorate a script, function or `param()` block with .NET's `SuppressMessageAttribute`: first argument is the rule name, second is `''` (or a parameter name to target it), plus an optional `Justification`. Suppression applies to the whole decorated scope; optional `Scope='Function'` and `Target` (wildcard/regex) narrow or broaden it.

```powershell
function Get-Something {
    [Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSAvoidUsingWriteHost', '',
        Justification = 'Interactive banner is intentional')]
    param()
    Write-Host 'Hello'
}
```

Parser errors cannot be suppressed this way.

## Ignore via configuration

The configuration file is a PowerShell data file (`.psd1`) passed to `Invoke-ScriptAnalyzer -Settings`. Use `ExcludeRules` to drop rules, `IncludeRules` to allow-list them, and `Severity` to filter levels:

```powershell
@{
    Severity     = @('Error', 'Warning')
    ExcludeRules = @('PSAvoidUsingCmdletAliases', 'PSAvoidUsingWriteHost')
}
```

PSScriptAnalyzer has no ignore-file mechanism for excluding paths; exclude files at MegaLinter level with the filter variable listed in the block above.

## When disabling is legitimate

- `PSAvoidUsingWriteHost` in scripts whose purpose is interactive console output (banners, menus, colored progress).
- `PSUseShouldProcessForStateChangingFunctions` / `ShouldProcess` on simple internal helpers where `-WhatIf` support adds no value.
- Compatibility rules (`PSUseCompatibleCmdlets`, `PSUseCompatibleSyntax`) when the script deliberately targets a single, known PowerShell version.
- `PSAvoidUsingCmdletAliases` for intentionally terse one-liners in test fixtures or generated code.

Prefer a scoped `SuppressMessageAttribute` with a `Justification`, then a rule exclusion in the settings file; disabling the linter or rules at MegaLinter level is the last resort.
