# Fix EDITORCONFIG_EDITORCONFIG_CHECKER errors

<!-- generated-descriptor-info-start -->
- Linter: **editorconfig-checker** (MegaLinter key: `EDITORCONFIG_EDITORCONFIG_CHECKER`)
- Descriptor: **EDITORCONFIG** (tooling_format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/editorconfig_editorconfig_checker/>
- Official documentation: <https://editorconfig-checker.github.io/>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.editorconfig-checker.json` (custom path can be defined with `EDITORCONFIG_EDITORCONFIG_CHECKER_CONFIG_FILE`)
- Rules configuration: <https://github.com/editorconfig-checker/editorconfig-checker#configuration>
- How to disable rules inline: <https://github.com/editorconfig-checker/editorconfig-checker#excluding>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `EDITORCONFIG_EDITORCONFIG_CHECKER` to fully disable this linter
  - `EDITORCONFIG_EDITORCONFIG_CHECKER_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `EDITORCONFIG_EDITORCONFIG_CHECKER_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `EDITORCONFIG_EDITORCONFIG_CHECKER_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `EDITORCONFIG_EDITORCONFIG_CHECKER_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

editorconfig-checker verifies that every file complies with the rules declared in the repository's `.editorconfig`: `end_of_line`, `insert_final_newline`, `trim_trailing_whitespace`, `indent_style`, `indent_size`, `max_line_length` and `charset`. It is check-only: it has no fix command, so correct the files manually (or with your editor's EditorConfig plugin, which applies these rules on save).

Fix by error category:

- **Wrong line endings** (`end_of_line`): convert the file to the declared ending (e.g. LF), typically with `dos2unix` or the editor's line-ending setting; check `.gitattributes` so Git does not reintroduce CRLF on checkout.
- **Missing final newline** (`insert_final_newline`): add a single newline at the end of the file.
- **Trailing whitespace** (`trim_trailing_whitespace`): remove spaces/tabs at end of lines; most editors can trim on save.
- **Wrong indentation** (`indent_style`, `indent_size`): re-indent with the declared style (tabs vs spaces) and width. If tabs followed by alignment spaces are intentional, set `"SpacesAfterTabs": true` in the configuration file instead of re-indenting.
- **Line too long** (`max_line_length`): wrap or shorten the offending lines.
- **Wrong charset** (`charset`): re-encode the file to the declared encoding (e.g. UTF-8).

If the `.editorconfig` rule itself is wrong for a file type, fix the `.editorconfig` (add a `[glob]` section overriding the property) rather than the files.

## Inline disable

Use comment markers in any comment style the file supports:

- `editorconfig-checker-disable-file` on the first line of the file: skip the whole file
- `editorconfig-checker-disable-line`: skip the line carrying the comment
- `editorconfig-checker-disable-next-line`: skip the following line
- `editorconfig-checker-disable` ... `editorconfig-checker-enable`: skip a block

Example:

```js
// editorconfig-checker-disable-next-line
const asciiArt = "this very long line intentionally exceeds max_line_length          ";

/* editorconfig-checker-disable */
const block = "everything here is ignored";
/* editorconfig-checker-enable */
```

## Ignore via configuration

In the configuration file, add regex patterns to `Exclude` or turn off a whole check in the `Disable` block:

```json
{
  "Exclude": ["\\.min\\.js$", "^vendor/"],
  "Disable": {
    "IndentSize": true
  }
}
```

Available `Disable` keys: `EndOfLine`, `Indentation`, `IndentSize`, `InsertFinalNewline`, `TrimTrailingWhitespace`, `MaxLineLength`, `Charset`. The same effects exist as CLI flags (`-exclude "pattern1|pattern2"`, `-disable-indentation`, `-disable-max-line-length`, ...) that can be passed through the linter arguments variable. There is no separate ignore file: exclusion lives in this configuration file (defaults such as `.git` and `node_modules` are already excluded unless `IgnoreDefaults` is changed).

Alternatively, scope rules out in `.editorconfig` itself, e.g. `indent_size = unset` under a `[*.md]` section.

## When disabling is legitimate

- Generated or vendored files (minified assets, lockfiles, third-party code) that must stay byte-identical to their source: exclude them via `Exclude`.
- Test fixtures that intentionally contain trailing whitespace, missing final newlines or exotic encodings because that is what they test: use `editorconfig-checker-disable-file`.
- Binary-like or format-constrained files (patches/diffs, snapshots) where trimming whitespace would corrupt content: exclude or disable `TrimTrailingWhitespace` for them in `.editorconfig`.
- A single unavoidable long line (URL, hash, ASCII art): prefer `editorconfig-checker-disable-next-line` over relaxing `max_line_length` globally.

Disabling the linter at MegaLinter level (`DISABLE_LINTERS` / `..._DISABLE_ERRORS`) is the last resort; prefer fixing files, adjusting `.editorconfig`, or targeted exclusions.
