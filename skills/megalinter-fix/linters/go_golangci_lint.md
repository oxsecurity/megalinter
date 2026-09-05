# Fix GO_GOLANGCI_LINT errors

<!-- generated-descriptor-info-start -->
- Linter: **golangci-lint** (MegaLinter key: `GO_GOLANGCI_LINT`)
- Descriptor: **GO** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/go_golangci_lint/>
- Official documentation: <https://golangci-lint.run/>
- Auto-fix support: **yes** — add `GO_GOLANGCI_LINT` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter GO_GOLANGCI_LINT --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `.golangci.yml` (custom path can be defined with `GO_GOLANGCI_LINT_CONFIG_FILE`)
- Rules index: <https://golangci-lint.run/usage/linters/>
- Rules configuration: <https://golangci-lint.run/usage/configuration/#config-file>
- How to disable rules inline: <https://golangci-lint.run/usage/false-positives/#nolint>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `GO_GOLANGCI_LINT` to fully disable this linter
  - `GO_GOLANGCI_LINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `GO_GOLANGCI_LINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `GO_GOLANGCI_LINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `GO_GOLANGCI_LINT_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `GO_GOLANGCI_LINT_ERROR_MODULE_DOWNLOAD`
  - `GO_GOLANGCI_LINT_ERROR_CONFIG_INVALID`
  - `GO_GOLANGCI_LINT_ERROR_TYPECHECK`
  - `GO_GOLANGCI_LINT_ERROR_OUT_OF_MEMORY`
<!-- generated-descriptor-info-end -->

## Fix instructions

golangci-lint is an aggregator that runs many Go linters at once; by default it enables errcheck, govet, ineffassign, staticcheck and unused. Each reported issue is prefixed with the name of the linter that produced it — fix according to that linter's rule.

- Identify the responsible linter from the issue suffix (e.g. `(errcheck)`, `(staticcheck)`) and look it up in the rules index to understand the rule before changing code.
- `errcheck`: handle every returned `error` — check it, return it, or explicitly assign it to `_` only when discarding is intentional.
- `govet` / `staticcheck`: correctness bugs (wrong printf verbs, unreachable code, misuse of APIs) — fix the logic, do not suppress.
- `unused` / `ineffassign`: delete dead code and useless assignments instead of silencing them.
- Formatting/style linters (gofmt, goimports, misspell, revive...) support auto-fix: run `golangci-lint run --fix`, or let MegaLinter apply fixes via the `APPLY_FIXES` mechanism described above.
- If the run fails before linting (typecheck, module download), make the project compile first: `go build ./...` and `go mod tidy` — most analyzers require compilable code.

## Inline disable

Use a `//nolint` directive. The syntax is strict: no space between `//`, `nolint`, `:` and the linter names. Always target specific linters (comma-separated, or `all`) and add a `//`-separated explanation on the same line.

```go
var legacyTimeout int //nolint:mnd // documented historical value

//nolint:gocyclo // legacy function, refactor planned
func complexLegacyFunction() {
    // the whole block is excluded when the directive is on its own line above it
}
```

Placed before the `package` clause, the directive applies to the whole file.

## Ignore via configuration

In the configuration file (schema `version: "2"` for the golangci-lint v2 shipped by MegaLinter), disable whole linters or exclude issues by rule, path or source text under `linters`:

```yaml
version: "2"
linters:
  disable:
    - gocyclo
  exclusions:
    generated: lax        # skip issues in generated files (lax|strict|disable)
    rules:
      - path: '(.+)_test\.go'
        linters:
          - funlen
      - linters:
          - lll
        source: "^//go:generate "
    paths:
      - third_party/
```

Built-in exclusion presets (`comments`, `common-false-positives`, `legacy`, `std-error-handling`) can be listed under `linters.exclusions.presets` to drop well-known false positives. There is no separate ignore file: path exclusions live in this configuration file.

## When disabling is legitimate

- Known false positives of a specific sub-linter on valid code — prefer a targeted `//nolint:<linter> // reason` over widening configuration.
- Generated code (protobuf, mocks, stringer output) — rely on `linters.exclusions.generated` or a `paths` exclusion rather than editing generated files.
- Test files where strictness rules (function length, magic numbers, duplication) add no value — use a `path: '(.+)_test\.go'` exclusion rule.
- Intentional divergence from an opinionated style linter (e.g. revive naming rules conflicting with an established public API) — disable that one linter in the config, not the whole tool.
- Disabling `GO_GOLANGCI_LINT` at MegaLinter level is the last resort: prefer fixing, then inline `nolint`, then configuration exclusions.
