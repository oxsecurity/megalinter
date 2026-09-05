# Fix CPP_CPPCHECK errors

<!-- generated-descriptor-info-start -->
- Linter: **cppcheck** (MegaLinter key: `CPP_CPPCHECK`)
- Descriptor: **CPP** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/cpp_cppcheck/>
- Official documentation: <https://cppcheck.sourceforge.io/>
- Auto-fix support: no (errors must be fixed manually)
- Rules index: <https://sourceforge.net/p/cppcheck/wiki/ListOfChecks/>
- Rules configuration: <https://cppcheck.sourceforge.io/manual.html#configuration>
- Error line format (regex): `error:`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `CPP_CPPCHECK` to fully disable this linter
  - `CPP_CPPCHECK_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `CPP_CPPCHECK_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `CPP_CPPCHECK_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `CPP_CPPCHECK_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

cppcheck is a static analyzer for C/C++ focused on detecting undefined behavior and dangerous constructs
(severities: `error`, `warning`, `style`, `performance`, `portability`, `information`). There is no auto-fix:
correct the code manually per category.

- **Memory/resource leaks** (`memleak`, resource leak): free/close every allocation on all paths; prefer RAII
  (smart pointers, containers) over raw `new`/`malloc`.
- **Null pointer dereference** (`nullPointer`): add a null check before dereferencing, or fix the logic that
  allows a null value to reach that point.
- **Out-of-bounds access** (`arrayIndexOutOfBounds`, buffer overflow): fix the index/size computation and
  bound loops to the real container/array size.
- **Uninitialized variables** (`uninitvar`): initialize variables at declaration and ensure all branches assign
  before use.
- **Dangling pointers/references**: never return a pointer or reference to a local (auto) variable; return by
  value or allocate with proper ownership.
- **Logic errors**: remove unreachable code, fix always-true/false conditions, guard against division by zero.
- **STL misuse**: do not use invalidated iterators or a `c_str()` result outliving its `std::string`.
- **Class checks**: add missing constructors and virtual destructors; never call pure virtual functions from
  constructors.

## Inline disable

Use a `cppcheck-suppress` comment on the line before (or at the end of) the offending line. Inline
suppressions only work when cppcheck runs with `--inline-suppr`, so add that flag through the linter's
extra-arguments tuning variable listed above.

```c
// cppcheck-suppress arrayIndexOutOfBounds
arr[10] = 0;

// cppcheck-suppress [arrayIndexOutOfBounds, zerodiv]
arr[10] = arr[10] / 0;
```

Suppress a whole region with `// cppcheck-suppress-begin <id>` ... `// cppcheck-suppress-end <id>`.

## Ignore via configuration

cppcheck has no default config file in MegaLinter; pass options through the extra-arguments tuning variable:

- `--suppress=<id>[:<file>]` — suppress one check id, optionally only in a given file, e.g.
  `--suppress=memleak:src/file1.cpp`
- `--suppressions-list=suppressions.txt` — file with one suppression per line:

```text
memleak:src/file1.cpp
uninitvar
```

- `-i <dir>` — skip analysis of a whole folder, e.g. `-itest`
- A `--project=` file (`.cppcheck` GUI project, `compile_commands.json`, `.sln`) can also carry excludes.

## When disabling is legitimate

- False positive because cppcheck lacks build context (missing includes, unknown library semantics); prefer a
  narrow `--suppress=<id>:<file>` over global suppression.
- Generated or vendored third-party sources: exclude the folder with `-i` or the MegaLinter filter regex.
- Intentional low-level constructs (placement tricks, hardware registers) that cppcheck flags as undefined
  behavior: suppress inline with a comment explaining why.
- Disabling `CPP_CPPCHECK` entirely at MegaLinter level is the last resort — suppress the specific check id
  first.
