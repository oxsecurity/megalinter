# Fix SCALA_SCALAFIX errors

<!-- generated-descriptor-info-start -->
- Linter: **scalafix** (MegaLinter key: `SCALA_SCALAFIX`)
- Descriptor: **SCALA** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/scala_scalafix/>
- Official documentation: <https://scalacenter.github.io/scalafix/>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.scalafix.conf` (custom path can be defined with `SCALA_SCALAFIX_CONFIG_FILE`)
- Rules index: <https://scalacenter.github.io/scalafix/docs/rules/overview.html>
- Rules configuration: <https://scalacenter.github.io/scalafix/docs/users/configuration.html>
- How to disable rules inline: <https://scalacenter.github.io/scalafix/docs/users/suppression.html>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `SCALA_SCALAFIX` to fully disable this linter
  - `SCALA_SCALAFIX_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `SCALA_SCALAFIX_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `SCALA_SCALAFIX_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `SCALA_SCALAFIX_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `SCALA_SCALAFIX_ERROR_RULE_NOT_FOUND`
  - `SCALA_SCALAFIX_ERROR_NO_SEMANTICDB`
  - `SCALA_SCALAFIX_ERROR_CONFIG_PARSE`
<!-- generated-descriptor-info-end -->

## Fix instructions

scalafix is a refactoring and linting tool for Scala. MegaLinter runs it with `--check`, which only reports diagnostics; scalafix itself can rewrite code when run without that flag: `scalafix --config .scalafix.conf <files>` (or `sbt scalafixAll` from a build). Note that MegaLinter runs scalafix without the project classpath, so only **syntactic** rules can run; semantic rules (`ExplicitResultTypes`, `OrganizeImports`, `RemoveUnused`, `NoAutoTupling`) need a SemanticDB-enabled build and must be fixed via the build tool.

Fix strategy per common rule:

- `DisableSyntax.*` (var, null, throw, XML literals, finalize, ...): remove the forbidden construct — replace `var` with `val` plus immutable transformations, `null` with `Option`, `throw` with typed error channels (`Either`, `Try`).
- `ProcedureSyntax`: replace deprecated procedure syntax `def foo() { ... }` with an explicit result type: `def foo(): Unit = { ... }`.
- `NoValInForComprehension`: remove the deprecated `val` keyword inside for-comprehension binders (`for { val x = ... }` becomes `for { x = ... }`).
- `LeakingImplicitClassVal`: add `private` to the value parameter of an implicit value class: `implicit class Ops(private val s: String) extends AnyVal`.
- `RedundantSyntax`: delete the unnecessary syntax reported, such as `final` modifiers on objects.
- Semantic-rule diagnostics reported from a local run (`RemoveUnused`, `NoAutoTupling`, ...): run `sbt scalafixAll` locally to apply the automated rewrites, then commit the result.

## Inline disable

Suppress a single expression with `// scalafix:ok`, optionally targeting rules and adding a reason after a semicolon:

```scala
var x: Int = 0 // scalafix:ok DisableSyntax.var; I need mutability
```

Suppress a region with `// scalafix:off` / `// scalafix:on` (rule names optional, comma-separated); an unpaired `scalafix:off` disables scalafix for the rest of the file:

```scala
// scalafix:off DisableSyntax.null, DisableSyntax.asInstanceOf
foo(null)
1.asInstanceOf[String]
// scalafix:on
```

## Ignore via configuration

The configuration file uses HOCON. Choose which rules run through the `rules` array, tune a rule with top-level keys, and demote or silence diagnostics with `lint.ignore` / `lint.warning` / `lint.error` (regex patterns on diagnostic IDs):

```hocon
rules = [
  DisableSyntax,
  ProcedureSyntax
]
DisableSyntax.noFinalize = true
lint.ignore = ["DisableSyntax.throw"]
```

scalafix has no ignore-file or file-exclusion mechanism in its configuration; exclude files at MegaLinter level with the filter variable listed in the block above.

## When disabling is legitimate

- Semantic rules left in `.scalafix.conf` for build-tool runs: they cannot execute in MegaLinter (no SemanticDB), so keep them out of the shared config or demote their diagnostics rather than fighting false failures.
- Generated sources (protobuf, OpenAPI, sbt-generated code) that intentionally use constructs banned by `DisableSyntax`.
- Legacy or interop code where `null` / `asInstanceOf` is imposed by a Java API: suppress the specific rule inline with a reason comment instead of relaxing it globally.
- Deliberate performance-critical mutability (`var` in a hot loop): suppress locally with `// scalafix:ok DisableSyntax.var; reason`.

Disabling the linter at MegaLinter level (`DISABLE_LINTERS` or `SCALA_SCALAFIX_DISABLE_ERRORS`) is the last resort.
