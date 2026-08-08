# Fix C_CPPCHECK errors

<!-- generated-descriptor-info-start -->
- Linter: **cppcheck** (MegaLinter key: `C_CPPCHECK`)
- Descriptor: **C** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/c_cppcheck/>
- Official documentation: <https://cppcheck.sourceforge.io/>
- Auto-fix support: no (errors must be fixed manually)
- Rules index: <https://sourceforge.net/p/cppcheck/wiki/ListOfChecks/>
- Rules configuration: <https://cppcheck.sourceforge.io/manual.html#configuration>
- Error line format (regex): `error:`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `C_CPPCHECK` to fully disable this linter
  - `C_CPPCHECK_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `C_CPPCHECK_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `C_CPPCHECK_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `C_CPPCHECK_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

cppcheck is a static analyzer for C/C++ focused on detecting undefined behavior and dangerous constructs rather than style. It has no auto-fix: every finding must be corrected manually in the code.

Fix strategy by severity (shown in each message):

- `error` (undefined behavior is certain): fix the code itself — typical findings are null pointer dereference, buffer overrun / out-of-bounds index, memory or resource leak, use of uninitialized variable, division by zero. Add the missing null check, bound the index, free/close the resource on every path, initialize before use.
- `warning` (undefined behavior is possible): same treatment as `error`; make the risky path impossible instead of assuming it never happens.
- `style` (redundant or dead code, unused functions/variables, always-true conditions): delete the dead code or simplify the condition.
- `performance` and `portability`: apply the suggested construct (e.g. avoid implementation-defined behavior, prefer cheaper STL usage) unless the platform assumption is deliberate.

Run `cppcheck --doc` or `cppcheck --errorlist` to get the description of a specific check id before changing code.

## Inline disable

Inline suppressions only work when cppcheck runs with `--inline-suppr` (add it to the linter arguments if MegaLinter does not already pass it). Use the error id shown in brackets in the message:

```c
// cppcheck-suppress arrayIndexOutOfBounds
arr[10] = 0;

// cppcheck-suppress[arrayIndexOutOfBounds,zerodiv]
arr[10] = arr[10] / 0;
```

Ranges and whole files can be covered with `// cppcheck-suppress-begin <id>` ... `// cppcheck-suppress-end <id>`, or `// cppcheck-suppress-file <id>` at the top of the file.

## Ignore via configuration

cppcheck has no project config file by default; suppressions are passed on the command line (via the MegaLinter arguments variable listed above):

- single rule, optionally scoped to a file: `--suppress=memleak:src/file1.cpp`
- suppressions file: `--suppressions-list=suppressions.txt`, one entry per line in the form `[error id]:[filename]:[line]`, `[error id]:[filename]` or `[error id]`; `*`, `?` and `**` wildcards are allowed in both id and filename:

```text
memleak:src/file1.cpp
uninitvar
unusedFunction:src/legacy/**
```

- exclude whole paths from analysis: `-i build/` (skips the given directory or file).

## When disabling is legitimate

- False positive on a code path cppcheck cannot follow (complex ownership transfer, custom allocator, inline assembly): suppress the specific id inline with a short comment explaining why.
- Generated or vendored third-party sources: exclude the directory with `-i` or a filename-scoped suppression rather than per-line comments.
- `unusedFunction` on entry points only referenced externally (plugin hooks, linker sections, callbacks registered by macro).
- Deliberate platform-specific code flagged by `portability` checks when the project only targets that platform.

Disabling the whole linter or a rule at MegaLinter level is the last resort — prefer fixing the code, then the narrowest suppression.
