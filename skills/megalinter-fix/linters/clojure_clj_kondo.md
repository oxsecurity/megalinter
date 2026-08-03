# Fix CLOJURE_CLJ_KONDO errors

<!-- generated-descriptor-info-start -->
- Linter: **clj-kondo** (MegaLinter key: `CLOJURE_CLJ_KONDO`)
- Descriptor: **CLOJURE** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/clojure_clj_kondo/>
- Official documentation: <https://github.com/borkdude/clj-kondo>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.clj-kondo/config.edn` (custom path can be defined with `CLOJURE_CLJ_KONDO_CONFIG_FILE`)
- Rules index: <https://github.com/borkdude/clj-kondo#features>
- Rules configuration: <https://github.com/borkdude/clj-kondo/blob/master/doc/config.md#configuration>
- How to disable rules inline: <https://github.com/clj-kondo/clj-kondo/blob/master/doc/config.md#ignore-warnings-in-an-expression>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `CLOJURE_CLJ_KONDO` to fully disable this linter
  - `CLOJURE_CLJ_KONDO_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `CLOJURE_CLJ_KONDO_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `CLOJURE_CLJ_KONDO_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `CLOJURE_CLJ_KONDO_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `CLOJURE_CLJ_KONDO_ERROR_CONFIG_INVALID`
<!-- generated-descriptor-info-end -->

## Fix instructions

clj-kondo statically analyzes Clojure, ClojureScript and EDN files for real bugs and dead code: arity errors, unresolved symbols/vars/namespaces, unused code, duplicate map keys or requires, and style issues. It has no auto-fix: correct the code manually, then re-check with `clj-kondo --lint <file>`.

Fix the most common categories as follows:

- `invalid-arity` / arity mismatch: call the function with the number of arguments its signature accepts, or fix the signature.
- `unresolved-symbol`, `unresolved-var`, `unresolved-namespace`: add the missing `:require` / `:import` to the `ns` form, fix the typo, or define the var before use.
- `unused-binding`, unused private var, unused namespace/referred var/import: delete the dead code, or rename an intentionally unused binding to `_`.
- Duplicate map keys, set elements or requires: remove the duplicate entry.
- `redundant-do`, `inline-def`, missing `:else` in `cond`: unwrap the superfluous `do`, replace nested `def` with `let`, add an `:else` branch.
- Warnings coming from macros clj-kondo does not understand: teach it the macro via `:lint-as` or hooks in the configuration instead of suppressing each call site.

## Inline disable

Prefix the offending expression with the `#_:clj-kondo/ignore` reader-discard marker; ignore only specific linters by passing a vector:

```clojure
#_{:clj-kondo/ignore [:invalid-arity]}
(inc 1 2 3)
```

Use plain `#_:clj-kondo/ignore` (no map) to suppress all warnings for the next expression only, and keep the linter list as narrow as possible.

## Ignore via configuration

Turn a rule off (or lower it to `:warning` / `:info`) in the configuration file:

```edn
{:linters {:unresolved-symbol {:level :off}}}
```

Shorter notation to fully ignore some linters: `{:ignore [:unresolved-symbol :invalid-arity]}`. There is no `.gitignore`-style ignore file; exclude files by regex instead:

```edn
{:exclude-files "generated/.*\\.clj$"}
```

Scope a rule change to specific namespaces with `:config-in-ns` (optionally combined with `:ns-groups` patterns), or via `{:clj-kondo/config '...}` metadata on the `ns` form itself.

## When disabling is legitimate

- False positives on symbols introduced by third-party macros — but prefer `:lint-as` or a hook config over disabling `unresolved-symbol`.
- Generated or vendored Clojure/EDN sources: exclude them with `:exclude-files` rather than turning rules off globally.
- REPL-driven or scratch namespaces where `inline-def` is intentional: scope the exception with `:config-in-ns`.
- Prefer the narrowest suppression (inline > namespace > config file); disabling at MegaLinter level (`DISABLE_LINTERS`, `..._DISABLE_ERRORS`, `..._FILTER_REGEX_EXCLUDE`) is the last resort.
