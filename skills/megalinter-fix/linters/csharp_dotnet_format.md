# Fix CSHARP_DOTNET_FORMAT errors

<!-- generated-descriptor-info-start -->
- Linter: **dotnet-format** (MegaLinter key: `CSHARP_DOTNET_FORMAT`)
- Descriptor: **CSHARP** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/csharp_dotnet_format/>
- Official documentation: <https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format>
- Auto-fix support: **yes** — add `CSHARP_DOTNET_FORMAT` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter CSHARP_DOTNET_FORMAT --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Rules configuration: <https://github.com/dotnet/sdk/tree/main/documentation/format/docs>
- How to disable rules inline: <https://docs.microsoft.com/en-us/dotnet/fundamentals/code-analysis/suppress-warnings>
- Error line format (regex): `.cs\([0-9]+,[0-9]+\):\s(?:warning|error)`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `CSHARP_DOTNET_FORMAT` to fully disable this linter
  - `CSHARP_DOTNET_FORMAT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `CSHARP_DOTNET_FORMAT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `CSHARP_DOTNET_FORMAT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `CSHARP_DOTNET_FORMAT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

dotnet-format is a formatter: it applies whitespace, code-style and analyzer preferences read from
`.editorconfig` to a project or solution, and MegaLinter runs it with `--verify-no-changes`, which
fails when any file would be reformatted. Do not hand-edit style issues one by one:

- Preferred: enable MegaLinter auto-fix (see the `APPLY_FIXES` line above) and commit the result.
- Locally, run the tool itself from the repository root: `dotnet format ./solution.sln` (or point it
  at a `.csproj`). Without an argument it picks up the `*proj`/`*.sln` file of the current directory.
- Target only one category when needed: `dotnet format whitespace` (indentation, spacing, newlines),
  `dotnet format style` (IDExxxx code-style rules) or `dotnet format analyzers` (CAxxxx quality rules).
- Fix a single reported diagnostic: `dotnet format style --diagnostics IDE0005 --severity info`.
- Reported lines match `file.cs(line,col): warning/error IDExxxx` — the diagnostic ID tells you which
  EditorConfig option or analyzer rule is involved; look it up in the rules index before changing config.

## Inline disable

Style and analyzer diagnostics can be suppressed for specific lines with `#pragma warning`:

```csharp
#pragma warning disable IDE0059 // Unnecessary assignment of a value
var unused = Compute();
#pragma warning restore IDE0059
```

Or per member/type with the attribute form (also usable in a `GlobalSuppressions.cs` file):

```csharp
[System.Diagnostics.CodeAnalysis.SuppressMessage("Usage", "CA2200:Rethrow to preserve stack details",
    Justification = "Explanation here")]
private static void MyMethod() { }
```

Pure whitespace formatting has no inline toggle — fix it or exclude the file via configuration.

## Ignore via configuration

Disable a rule for a whole project by setting its severity to `none` in `.editorconfig`:

```ini
[*.cs]
dotnet_diagnostic.IDE0055.severity = none
csharp_new_line_before_open_brace = none
```

Exclude paths or diagnostics on the command line (pass them through `CSHARP_DOTNET_FORMAT_ARGUMENTS`):

```bash
dotnet format --exclude ./src/Generated/ --exclude-diagnostics IDE0005
```

There is no dedicated ignore file; use `.editorconfig` section scoping (e.g. `[Generated/**.cs]`) or
`--exclude` to carve out paths. SDK-generated files are already skipped unless `--include-generated` is set.

## When disabling is legitimate

- Generated or vendored code (protobuf/OpenAPI output, migrations) that will be regenerated — exclude
  the path rather than reformatting it.
- A team style that intentionally diverges from a default rule — encode the choice in `.editorconfig`
  so the tool enforces your convention instead of fighting it.
- Analyzer false positives on a specific line — suppress with `#pragma warning disable` plus a
  `Justification`, never with a blanket severity change.
- Disabling the linter at MegaLinter level (`DISABLE_LINTERS`, `..._DISABLE_ERRORS`) is the last
  resort, when formatting cannot be applied at all for the repository.
