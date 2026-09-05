# Fix BASH_SHELLCHECK errors

<!-- generated-descriptor-info-start -->
- Linter: **shellcheck** (MegaLinter key: `BASH_SHELLCHECK`)
- Descriptor: **BASH** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/bash_shellcheck/>
- Official documentation: <https://github.com/koalaman/shellcheck>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.shellcheckrc` (custom path can be defined with `BASH_SHELLCHECK_CONFIG_FILE`)
- Rules index: <https://github.com/koalaman/shellcheck#gallery-of-bad-code>
- How to disable rules inline: <https://github.com/koalaman/shellcheck/wiki/Ignore>
- Error line format (regex): `In .* line .*:.*\n`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `BASH_SHELLCHECK` to fully disable this linter
  - `BASH_SHELLCHECK_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `BASH_SHELLCHECK_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `BASH_SHELLCHECK_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `BASH_SHELLCHECK_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

shellcheck performs static analysis of shell scripts to find syntax issues, quoting bugs, and
fragile constructs. Each finding has an `SCxxxx` code documented at `https://www.shellcheck.net/wiki/SCxxxx`.
MegaLinter applies no auto-fix for this linter; fix findings manually (`shellcheck -f diff` can emit
auto-fixes as a unified diff for some rules, pipeable to `git apply` or `patch -p1`).

Fix strategy for the most common codes:

- **SC2086** (unquoted variable): double-quote every expansion to prevent globbing and word
  splitting — write `echo "$1"` instead of `echo $1`, and iterate with `for i in "$@"` instead of `$*` or `$@`.
- **SC2046** (unquoted command substitution): quote it — `"$(getfilename)"`. When the command emits
  multiple items, read them into an array first: `readarray -t files < <(find . -type f)` then expand
  with `"${files[@]}"`.
- **SC2164** (`cd` may fail): append a failure handler so the script does not continue in the wrong
  directory — `cd somedir || exit` (use `|| return` inside functions).
- **SC1090/SC1091** (sourced file not followed): add `# shellcheck source=path/to/file` above the
  `source` line when the path is known, run with `-x` or set `external-sources=true` in `.shellcheckrc`
  to let shellcheck open sourced files, or use `# shellcheck source=/dev/null` when the file is not
  available at lint time. SC1090 covers dynamic paths (`source "$dir/file"`) shellcheck cannot resolve.
- **SC2034** (unused variable): reference the variable where intended (check for case typos like
  `$FOO` vs `$foo`), `export` it if consumed by child processes, name throwaway variables `_`
  (or prefix with `_`), or disable the code for deliberate cases.

## Inline disable

Place a directive comment on the line above the finding:

```bash
# shellcheck disable=SC2086
hash=$(echo ${hash})
```

Disable several codes at once with a comma-separated list (`disable=SC2116,SC2086`). A directive
placed right after the shebang applies to the whole file:

```bash
#!/bin/sh
# shellcheck disable=SC2059
```

Use `# shellcheck source=somefile` above a `source` line to tell shellcheck which file to follow.
Note a directive only applies to the first command of a `cmd1; cmd2` sequence.

## Ignore via configuration

Add file-wide directives as `key=value` lines in `.shellcheckrc` at the repository root
(shellcheck searches the script's directory and its parents):

```ini
disable=SC1091,SC2034
external-sources=true
source-path=SCRIPTDIR
```

`disable` also accepts ranges (`disable=SC1090-SC1100`), `external-sources=true` allows opening any
sourced file, and `source-path` adds directories to the search path for `source`/`.` statements.

## When disabling is legitimate

- The sourced file only exists at runtime (CI-provided env file, generated script): use
  `source=/dev/null` or disable SC1091 rather than faking the file.
- The variable is intentionally unused but part of a documented interface (consumed by a sourcing
  script or external tool): disable SC2034 on that line.
- Unquoted expansion is deliberate because word splitting is the intent (building an argument list
  from a controlled variable): disable SC2086 inline with a comment explaining why.
- Disabling the whole linter or a code globally via MegaLinter variables (`DISABLE_LINTERS`,
  `BASH_SHELLCHECK_DISABLE_ERRORS`, `BASH_SHELLCHECK_FILTER_REGEX_EXCLUDE`) is a last resort —
  prefer targeted inline directives or `.shellcheckrc` entries.
