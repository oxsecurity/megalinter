# Fix POWERSHELL_POWERSHELL_FORMATTER errors

<!-- generated-descriptor-info-start -->
- Linter: **powershell_formatter** (MegaLinter key: `POWERSHELL_POWERSHELL_FORMATTER`)
- Descriptor: **POWERSHELL** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/powershell_powershell_formatter/>
- Official documentation: <https://github.com/PowerShell/PSScriptAnalyzer>
- Auto-fix support: **yes** — add `POWERSHELL_POWERSHELL_FORMATTER` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter POWERSHELL_POWERSHELL_FORMATTER --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `.powershell-formatter.psd1` (custom path can be defined with `POWERSHELL_POWERSHELL_FORMATTER_CONFIG_FILE`)
- Rules index: <https://learn.microsoft.com/en-us/powershell/utility-modules/psscriptanalyzer/rules/readme?view=ps-modules>
- Rules configuration: <https://learn.microsoft.com/en-us/powershell/utility-modules/psscriptanalyzer/using-scriptanalyzer?view=ps-modules#explicit>
- How to disable rules inline: <https://learn.microsoft.com/en-us/powershell/utility-modules/psscriptanalyzer/using-scriptanalyzer?view=ps-modules#suppressing-rules>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `POWERSHELL_POWERSHELL_FORMATTER` to fully disable this linter
  - `POWERSHELL_POWERSHELL_FORMATTER_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `POWERSHELL_POWERSHELL_FORMATTER_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `POWERSHELL_POWERSHELL_FORMATTER_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `POWERSHELL_POWERSHELL_FORMATTER_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

This linter is a pure formatter: it runs PSScriptAnalyzer's `Invoke-Formatter` cmdlet, which rewrites
PowerShell script text according to code-formatting rules (by default the `CodeFormatting` preset:
brace placement, consistent indentation, consistent whitespace, casing, assignment alignment).

- Preferred fix: let MegaLinter apply the formatting automatically (auto-fix is supported, see above).
- To fix manually, run the formatter yourself and write the result back:

```powershell
pwsh -NoProfile -NoLogo -Command "Invoke-Formatter -ScriptDefinition (Get-Content myscript.ps1 -Raw)"
```

- Pass `-Settings <path-or-hashtable>` to format with a custom `.psd1` settings file instead of the
  default `CodeFormatting` settings; `-Range <start-line,start-col,end-line,end-col>` limits
  formatting to a region.
- Do not hand-edit whitespace to guess the expected style: run the formatter once and commit its output.

## Inline disable

`Invoke-Formatter` rewrites text according to its settings and does not honor per-line suppression
comments, so there is no inline mechanism specific to the formatter. PSScriptAnalyzer's
`SuppressMessageAttribute` only silences diagnostic rules reported by `Invoke-ScriptAnalyzer`:

```powershell
function Get-Thing {
    [Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSProvideCommentHelp', '',
        Justification = 'Just an example')]
    param()
}
```

To keep a file or a rule out of formatting, use the configuration file below (or the MegaLinter
exclude-regex variable listed in the section above).

## Ignore via configuration

The configuration file is a PowerShell data file (`.psd1`). Only the rules it selects are applied,
and each formatting rule exposes an `Enable` property plus rule-specific options:

```powershell
@{
    IncludeRules = @('PSPlaceOpenBrace', 'PSUseConsistentIndentation')
    Rules        = @{
        PSPlaceOpenBrace           = @{ Enable = $true; OnSameLine = $false }
        PSUseConsistentIndentation = @{ Enable = $true }
        PSUseConsistentWhitespace  = @{ Enable = $false }
    }
}
```

Configurable formatting rules include `PSPlaceOpenBrace`, `PSPlaceCloseBrace`,
`PSUseConsistentIndentation`, `PSUseConsistentWhitespace`, `PSAlignAssignmentStatement`,
`PSUseCorrectCasing`, and `PSAvoidUsingDoubleQuotesForConstantString`. There is no separate
ignore-file mechanism: exclude files with the MegaLinter exclude-regex variable.

## When disabling is legitimate

- The file is generated or vendored PowerShell (module manifests exported by tools, third-party
  scripts) whose formatting must stay byte-identical to upstream.
- The team intentionally diverges from a default style (e.g. Allman braces): configure the rule
  (`OnSameLine = $false`) in the settings file rather than disabling the linter.
- Reformatting can change file encoding; scripts that depend on a specific encoding may need the
  `POWERSHELL_POWERSHELL_FORMATTER_OUTPUT_ENCODING` variable adjusted instead of a rewrite.
- Disabling the linter at MegaLinter level is the last resort: prefer fixing, then rule
  configuration, then file exclusion.
