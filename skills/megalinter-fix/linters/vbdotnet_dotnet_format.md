# Fix VBDOTNET_DOTNET_FORMAT errors

<!-- generated-descriptor-info-start -->
- Linter: **dotnet-format** (MegaLinter key: `VBDOTNET_DOTNET_FORMAT`)
- Descriptor: **VBDOTNET** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/vbdotnet_dotnet_format/>
- Official documentation: <https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format>
- Auto-fix support: **yes** — add `VBDOTNET_DOTNET_FORMAT` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter VBDOTNET_DOTNET_FORMAT --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Rules configuration: <https://github.com/dotnet/sdk/tree/main/documentation/format/docs>
- How to disable rules inline: <https://docs.microsoft.com/en-us/dotnet/fundamentals/code-analysis/suppress-warnings>
- Error line format (regex): `.vb\([0-9]+,[0-9]+\):\s(?:warning|error)`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `VBDOTNET_DOTNET_FORMAT` to fully disable this linter
  - `VBDOTNET_DOTNET_FORMAT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `VBDOTNET_DOTNET_FORMAT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `VBDOTNET_DOTNET_FORMAT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `VBDOTNET_DOTNET_FORMAT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

dotnet-format is a formatter: it applies whitespace, code-style, and analyzer-based fixes to a
VB.NET project or solution according to `.editorconfig` settings (or built-in defaults when no
`.editorconfig` exists). In MegaLinter it runs in check mode (`--verify-no-changes`), which exits
non-zero when any file would be reformatted.

- Preferred fix: let the tool rewrite the files — enable MegaLinter auto-fix (see generated block
  above) or run locally `dotnet format ./solution.sln` (or a `.vbproj` path).
- Fix only whitespace issues: `dotnet format whitespace` (add `--folder` to treat the argument as
  a plain folder of code files instead of a project/solution).
- Fix code-style diagnostics (IDExxxx): `dotnet format style --severity info` or target one rule
  with `dotnet format style --diagnostics IDE0005`.
- Fix analyzer quality diagnostics (CAxxxx): `dotnet format analyzers --diagnostics CA1831`.
- Limit scope with `--include ./src/ --exclude ./src/generated/` (space-separated relative paths);
  `--severity` accepts `info`, `warn` (default), `error`.
- Verify before pushing: `dotnet format --verify-no-changes`.

## Inline disable

Formatting (whitespace) differences cannot be suppressed inline — fix them or exclude the file.
Style/analyzer diagnostics use the standard .NET suppression mechanisms:

```vb
#Disable Warning CA2200 ' Rethrow to preserve stack details
        Throw e
#Enable Warning CA2200
```

Or suppress a member/scope with the attribute (also usable in a `GlobalSuppressions.vb` file):

```vb
<System.Diagnostics.CodeAnalysis.SuppressMessage("Usage", "CA2200:Rethrow to preserve stack details", Justification:="Not production code.")>
```

## Ignore via configuration

Configuration lives in `.editorconfig`. Disable a rule by setting its severity to `none`:

```ini
[*.vb]
dotnet_diagnostic.CA2200.severity = none
```

Formatting preferences (indentation, spacing, newlines) are also driven by `.editorconfig`
options, so adjust those instead of disabling when the team style diverges from defaults.
There is no dedicated ignore file; exclude paths at invocation time via CLI arguments
(e.g. `--exclude ./src/generated/`) added through the MegaLinter arguments variable, or skip
specific diagnostics with `--exclude-diagnostics <IDs>`. Generated files are skipped by default
unless `--include-generated` is passed.

## When disabling is legitimate

- Generated or vendored VB code (designer files, scaffolded sources) that will be regenerated —
  exclude the paths rather than reformatting them.
- A team style intentionally diverging from the defaults — encode it in `.editorconfig` so the
  formatter enforces your style instead of being silenced.
- An analyzer diagnostic that is a false positive in a specific spot — use a targeted
  `#Disable Warning` with a justification comment, never a blanket severity change.
- Rules conflicting with another formatter or analyzer running on the same files — align both
  configurations before considering suppression.

Disabling the linter at MegaLinter level is the last resort: prefer fixing the code, tuning
`.editorconfig`, or excluding specific files first.
