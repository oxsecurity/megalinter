# Fix REPOSITORY_GIT_DIFF errors

<!-- generated-descriptor-info-start -->
- Linter: **git_diff** (MegaLinter key: `REPOSITORY_GIT_DIFF`)
- Descriptor: **REPOSITORY** (other)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/repository_git_diff/>
- Official documentation: <https://git-scm.com>
- Auto-fix support: no (errors must be fixed manually)
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `REPOSITORY_GIT_DIFF` to fully disable this linter
  - `REPOSITORY_GIT_DIFF_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `REPOSITORY_GIT_DIFF_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `REPOSITORY_GIT_DIFF_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `REPOSITORY_GIT_DIFF_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

This linter runs `git diff --check`, which warns when changes introduce leftover Git
conflict markers or whitespace errors. By default, whitespace errors are trailing
whitespace (including lines made only of whitespace) and a space immediately followed
by a tab inside the initial indent of a line; the exact set is controlled by the
`core.whitespace` git configuration. There is no auto-fix command: apply fixes manually.

- Conflict markers: open each reported file, finish the merge resolution by keeping the
  intended content, then delete the `<<<<<<<`, `=======` and `>>>>>>>` lines entirely.
- Trailing whitespace / blank-only lines: strip the whitespace at end of the reported
  lines (most editors offer "trim trailing whitespace on save").
- Space-before-tab in indentation: re-indent the line consistently (tabs only or spaces
  only, matching the file's existing style).
- Re-run `git diff --check` locally until it exits with status 0.

## Inline disable

`git diff --check` has no inline comment suppression mechanism. The closest alternative
is a per-path exclusion via a `.gitattributes` entry that unsets the `whitespace`
attribute (see next section):

```gitattributes
# Do not report any whitespace error on generated files
*.generated -whitespace
```

Note that `-whitespace` only silences whitespace errors, not conflict-marker warnings.

## Ignore via configuration

git_diff has no dedicated configuration file; it obeys standard git configuration.

Tune which whitespace problems are reported with `core.whitespace` (prefix a value with
`-` to disable it):

```bash
git config core.whitespace "-blank-at-eol,-space-before-tab"
```

Recognized values include `blank-at-eol` (alias `trailing-space`), `space-before-tab`,
`indent-with-non-tab`, `tab-in-indent`, `blank-at-eof` and `cr-at-eol`.

For per-path control, use the `whitespace` attribute in `.gitattributes`:

```gitattributes
*.py whitespace=blank-at-eol,blank-at-eof,space-before-tab
vendor/** -whitespace
```

Caution: this linter runs in project mode, so the `FILTER_REGEX_EXCLUDE` variable of the
generated block above does not apply — use the git mechanisms shown here instead.

## When disabling is legitimate

- Files that intentionally contain conflict-marker-like sequences, such as documentation
  or test fixtures demonstrating merge conflicts.
- Generated or vendored files with trailing whitespace you do not control: unset the
  `whitespace` attribute for those paths in `.gitattributes`.
- Formats where trailing whitespace is meaningful (e.g. Markdown hard line breaks):
  relax `core.whitespace` or the per-path attribute rather than the whole linter.
- Disabling at MegaLinter level (`DISABLE_LINTERS` or `..._DISABLE_ERRORS`) is the last
  resort, after git-level configuration has been considered.
