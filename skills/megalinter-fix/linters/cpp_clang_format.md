# Fix CPP_CLANG_FORMAT errors

<!-- generated-descriptor-info-start -->
- Linter: **clang-format** (MegaLinter key: `CPP_CLANG_FORMAT`)
- Descriptor: **CPP** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/cpp_clang_format/>
- Official documentation: <https://releases.llvm.org/21.1.0/tools/clang/docs/ClangFormat.html>
- Auto-fix support: **yes** — add `CPP_CLANG_FORMAT` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter CPP_CLANG_FORMAT --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `.clang-format` (custom path can be defined with `CPP_CLANG_FORMAT_CONFIG_FILE`)
- Rules index: <https://releases.llvm.org/21.1.0/tools/clang/docs/ClangFormat.html>
- Rules configuration: <https://releases.llvm.org/21.1.0/tools/clang/docs/ClangFormatStyleOptions.html>
- How to disable rules inline: <https://releases.llvm.org/21.1.0/tools/clang/docs/ClangFormatStyleOptions.html#disabling-formatting-on-a-piece-of-code>
- Error line format (regex): `code should be clang-formatted`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `CPP_CLANG_FORMAT` to fully disable this linter
  - `CPP_CLANG_FORMAT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `CPP_CLANG_FORMAT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `CPP_CLANG_FORMAT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `CPP_CLANG_FORMAT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

clang-format is a pure formatter: it checks that C/C++ code layout (indentation, braces,
line breaking, spacing, include order) matches the project style, and it reports no other
kind of issue. Do not hand-edit whitespace to satisfy it — reformat instead:

- Preferred: run the MegaLinter auto-fix described in the block above; it rewrites the
  files with the exact expected layout.
- Locally: `clang-format -i <files>` formats files in place; add `--style=file` to use the
  repository configuration (this is the default lookup: `.clang-format` or `_clang-format`
  found in the file's parent directories).
- To only preview problems, use `clang-format --dry-run --Werror <files>`, which prints
  the would-be changes as errors without modifying anything.

If the reformatted result looks wrong, the style option causing it must be adjusted in the
configuration file (see rules configuration link above) rather than fought manually.

## Inline disable

Wrap the region between `// clang-format off` and `// clang-format on` comments
(`/* clang-format off */` block comments also work). An optional `: reason` suffix is
allowed. Everything between the two markers is left untouched:

```cpp
// clang-format off: alignment matters for this lookup table
static const int kTable[] = { 1,   2,   4,
                              8,  16,  32 };
// clang-format on
```

Always restore formatting with the matching `on` comment, otherwise the rest of the file
is skipped too.

## Ignore via configuration

The configuration file is YAML, typically starting from a base style and overriding
individual options:

```yaml
BasedOnStyle: LLVM
IndentWidth: 4
```

- Exempt a whole directory tree by placing in it a config file containing only
  `DisableFormat: true` — nested config files can re-enable formatting below.
- Exclude paths with a `.clang-format-ignore` file: one pattern per line, POSIX
  wildcards plus bash globstar `**`, `!` to negate, `#` for comments, e.g.:

```gitignore
third_party/**
!third_party/ours/**
```

- Per-language overrides use multiple YAML documents separated by `---`, each with a
  `Language:` key (e.g. `Language: Cpp`).

## When disabling is legitimate

- Hand-aligned constructs (lookup tables, matrices, ASCII-art comments, macro blocks)
  whose readability depends on a layout clang-format would destroy — use inline
  `clang-format off/on`.
- Vendored, third-party or generated sources that must stay byte-identical to upstream —
  exclude them via `.clang-format-ignore` or a `DisableFormat: true` config file.
- A style option that clearly mismatches the team's convention — change the option in the
  configuration file instead of sprinkling inline disables.
- Different clang-format versions can produce different output; align the local binary
  version with the one MegaLinter runs before suppressing anything.

Disabling the linter at MegaLinter level (`DISABLE_LINTERS`, `..._DISABLE_ERRORS`,
`..._FILTER_REGEX_EXCLUDE`) is the last resort, once inline and configuration options
are exhausted.
