# Fix CSHARP_ROSLYNATOR errors

<!-- generated-descriptor-info-start -->
- Linter: **roslynator** (MegaLinter key: `CSHARP_ROSLYNATOR`)
- Descriptor: **CSHARP** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/csharp_roslynator/>
- Official documentation: <https://github.com/dotnet/Roslynator>
- Auto-fix support: **yes** — add `CSHARP_ROSLYNATOR` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter CSHARP_ROSLYNATOR --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Rules index: <https://josefpihrt.github.io/docs/roslynator/analyzers>
- Rules configuration: <https://josefpihrt.github.io/docs/roslynator/configuration>
- How to disable rules inline: <https://josefpihrt.github.io/docs/roslynator/how-to-suppress-diagnostic>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `CSHARP_ROSLYNATOR` to fully disable this linter
  - `CSHARP_ROSLYNATOR_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `CSHARP_ROSLYNATOR_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `CSHARP_ROSLYNATOR_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `CSHARP_ROSLYNATOR_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

Roslynator runs 200+ Roslyn analyzers on C# projects: common code-quality/style rules (`RCS1xxx`, e.g. redundancy removal, `nameof` usage, async naming), formatting rules (`RCS0xxx`, blank lines, braces, line breaks) and Roslyn-API rules (`RCS9xxx`).

- Look up each reported `RCSxxxx` id in the rules index, then apply the suggested rewrite: remove the redundant code, simplify the expression, rename the member, or adjust modifiers/formatting as the rule describes.
- Prefer the automatic fix: most analyzers ship a code fix. Run `roslynator fix <PROJECT|SOLUTION>` (the project must build first) to apply all available fixes, optionally scoping with `--supported-diagnostics RCS1008` or `--ignored-diagnostics`, and `--format` to reformat fixed documents.
- In MegaLinter, enable the auto-fix option listed in the block above instead of fixing by hand.
- For formatting-only findings (`RCS0xxx`), apply the fix command rather than manual edits.

## Inline disable

Use standard C# `#pragma` directives with the diagnostic id:

```csharp
#pragma warning disable RCS1008
var x = Foo(); // diagnostic suppressed here
#pragma warning restore RCS1008
```

Or suppress at declaration level with an attribute:

```csharp
[SuppressMessage("Readability", "RCS1008", Justification = "Explicit type hurts readability here")]
void M() { }
```

Assembly-level `[assembly: SuppressMessage(..., Scope = "member", Target = "~M:C.M")]` entries (typically in `GlobalSuppressions.cs`) suppress a single member or a whole namespace (`Scope = "NamespaceAndDescendants"`).

## Ignore via configuration

Configure rules per project in `.editorconfig` (severity `none` disables a rule):

```ini
[*.cs]
# Disable one analyzer
dotnet_diagnostic.rcs1015.severity = none
# Lower all Roslynator analyzers to suggestions
dotnet_analyzer_diagnostic.category-roslynator.severity = suggestion
# Analyzer behavior options
roslynator_use_var = when_type_is_obvious
```

For machine-wide defaults, use a global `.roslynatorconfig` (must contain `is_global = true`, no `[*.cs]` sections) where you can also set `roslynator_analyzers.enabled_by_default = false` and re-enable rules selectively. There is no dedicated ignore-file mechanism; exclude files via `.editorconfig` sections or generated-code conventions.

## When disabling is legitimate

- Generated code (designer files, source generators, scaffolded clients) that will be regenerated and should not be hand-edited.
- Opinionated style rules that conflict with the team's agreed conventions (e.g. `var` usage, blank-line formatting) — configure them once in `.editorconfig` rather than suppressing inline everywhere.
- Rare false positives on a specific construct: suppress inline with a `Justification`, keep the rule active elsewhere.
- Rules overlapping with another active formatter/analyzer (e.g. dotnet-format or StyleCop) producing contradictory fixes.

Disabling the linter at MegaLinter level is the last resort — prefer fixing, then inline suppression, then rule configuration.
