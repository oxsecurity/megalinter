# Fix BASH_EXEC errors

<!-- generated-descriptor-info-start -->
- Linter: **bash-exec** (MegaLinter key: `BASH_EXEC`)
- Descriptor: **BASH** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/bash_bash_exec/>
- Official documentation: <https://www.gnu.org/software/bash/>
- Auto-fix support: no (errors must be fixed manually)
- Rules configuration: <https://www.gnu.org/software/bash/manual/bash.html>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `BASH_EXEC` to fully disable this linter
  - `BASH_EXEC_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `BASH_EXEC_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `BASH_EXEC_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `BASH_EXEC_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

bash-exec is a minimal MegaLinter-internal check: it verifies that shell script files
(`.sh`, `.bash`, `.dash`, `.ksh`, or files with a bash/sh shebang) carry the executable
permission bit. The only error it emits is `Error: File:[<file>] is not executable`.

To fix, make the reported script executable and commit the permission change:

- On Linux/macOS, run `chmod +x path/to/script.sh`, then stage and commit the file (git tracks the exec bit).
- On Windows, the filesystem has no exec bit: set it directly in the git index with `git add --chmod=+x path/to/script.sh`, then commit.
- If the file is not actually meant to be executed directly (e.g. a library sourced by other scripts), consider renaming it away from a script extension or excluding it (see below) instead of adding a misleading exec bit.

Notes on severity:

- By default the check is non-blocking: missing exec bits are reported as warnings.
- Setting `ERROR_ON_MISSING_EXEC_BIT: true` in `.mega-linter.yml` turns them into blocking errors.

## Inline disable

bash-exec has no inline suppression mechanism: it checks file permissions, not file
content, so no comment or directive inside the script can silence it. The closest
alternative is excluding the file from the linter via configuration (next section).

## Ignore via configuration

bash-exec has no configuration file of its own (it is a permission check, not a
configurable tool). Exclusions are done at MegaLinter level in `.mega-linter.yml`, e.g.:

```yaml
BASH_EXEC_FILTER_REGEX_EXCLUDE: "(lib/.*\\.sh|scripts/sourced-.*)"
```

You can also narrow which extensions are checked:

```yaml
BASH_EXEC_FILE_EXTENSIONS: [".sh"]
```

## When disabling is legitimate

Excluding files or keeping the check non-blocking is reasonable when:

- The scripts are libraries meant to be sourced (`source lib.sh`), never executed directly, so an exec bit would be misleading.
- The repository is developed mostly on Windows filesystems where the exec bit does not exist locally and contributors cannot easily verify it (use `git add --chmod=+x` case by case instead).
- The scripts are vendored or generated third-party files whose permissions you do not control.
- Deployment tooling (packaging, container COPY with explicit chmod) sets permissions itself, making the in-repo bit irrelevant.

Disabling the whole linter at MegaLinter level (`DISABLE_LINTERS`) remains the last
resort — prefer fixing the exec bit or excluding the specific files.
