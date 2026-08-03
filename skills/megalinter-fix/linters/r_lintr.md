# Fix R_LINTR errors

<!-- generated-descriptor-info-start -->
- Linter: **lintr** (MegaLinter key: `R_LINTR`)
- Descriptor: **R** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/r_lintr/>
- Official documentation: <https://lintr.r-lib.org/>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.lintr` (custom path can be defined with `R_LINTR_CONFIG_FILE`)
- Rules index: <https://lintr.r-lib.org/reference/index.html>
- Rules configuration: <https://lintr.r-lib.org/articles/lintr.html#configuring-linters>
- How to disable rules inline: <https://lintr.r-lib.org/articles/lintr.html#exclusions>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `R_LINTR` to fully disable this linter
  - `R_LINTR_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `R_LINTR_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `R_LINTR_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `R_LINTR_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

lintr provides static code analysis for R: it checks adherence to a given style and identifies syntax errors and possible semantic issues. It has no auto-fix; fix each finding manually, guided by the linter name in the message.

- Style findings (`assignment_linter`, `line_length_linter`, `object_name_linter`, `indentation_linter`, `trailing_whitespace_linter`, `commas_linter`, `infix_spaces_linter`): rewrite the code to match the expected style — use `<-` for assignment, keep lines under the configured length, use the expected naming convention, fix indentation and spacing.
- Whole-file style cleanup: lintr is complementary to the `styler` package, which automatically restyles R code and eliminates many of the problems lintr detects — run `styler::style_file("path/to/file.R")` locally, then re-lint.
- Correctness / common-mistake findings: read the rule page under the rules index of the generated block above and change the logic accordingly; do not suppress these.

## Inline disable

Append a `# nolint` comment to the offending line, optionally naming the linter(s) after a colon and ending with a period:

```r
X = 42L # nolint: object_name_linter, assignment_linter.
```

For a block of lines, wrap it with `# nolint start` / `# nolint end`:

```r
# nolint start: commented_code_linter.
# x <- 42L
# print(x)
# nolint end
```

## Ignore via configuration

The configuration file uses Debian Control Field format. Disable a rule globally by setting it to `NULL` in `linters`, or tune its parameters; exclude files, directories, or specific lines with `exclusions`:

```r
linters: linters_with_defaults(
    line_length_linter(120),
    commented_code_linter = NULL
  )
exclusions: list(
    "renv",
    "R/generated.R",
    "R/legacy.R" = list(line_length_linter = 4:6)
  )
```

There is no separate ignore file: `exclusions` in the configuration file is the file-level ignore mechanism.

## When disabling is legitimate

- Generated or vendored R code (e.g. `renv/`, Rcpp-generated files, roxygen output) that should not follow the project style — exclude the paths via `exclusions`.
- Intentional style divergence from the tidyverse defaults (e.g. a longer line length, a different naming convention) — reconfigure the linter's parameters instead of suppressing findings.
- `commented_code_linter` or `object_name_linter` false positives on prose-like comments or names imposed by an external API — suppress with a targeted `# nolint: <linter>.` comment.
- Prefer targeted inline `# nolint` and configuration exclusions; disabling the whole linter at MegaLinter level is the last resort.
