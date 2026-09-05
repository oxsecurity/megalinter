# Fix CLOJURE_CLJSTYLE errors

<!-- generated-descriptor-info-start -->
- Linter: **cljstyle** (MegaLinter key: `CLOJURE_CLJSTYLE`)
- Descriptor: **CLOJURE** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/clojure_cljstyle/>
- Official documentation: <https://github.com/greglook/cljstyle>
- Auto-fix support: **yes** — add `CLOJURE_CLJSTYLE` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter CLOJURE_CLJSTYLE --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `.cljstyle` (custom path can be defined with `CLOJURE_CLJSTYLE_CONFIG_FILE`)
- Rules index: <https://github.com/greglook/cljstyle/blob/main/doc/configuration.md#format-rules>
- Rules configuration: <https://github.com/greglook/cljstyle/blob/main/doc/configuration.md#format-rules>
- How to disable rules inline: <https://github.com/greglook/cljstyle#ignoring-forms>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `CLOJURE_CLJSTYLE` to fully disable this linter
  - `CLOJURE_CLJSTYLE_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `CLOJURE_CLJSTYLE_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `CLOJURE_CLJSTYLE_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `CLOJURE_CLJSTYLE_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

cljstyle is a pure formatter for Clojure source: it rewrites whitespace, indentation, blank lines, comment style, namespace forms and var/function definitions to a canonical style. It reports no logic issues, so the fix is always to reformat, never to change behavior.

- Prefer the auto-fix: enable MegaLinter auto-fix (see generated block above) or run `cljstyle fix` at the repository root to rewrite all offending files in place.
- To preview what would change, run `cljstyle check`: it prints a diff of every violation without modifying files. Apply the shown diff manually only if you cannot run `fix`.
- To format a snippet or integrate with an editor, pipe code through `cljstyle pipe` (reads stdin, writes formatted code to stdout).
- Typical error categories map to rule keys: `:indentation` (list/body indent), `:whitespace` (spaces between/around forms), `:blank-lines` (max consecutive blank lines between top-level forms), `:eof-newline` (trailing newline), `:comments`, `:vars`, `:functions`, `:types`, and `:namespaces` (canonical `ns` form ordering). All are corrected by `cljstyle fix`.
- If a macro's body is re-indented wrongly, do not fight the formatter by hand: add a custom indent rule under `:rules {:indentation {:indents ...}}` in the configuration file instead.

## Inline disable

Attach the `^:cljstyle/ignore` metadata tag directly before a form to exclude it (and its contents) from all formatting rules:

```clojure
^:cljstyle/ignore
(def styled-table
  [:a   1
   :bb  22])
```

Forms inside `(comment ...)` blocks and forms discarded with `#_` are also left untouched.

## Ignore via configuration

The configuration file is EDN. Disable a whole rule by setting its `:enabled?` option to false, or tune rule options; exclude files and directories with the `:ignore` set under `:files` (strings match file/directory names exactly, regex patterns match the whole relative path):

```clojure
{:rules {:blank-lines {:enabled? false}
         :indentation {:list-indent 1}}
 :files {:ignore #{"target" "checkouts" #"generated/.*"}}}
```

Rule maps merge with defaults; add the `^:replace` metadata hint (e.g. on an `:indents` map) to override instead of merge. There is no separate ignore file such as `.cljstyleignore`.

## When disabling is legitimate

- Data literals laid out as aligned tables or matrices, where hand alignment is more readable than canonical indentation — use `^:cljstyle/ignore` on that form only.
- Generated or vendored Clojure sources (e.g. `target`, `checkouts`, protocol-generated code) — exclude them via `:files {:ignore ...}`.
- Custom macros whose bodies cljstyle indents like plain function calls — prefer adding an `:indents` rule for the macro over disabling `:indentation` globally.
- A team that intentionally follows a different style guide should encode it in the configuration file rather than suppressing findings case by case.

Disabling the linter at MegaLinter level (`DISABLE_LINTERS`, `..._DISABLE_ERRORS`, `..._FILTER_REGEX_EXCLUDE`) is the last resort, once inline and configuration options are exhausted.
