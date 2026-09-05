# Fix GO_REVIVE errors

<!-- generated-descriptor-info-start -->
- Linter: **revive** (MegaLinter key: `GO_REVIVE`)
- Descriptor: **GO** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/go_revive/>
- Official documentation: <https://revive.run/>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `revive.toml` (custom path can be defined with `GO_REVIVE_CONFIG_FILE`)
- Rules index: <https://revive.run/r>
- Rules configuration: <https://revive.run/docs#custom-configuration>
- How to disable rules inline: <https://revive.run/docs#comment-directives>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `GO_REVIVE` to fully disable this linter
  - `GO_REVIVE_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `GO_REVIVE_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `GO_REVIVE_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `GO_REVIVE_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

revive is a fast, configurable replacement for golint: it checks Go code for style, naming, error-handling and complexity issues (100+ rules; without a config file it runs the golint default rule set). It has no auto-fix — every finding must be corrected manually.

Fix strategy by common rule category:

- **Naming** (`var-naming`, `receiver-naming`, `package-comments`, `exported`): rename identifiers to Go conventions (e.g. prefix error variables with `err`, use consistent receiver names) and add the required doc comments on exported symbols.
- **Error handling** (`error-return`, `error-strings`, `unhandled-error`): return the `error` as the last value, lowercase error messages without trailing punctuation, and handle or explicitly assign ignored errors.
- **Control flow** (`indent-error-flow`, `early-return`, `bare-return`, `max-control-nesting`): invert conditions to return early, name the returned values in `return` statements, and flatten deep nesting.
- **Complexity** (`cyclomatic`, `cognitive-complexity`, `function-length`): split large functions; if a threshold is intentionally different for the project, tune the rule arguments (e.g. `[rule.cyclomatic]` with `arguments = [10]`) instead of suppressing findings.
- **Correctness** (`range-val-in-closure`, `unchecked-type-assertion`, `defer`): copy loop variables before capturing them in goroutines, and use the two-value form `v, ok := x.(T)` for type assertions.

Reproduce locally with `revive -config revive.toml -formatter friendly ./...` to confirm each fix.

## Inline disable

Use revive comment directives, optionally scoped to a rule and followed by a reason:

```go
//revive:disable:unexported-return returned type is intentionally private
func Public() private {
    return private
}
//revive:enable:unexported-return
```

Single-line variants: `//revive:disable-next-line:<rule>` before the line, or `//revive:disable-line:<rule>` on the line itself. A bare `//revive:disable` / `//revive:enable` pair suppresses all rules in the range. Enable `[directive.specify-disable-reason]` in the configuration to make an explanation after the directive mandatory.

## Ignore via configuration

In the TOML configuration file, disable a rule globally or exclude files per rule:

```toml
[rule.line-length-limit]
Disabled = true

[rule.blank-imports]
Exclude = ["**/*.pb.go"]
```

Exclude whole paths with the CLI flag `-exclude <pattern>` (when no exclusion pattern is given, `vendor/...` is excluded by default). Note that listing rules in the file replaces the default set; use `enable-default-rules = true` to keep the golint defaults alongside your additions, or `enable-all-rules = true` to activate everything (the two options cannot be combined). revive has no dedicated ignore file.

## When disabling is legitimate

- Generated Go code (protobuf `*.pb.go`, mocks) that cannot follow naming or comment conventions — use per-rule `Exclude` patterns or `-exclude`.
- Opinionated style rules (`line-length-limit`, `package-comments`, comment wording) that conflict with an established project style — disable the rule in `revive.toml` rather than sprinkling inline directives.
- A single intentional divergence (e.g. a deliberately complex but readable function) — prefer a scoped `//revive:disable-next-line:<rule>` with a stated reason.
- Complexity thresholds that do not match the codebase — adjust the rule `arguments` before disabling the rule entirely.

Disabling the linter at MegaLinter level is the last resort.
