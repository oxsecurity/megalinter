# Fix RUST_CLIPPY errors

<!-- generated-descriptor-info-start -->
- Linter: **clippy** (MegaLinter key: `RUST_CLIPPY`)
- Descriptor: **RUST** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/rust_clippy/>
- Official documentation: <https://github.com/rust-lang/rust-clippy>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.clippy.toml` (custom path can be defined with `RUST_CLIPPY_CONFIG_FILE`)
- Rules index: <https://rust-lang.github.io/rust-clippy/stable/index.html>
- Rules configuration: <https://github.com/rust-lang/rust-clippy#configuration>
- How to disable rules inline: <https://github.com/rust-lang/rust-clippy#allowingdenying-lints>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `RUST_CLIPPY` to fully disable this linter
  - `RUST_CLIPPY_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `RUST_CLIPPY_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `RUST_CLIPPY_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `RUST_CLIPPY_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

Clippy is the official Rust lint collection (800+ lints) that catches likely bugs, non-idiomatic code and performance issues on top of the compiler. Lints are grouped by category: `correctness` (deny by default), `suspicious`, `style`, `complexity`, `perf` (warn by default), plus opt-in groups `pedantic`, `restriction`, `nursery` and `cargo`.

- Read each diagnostic fully: Clippy names the lint (e.g. `clippy::needless_return`) and usually prints a concrete suggested replacement — apply that suggestion.
- Fix `correctness` lints first: they flag code that is outright wrong (e.g. `absurd_extreme_comparisons`) and fail the build.
- For `style` and `complexity` lints, rewrite the code to the idiomatic form shown in the suggestion rather than suppressing the lint.
- Many suggestions are machine-applicable: run `cargo clippy --fix` locally to apply them automatically (it implies `--all-targets`). Review the resulting diff — suggestions marked "MaybeIncorrect" need manual verification.
- Look up any unclear lint in the rules index (link above): each entry explains why the pattern is bad and shows a compliant example.

## Inline disable

Use Rust lint-level attributes with the `clippy::` prefix on the item, or crate-wide with the inner `#![allow(...)]` form.

```rust
#[allow(clippy::too_many_arguments)]
fn setup(a: u8, b: u8, c: u8, d: u8, e: u8, f: u8, g: u8, h: u8) {}

// Crate-wide, at the top of lib.rs / main.rs:
#![allow(clippy::single_match)]
```

The same attribute syntax accepts `warn` and `deny` to raise a lint's level instead of silencing it.

## Ignore via configuration

The configuration file only tunes lint *behavior* (thresholds, MSRV, allowed names) — it cannot allow or deny lints.

```toml
avoid-breaking-exported-api = false
disallowed-names = ["toto", "tata", "titi"]
msrv = "1.30.0"
```

To change lint levels project-wide, pass compiler lint flags through extra CLI arguments, e.g. in `.mega-linter.yml`:

```yaml
RUST_CLIPPY_ARGUMENTS: "-- -A clippy::too_many_arguments -W clippy::pedantic"
```

Clippy has no ignore-file mechanism; exclude paths (e.g. generated code) with `RUST_CLIPPY_FILTER_REGEX_EXCLUDE` instead.

## When disabling is legitimate

- `pedantic` and `nursery` lints are allow-by-default precisely because they are strict or still experimental and prone to false positives — silence them case by case rather than fixing awkwardly.
- Generated code (e.g. `bindgen`, protobuf, macro output) that you do not own: use a crate- or module-level `#![allow(...)]` or path exclusion.
- A suggested rewrite would break a public API contract; prefer setting `avoid-breaking-exported-api` in the configuration file over scattering allows.
- An inline `#[allow]` on the smallest possible scope, ideally with a comment explaining why, is always preferable to disabling `RUST_CLIPPY` at MegaLinter level — that is the last resort.
