# Fix BASH_SHFMT errors

<!-- generated-descriptor-info-start -->
- Linter: **shfmt** (MegaLinter key: `BASH_SHFMT`)
- Descriptor: **BASH** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/bash_shfmt/>
- Official documentation: <https://github.com/mvdan/sh>
- Auto-fix support: **yes** — add `BASH_SHFMT` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter BASH_SHFMT --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Rules configuration: <https://github.com/mvdan/sh/blob/master/cmd/shfmt/shfmt.1.scd>
- How to disable rules inline: <https://github.com/mvdan/sh/blob/master/cmd/shfmt/shfmt.1.scd>
- Error line format (regex): `---.*\n.*\+\+\+.*`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `BASH_SHFMT` to fully disable this linter
  - `BASH_SHFMT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `BASH_SHFMT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `BASH_SHFMT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `BASH_SHFMT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

shfmt is a shell script formatter, not a rule-based linter: any error is a formatting
diff between the file and shfmt's canonical style (indentation, spacing, line breaks).
The fix is always to reformat, never to hand-edit whitespace:

- Prefer the MegaLinter auto-fix (see the auto-fix line in the block above), which rewrites files in place.
- Or run shfmt locally: `shfmt -w file.sh` (`-w`/`--write` writes the result to the file), `shfmt -l .` lists non-compliant files, `shfmt -d file.sh` shows the diff.
- Match the project's style flags when running manually: `-i` (spaces per indent, `0` = tabs), `-ci` (indent switch cases), `-bn` (binary ops like `&&` may start a line), `-sr` (space after redirect operators), `-fn` (function brace on next line), `-ln` (dialect: `bash`, `posix`, `mksh`, `bats`). Reuse the flags found in `BASH_SHFMT_ARGUMENTS` if any.
- `shfmt -s` additionally simplifies code (and `-mn` minifies); only use them if the project already does.
- If shfmt reports a parse error instead of a diff, fix the shell syntax error first — shfmt cannot format an unparseable script.

## Inline disable

shfmt has no inline suppression: the project states "The formatter cannot be
disabled for ranges of lines". There is no `# shfmt: disable` comment. The only
alternatives are excluding the file via `.editorconfig` `ignore = true` (below)
or via the MegaLinter exclude-regex variable from the block above.

## Ignore via configuration

shfmt reads formatting options from `.editorconfig` when no parser or printer
flags are passed on the command line (any such flag disables EditorConfig usage,
so keep `BASH_SHFMT_ARGUMENTS` empty if you rely on `.editorconfig`):

```ini
[*.sh]
indent_style = space
indent_size = 2
shell_variant = bash
switch_case_indent = true
binary_next_line = true
space_redirects = true

[third_party/**]
ignore = true
```

Other supported properties: `simplify`, `keep_padding`, `function_next_line`.
`ignore = true` sections skip matching files when formatting directories; for
files passed directly, add the `--apply-ignore` flag.

## When disabling is legitimate

- Vendored or third-party scripts kept byte-identical to upstream: exclude them with an `ignore = true` EditorConfig section rather than reformatting.
- Generated shell scripts (e.g. embedded installers, configure scripts) that a tool rewrites on each build.
- Scripts in a dialect shfmt cannot parse correctly for your use case (set `shell_variant` / `-ln` first; exclude only if that fails).
- Deliberate alignment/padding that formatting would destroy: try `keep_padding` before excluding the file.

Excluding files this way is preferable to weakening the check globally: disabling
`BASH_SHFMT` at MegaLinter level is the last resort.
