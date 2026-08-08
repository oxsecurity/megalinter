# Fix C_CLANG_FORMAT errors

<!-- generated-descriptor-info-start -->
- Linter: **clang-format** (MegaLinter key: `C_CLANG_FORMAT`)
- Descriptor: **C** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/c_clang_format/>
- Official documentation: <https://releases.llvm.org/21.1.0/tools/clang/docs/ClangFormat.html>
- Auto-fix support: **yes** — add `C_CLANG_FORMAT` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter C_CLANG_FORMAT --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `.clang-format` (custom path can be defined with `C_CLANG_FORMAT_CONFIG_FILE`)
- Rules index: <https://releases.llvm.org/21.1.0/tools/clang/docs/ClangFormat.html>
- Rules configuration: <https://releases.llvm.org/21.1.0/tools/clang/docs/ClangFormatStyleOptions.html>
- How to disable rules inline: <https://releases.llvm.org/21.1.0/tools/clang/docs/ClangFormatStyleOptions.html#disabling-formatting-on-a-piece-of-code>
- Error line format (regex): `code should be clang-formatted`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `C_CLANG_FORMAT` to fully disable this linter
  - `C_CLANG_FORMAT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `C_CLANG_FORMAT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `C_CLANG_FORMAT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `C_CLANG_FORMAT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

clang-format is a pure formatter: it checks whitespace, indentation, line breaking, brace placement and alignment of C/C++ (and other C-family) code against a style definition. It reports no rule-level findings — a file either matches the expected formatting or it does not.

- Do not fix formatting by hand: run the formatter. The canonical fix is MegaLinter auto-fix (see the generated block above), or locally `clang-format -i <file>` to rewrite files in place.
- To preview issues without modifying files, run `clang-format --dry-run <file>` (alias `-n`); add `--Werror` to turn formatting warnings into errors, which is how CI-style checks fail.
- The applied style comes from `-style`: `file` (default) walks parent directories for the configuration file, `file:<path>` points to an explicit one, and presets such as `LLVM`, `Google`, `Chromium`, `Mozilla`, `WebKit`, `Microsoft`, `GNU` can be used directly or inline: `--style="{BasedOnStyle: llvm, IndentWidth: 8}"`.
- If the whole file is reformatted unexpectedly, first verify which style is being picked up before touching code: a missing or mislocated configuration file makes clang-format fall back to a different style than the project expects.

## Inline disable

Wrap the code to preserve between `// clang-format off` and `// clang-format on` comments (block-comment form `/* clang-format off */` also works). An optional explanation may follow after a colon.

```c
int formatted_code;
// clang-format off: manually aligned lookup table
    void    unformatted_code  ;
// clang-format on
void formatted_code_again;
```

## Ignore via configuration

The configuration file is YAML `key: value` pairs, usually starting from a preset:

```yaml
BasedOnStyle: LLVM
IndentWidth: 4
ColumnLimit: 80
```

- To exclude files, create a `.clang-format-ignore` file: one POSIX glob pattern per line (bash globstar `**` supported), `#` for comments, leading `!` to negate; patterns are relative to the ignore file's directory.
- To disable formatting entirely for files matched by a configuration, set `DisableFormat: true` — e.g. drop a minimal config with that option in a subdirectory of untouched code, or use a `Language:` section to disable one language only:

```yaml
---
Language: Proto
DisableFormat: true
```

## When disabling is legitimate

- Manually aligned constructs (lookup tables, matrices, ASCII-art comments) that clang-format would flatten: keep them readable with `// clang-format off` blocks.
- Generated or vendored/third-party sources that must stay byte-identical to their upstream: exclude them via `.clang-format-ignore` or the exclude regex.
- Sections formatted for a specific external convention (e.g. code copied from a spec or another project's style) where reformatting would obscure diffs against the origin.

Disabling the linter at MegaLinter level (`DISABLE_LINTERS` / disable-errors variables) is the last resort — prefer running the auto-fix or scoping exclusions as narrowly as possible.
