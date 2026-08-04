# Fix CPP_CPPLINT errors

<!-- generated-descriptor-info-start -->
- Linter: **cpplint** (MegaLinter key: `CPP_CPPLINT`)
- Descriptor: **CPP** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/cpp_cpplint/>
- Official documentation: <https://github.com/cpplint/cpplint>
- Auto-fix support: no (errors must be fixed manually)
- Rules index: <https://google.github.io/styleguide/cppguide.html>
- Error line format (regex): `Total errors found: ([0-9]+)`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `CPP_CPPLINT` to fully disable this linter
  - `CPP_CPPLINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `CPP_CPPLINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `CPP_CPPLINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `CPP_CPPLINT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

cpplint is a static style checker that validates C/C++ files against the Google C++ Style Guide. It reports style violations, not functional bugs, and has no auto-fix command: every error must be corrected manually in the source.

Each message ends with its category (e.g. `[whitespace/braces] [4]`). Fix by category:

- `whitespace/*` (blank_line, braces, comma, indent, line_length, tab, end_of_line...): adjust spacing, indentation, brace placement and line length exactly as the message states; wrap lines longer than the limit (default 80).
- `build/*` (header_guard, include, include_order, namespaces, storage_class...): fix header guard names to match the expected path-based macro, reorder `#include` directives (related header, C system, C++ system, other libs, project headers), avoid `using namespace` in headers.
- `readability/*` (braces, casting, todo, constructors...): replace C-style casts with `static_cast`/`reinterpret_cast`, format `TODO(user)` comments, mark single-argument constructors `explicit` when flagged under `runtime/explicit`.
- `runtime/*` (int, references, printf, string, arrays...): use fixed-width or `int` instead of `short`/`long`, make non-const reference parameters const or pointers, prefer `snprintf` over `sprintf`, avoid static/global objects of class type.
- `legal/copyright`: add a copyright notice at the top of the file.

Look up the rationale for any rule in the Google C++ Style Guide (rules index above) before changing code.

## Inline disable

Append a `NOLINT(category)` comment to the offending line; `// NOLINT` or `// NOLINT(*)` suppresses all categories on that line. Use `// NOLINTNEXTLINE(category)` to suppress on the following line, and `// NOLINTBEGIN(category)` / `// NOLINTEND` around a block:

```cpp
using namespace std;  // NOLINT(build/namespaces)
// NOLINTNEXTLINE(whitespace/line_length)
int a_very_long_declaration_that_exceeds_the_configured_line_length_limit = 42;
// NOLINTBEGIN(runtime/int)
short legacy_value;
// NOLINTEND
```

Always name the category instead of using a bare `NOLINT` so other checks stay active.

## Ignore via configuration

Place a `CPPLINT.cfg` file in the project root (or any directory: it applies to that directory and all subdirectories, and parent directories are also searched unless `set noparent` is present):

```text
set noparent
filter=-whitespace/line_length,-build/include_order
exclude_files=third_party/.*
linelength=120
root=include
```

- `filter=` uses the same `-category,+category` syntax as the `--filter` CLI flag (e.g. `--filter=-whitespace,+whitespace/braces`); categories can also be passed through the MegaLinter arguments variable.
- `exclude_files=` is a regex matched against file names in that directory to skip them.
- There is no separate ignore file; `exclude_files` in `CPPLINT.cfg` (or the `--exclude` CLI flag) is the exclusion mechanism.

## When disabling is legitimate

- The codebase deliberately follows another style guide (LLVM, Qt, kernel style): disable the conflicting `whitespace/*` or `build/*` categories in `CPPLINT.cfg` rather than fighting each finding.
- Generated or vendored code (protobuf output, `third_party/`): exclude it with `exclude_files=` instead of editing it.
- Known false positives, e.g. `runtime/references` on APIs that intentionally use non-const references, or `build/include_order` when an include order is imposed by a dependency: suppress with a targeted `NOLINT(category)`.
- `legal/copyright` on projects that do not use per-file copyright headers: disable that single category globally.

Prefer a scoped `NOLINT(category)` or a `CPPLINT.cfg` filter over MegaLinter-level exclusion; disabling the linter in `.mega-linter.yml` is the last resort.
