# Fix C_CPPLINT errors

<!-- generated-descriptor-info-start -->
- Linter: **cpplint** (MegaLinter key: `C_CPPLINT`)
- Descriptor: **C** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/c_cpplint/>
- Official documentation: <https://github.com/cpplint/cpplint>
- Auto-fix support: no (errors must be fixed manually)
- Rules index: <https://google.github.io/styleguide/cppguide.html>
- Error line format (regex): `Total errors found: ([0-9]+)`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `C_CPPLINT` to fully disable this linter
  - `C_CPPLINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `C_CPPLINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `C_CPPLINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `C_CPPLINT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

cpplint checks C/C++ files for style issues according to the Google C++ Style Guide. Every message is tagged with a category (`build/`, `legal/`, `readability/`, `runtime/`, `whitespace/`); fix by category:

- `whitespace/*` (indent, line_length, operators...): reformat the flagged line manually — wrap long lines, fix indentation and spacing around operators and braces.
- `build/header_guard`: add or correct the `#ifndef`/`#define`/`#endif` include guard so its name matches the expected path-based guard.
- `build/include_order`, `build/include_alpha`: reorder `#include` directives into the order required by the style guide, alphabetized within each block.
- `build/include_what_you_use`: directly include the header that declares each symbol you use instead of relying on transitive includes.
- `readability/*` (braces, casting, fn_size...): apply the style-guide construct — e.g. replace C-style casts with C++ named casts, add required braces, split oversized functions.
- `runtime/*` (printf_format, references...): fix the flagged call or declaration, e.g. correct `printf`-style format strings.
- `legal/copyright`: add the expected copyright header at the top of the file.

Consult the message's category in the rules index above to understand the required style before editing. There is no fix command: every error is corrected by hand.

## Inline disable

Append a `// NOLINT(category[, category...])` comment to the offending line; `// NOLINT` or `// NOLINT(*)` suppresses all categories on that line. Use `// NOLINTNEXTLINE(category)` to suppress on the following line, and `// NOLINTBEGIN(category)` ... `// NOLINTEND` around a block (statements on the BEGIN/END lines are included).

```cpp
int* p = (int*)malloc(4);  // NOLINT(readability/casting)
// NOLINTNEXTLINE(whitespace/line_length)
some_very_long_call(argument_one, argument_two, argument_three, argument_four);
// NOLINTBEGIN(build/include_order)
#include "b.h"
#include "a.h"
// NOLINTEND
```

## Ignore via configuration

cpplint reads per-directory `CPPLINT.cfg` files (merged from the file's directory up through parent directories unless `set noparent` stops the traversal). Example:

```text
set noparent
filter=-build/include_order,+build/include_alpha
exclude_files=.*\.cc
linelength=80
root=subdir
```

- `filter=` applies `+`/`-` category prefixes left to right (e.g. `-whitespace,+whitespace/braces` keeps only the braces check among whitespace ones); the same syntax works on the command line via `--filter=`, which can be passed through `C_CPPLINT_ARGUMENTS`.
- `exclude_files=` is a regex matched against file names in that directory; whole files can also be skipped with the `--exclude` CLI flag.
- `linelength=` and `root=` tune the line-length limit and the header-guard root directory instead of suppressing their checks.

## When disabling is legitimate

- The project intentionally follows a different style than Google's (e.g. another line length or include order): adjust `linelength=` or add a `filter=` in `CPPLINT.cfg` rather than sprinkling NOLINT comments.
- Generated or vendored C/C++ sources that must not be hand-edited: exclude them with `exclude_files=` in the directory's `CPPLINT.cfg`.
- `build/header_guard` false positives when headers live under a non-standard root: set `root=` instead of disabling the check.
- C-style casts or `printf` usage required by a C API boundary: suppress the single line with `// NOLINT(category)`.

Disabling the linter at MegaLinter level (`DISABLE_LINTERS`, `C_CPPLINT_DISABLE_ERRORS`, `C_CPPLINT_FILTER_REGEX_EXCLUDE`) is the last resort — prefer fixing the code or narrowing suppression in cpplint's own configuration.
