# Fix CSHARP_CSHARPIER errors

<!-- generated-descriptor-info-start -->
- Linter: **csharpier** (MegaLinter key: `CSHARP_CSHARPIER`)
- Descriptor: **CSHARP** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/csharp_csharpier/>
- Official documentation: <https://csharpier.com/>
- Auto-fix support: **yes** — add `CSHARP_CSHARPIER` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter CSHARP_CSHARPIER --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `.csharpierrc` (custom path can be defined with `CSHARP_CSHARPIER_CONFIG_FILE`)
- Ignore file: `.csharpierignore`
- Rules configuration: <https://csharpier.com/docs/Configuration>
- How to disable rules inline: <https://csharpier.com/docs/Ignore>
- How to ignore files and directories: <https://csharpier.com/docs/Ignore>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `CSHARP_CSHARPIER` to fully disable this linter
  - `CSHARP_CSHARPIER_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `CSHARP_CSHARPIER_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `CSHARP_CSHARPIER_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `CSHARP_CSHARPIER_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

CSharpier is an opinionated code formatter for C# (and XML): it does not report code-quality rules, it only fails when files are not formatted the way it would print them. The fix is never manual restyling — reformat the files:

- In MegaLinter, enable the auto-fix support described in the block above so the reformatted files are committed or pushed back.
- Locally, run CSharpier itself: `dotnet csharpier format .` rewrites all files in place, and `dotnet csharpier check .` verifies formatting without writing (exit code 1 on unformatted files, as used in CI).

If the reported style differs from your expectations (line width, tabs vs spaces, indent size, line endings), do not fight the formatter file by file: adjust the few available options in the configuration file (see below), then re-run the format command.

## Inline disable

Use `// csharpier-ignore` before a statement or member to leave it untouched, or wrap a region with `// csharpier-ignore-start` / `// csharpier-ignore-end`. An optional description can follow after a hyphen.

```csharp
// csharpier-ignore - hand-aligned matrix kept readable
public class Unformatted { }

// csharpier-ignore-start
public class Unformatted1 { }
public class Unformatted2 { }
// csharpier-ignore-end
```

For XML files, use the same keywords in XML comments: `<!-- csharpier-ignore -->`, `<!-- csharpier-ignore-start -->` / `<!-- csharpier-ignore-end -->`.

## Ignore via configuration

CSharpier has no per-rule toggles — only global layout options, settable in JSON or YAML form of its configuration file (an `.editorconfig` with `indent_style`, `indent_size` and `max_line_length` is also honored, but the CSharpier config file in the same directory takes priority):

```yaml
printWidth: 100
useTabs: false
indentSize: 4
endOfLine: auto
```

To exclude files or folders entirely, list them in the ignore file named in the block above, using gitignore syntax (patterns there take priority over `.gitignore`; prefix with `!` to force-format a git-ignored file):

```text
Uploads/**/App_Data/*.cs
Migrations/
```

Note that generated files such as `*.designer.cs` and `*.generated.cs` are already ignored by default.

## When disabling is legitimate

- Generated or scaffolded code (EF migrations, T4 output, vendored sources) that will be regenerated: exclude it in the ignore file rather than reformatting it.
- Deliberately hand-aligned constructs (matrices, lookup tables, fluent chains kept on aligned lines) where the printed layout hurts readability: use an inline ignore with a short description.
- Files shared with an upstream project that enforces a different formatter, where reformatting would create noisy diffs on every sync.
- Disabling the linter at MegaLinter level (variables listed in the block above) is the last resort — prefer running the formatter, tuning its few options, or scoping ignores narrowly.
