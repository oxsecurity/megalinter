# Fix REPOSITORY_DEVSKIM errors

<!-- generated-descriptor-info-start -->
- Linter: **devskim** (MegaLinter key: `REPOSITORY_DEVSKIM`)
- Descriptor: **REPOSITORY** (other)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/repository_devskim/>
- Official documentation: <https://github.com/microsoft/DevSkim>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.devskim.json` (custom path can be defined with `REPOSITORY_DEVSKIM_CONFIG_FILE`)
- Rules configuration: <https://github.com/microsoft/DevSkim/wiki/Analyze-Command>
- How to ignore files and directories: <https://github.com/microsoft/DevSkim/wiki/Analyze-Command>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `REPOSITORY_DEVSKIM` to fully disable this linter
  - `REPOSITORY_DEVSKIM_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `REPOSITORY_DEVSKIM_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `REPOSITORY_DEVSKIM_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `REPOSITORY_DEVSKIM_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `REPOSITORY_DEVSKIM_ERROR_RULES_NOT_FOUND`
<!-- generated-descriptor-info-end -->

## Fix instructions

DevSkim is a security static analyzer: each finding (rule ID `DSxxxxxx`) flags a dangerous API, weak
cryptography, hardcoded secret, insecure protocol or similar anti-pattern, with a severity of
Critical, Important, Moderate, BestPractice or ManualReview.

- Read the rule's guidance in the report, then replace the flagged construct with the secure
  alternative it recommends (e.g. swap a broken hash or cipher for a modern one, use `https://`
  instead of `http://`, use parameterized APIs instead of string concatenation).
- For hardcoded secrets or credentials: remove them from the code, rotate the exposed value, and
  load it from a secret store or environment configuration instead.
- Treat `ManualReview` findings as review prompts: verify the code is safe in context rather than
  mechanically rewriting it.
- DevSkim can apply its own suggested fixes from a previous SARIF report:
  `devskim fix -I <source-dir> -O <report.sarif>` (add `--dry-run` to preview, `--all` to apply
  every available fix, or `--rules DS123456` to restrict to given rules). MegaLinter itself runs
  DevSkim in analysis-only mode.

## Inline disable

Append a `DevSkim: ignore <ruleId>` comment at the end of the offending line, using the comment
syntax of the file's language. Suppress several rules by listing IDs separated by commas without
spaces, and optionally add `until YYYY-MM-DD` for a temporary suppression:

```python
hash = hashlib.md5(data)  # DevSkim: ignore DS126858
```

```csharp
var url = "http://internal.example";  // DevSkim: ignore DS137138 until 2026-12-31
```

The `devskim suppress -I <source-dir> -O <report.sarif>` command can insert these comments for you
(options: `--rules`, `--reviewer`, `--duration <days>`, `--dry-run`). Note that suppression
comments are honored unless the scan runs with `-d, --disable-suppression`.

## Ignore via configuration

The configuration file is a serialized set of `devskim analyze` options; the most useful keys are
`Globs` (comma-separated glob patterns of files to skip) and `IgnoreRuleIds` (rule IDs to disable
everywhere):

```json
{
  "Globs": ["**/generated/**", "**/*.min.js"],
  "IgnoreRuleIds": ["DS126858"],
  "LanguageRuleIgnoreMap": {"python": ["DS137138"]}
}
```

You can also narrow the scan with `Severities` / `Confidences` (same values as the `--severity` and
`--confidence` CLI options). DevSkim has no dedicated ignore file, but `--skip-git-ignored-files`
makes it respect `.gitignore`.

## When disabling is legitimate

- The finding is a false positive: the pattern match is textual and the flagged API is not actually
  used insecurely in context (e.g. an MD5 checksum used for non-security deduplication).
- The file is generated, vendored or minified code you do not maintain — exclude it with `Globs`
  rather than editing it.
- A `ManualReview` or `BestPractice` finding has been reviewed and accepted; prefer an inline
  suppression with `until` and a reviewer trail so the decision stays visible and time-boxed.
- A rule conflicts with a documented project constraint (e.g. a legacy protocol mandated by an
  external system) — disable that single rule ID, not the whole scan.

Disabling the linter at MegaLinter level is the last resort: prefer fixing the code, then inline
suppressions, then rule/file exclusions in the configuration file.
