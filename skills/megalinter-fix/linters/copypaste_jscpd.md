# Fix COPYPASTE_JSCPD errors

<!-- generated-descriptor-info-start -->
- Linter: **jscpd** (MegaLinter key: `COPYPASTE_JSCPD`)
- Descriptor: **COPYPASTE** (other)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/copypaste_jscpd/>
- Official documentation: <https://github.com/kucherenko/jscpd/tree/master/apps/jscpd>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.jscpd.json` (custom path can be defined with `COPYPASTE_JSCPD_CONFIG_FILE`)
- Rules configuration: <https://github.com/kucherenko/jscpd/tree/master/apps/jscpd#config-file>
- How to disable rules inline: <https://github.com/kucherenko/jscpd/tree/master/apps/jscpd#ignored-blocks>
- Error line format (regex): `Found ([0-9]+) clones`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `COPYPASTE_JSCPD` to fully disable this linter
  - `COPYPASTE_JSCPD_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `COPYPASTE_JSCPD_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `COPYPASTE_JSCPD_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `COPYPASTE_JSCPD_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

jscpd detects duplicated code blocks (copy-paste) across 150+ languages and formats, and fails when the number of clones or the overall duplication percentage exceeds the configured threshold. There is no auto-fix: resolve findings by refactoring.

- Open the reported clone pair (both file locations are listed in the output) and compare the duplicated fragments.
- Extract the duplicated logic into a shared function, method, class, or module, then call it from both places.
- For duplicated configuration or markup, factor the common part into an include, template, partial, or base definition.
- When the duplication is intentional (test fixtures, generated code, scaffolded boilerplate), do not force an artificial abstraction: exclude it via an inline ignore block or an `ignore` glob pattern instead.

## Inline disable

Wrap an intentionally duplicated section between `jscpd:ignore-start` and `jscpd:ignore-end` markers placed in comments (use the comment syntax of the file's language, e.g. `<!-- jscpd:ignore-start -->` in HTML/markup):

```javascript
/* jscpd:ignore-start */
const duplicatedButIntentional = buildFixture();
/* jscpd:ignore-end */
```

Everything between the two markers is excluded from duplication detection.

## Ignore via configuration

Create a `.jscpd.json` file at the repository root (a `"jscpd"` property in `package.json` also works). Main options:

- `threshold`: maximum allowed duplication percentage; jscpd exits with an error above it
- `ignore`: array of glob patterns for files or directories to skip
- `minLines` / `minTokens`: minimum size of a block to be reported as a clone (defaults: 5 lines, 50 tokens)
- `format`: list of formats (languages) to analyze for duplications
- `mode`: detection strictness — `strict`, `mild` (default), or `weak`

```json
{
  "threshold": 0,
  "ignore": ["**/__snapshots__/**", "**/vendor/**"],
  "minLines": 10,
  "minTokens": 70,
  "format": ["javascript", "typescript"]
}
```

Raising `minLines`/`minTokens` filters out small incidental repetitions; use `ignore` for whole files or folders that are duplicated by design.

## When disabling is legitimate

- A few similar lines repeated two or three times: a premature abstraction is often worse than the duplication itself.
- Cross-language or cross-format duplication (e.g. the same constants in a JS file and a YAML config) that cannot share code.
- Generated or scaffolded files (snapshots, migrations, framework boilerplate) that will be regenerated anyway — exclude them with `ignore` globs.
- Prefer targeted inline ignores or `.jscpd.json` excludes; MegaLinter-level tuning (`COPYPASTE_JSCPD_FILTER_REGEX_EXCLUDE`, `DISABLE_LINTERS`) is a last resort.
