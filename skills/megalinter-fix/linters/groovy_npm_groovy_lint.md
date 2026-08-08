# Fix GROOVY_NPM_GROOVY_LINT errors

<!-- generated-descriptor-info-start -->
- Linter: **npm-groovy-lint** (MegaLinter key: `GROOVY_NPM_GROOVY_LINT`)
- Descriptor: **GROOVY** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/groovy_npm_groovy_lint/>
- Official documentation: <https://nvuillam.github.io/npm-groovy-lint/>
- Auto-fix support: **yes** — add `GROOVY_NPM_GROOVY_LINT` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter GROOVY_NPM_GROOVY_LINT --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `.groovylintrc.json` (custom path can be defined with `GROOVY_NPM_GROOVY_LINT_CONFIG_FILE`)
- Rules index: <https://codenarc.org/codenarc-rule-index.html>
- Rules configuration: <https://github.com/nvuillam/npm-groovy-lint#configuration>
- How to disable rules inline: <https://github.com/nvuillam/npm-groovy-lint#disabling-rules-in-source>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `GROOVY_NPM_GROOVY_LINT` to fully disable this linter
  - `GROOVY_NPM_GROOVY_LINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `GROOVY_NPM_GROOVY_LINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `GROOVY_NPM_GROOVY_LINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `GROOVY_NPM_GROOVY_LINT_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `GROOVY_NPM_GROOVY_LINT_ERROR_CODENARC_SERVER`
<!-- generated-descriptor-info-end -->

## Fix instructions

npm-groovy-lint lints Groovy and Jenkinsfile sources against CodeNarc rules (presets `recommended`, `recommended-jenkinsfile`, `all`), reporting findings with `error`, `warning` or `info` severity.

- Start with the built-in auto-fix: run `npm-groovy-lint --fix path/to/file.groovy` (or the MegaLinter auto-fix described in the block above). It resolves many mechanical findings such as `UnnecessarySemicolon`, `TrailingWhitespace`, `SpaceAfterComma` and `UnusedImport`.
- For layout-only findings (indentation, spacing, braces), run `npm-groovy-lint --format` to reformat the source instead of editing by hand.
- Restrict what auto-fix touches with `--fixrules SpaceAfterComma,TrailingWhitespace` or exclude risky ones with `--fixrulesexclude Indentation,IndentationClosingBraces`.
- Fix the remaining findings manually by rule family: remove unused imports/variables (`imports`/`unused` rules), replace `def` with explicit types where `NoDef` is enforced, rename identifiers to match `naming` conventions, and address `security`/`design` findings by changing the code they flag rather than suppressing them.
- Look up any unfamiliar rule in the CodeNarc rule index linked above before changing code — each rule page states its intent and configurable properties.

## Inline disable

Use ESLint-style comments in the Groovy source.

Disable for a whole block (optionally naming rules):

```groovy
/* groovylint-disable NoDef, UnnecessarySemicolon */
def variable = 1;
/* groovylint-enable NoDef, UnnecessarySemicolon */
```

Disable for a single line:

```groovy
def variable = 1; // groovylint-disable-line NoDef, UnnecessarySemicolon
// groovylint-disable-next-line NoDef
def other = 2
```

A bare `/* groovylint-disable */` (or `// groovylint-disable-line` without rule names) disables all rules for that scope — always prefer naming the rules.

## Ignore via configuration

In the configuration file, set a rule to `"off"` or tune its severity/properties under `rules` (rule names may be prefixed by their CodeNarc section):

```json
{
    "extends": "recommended",
    "rules": {
        "comments.ClassJavadoc": "off",
        "formatting.Indentation": {
            "spacesPerIndentLevel": 4,
            "severity": "info"
        }
    }
}
```

There is no dedicated ignore file; exclude files with the `-i, --ignorepattern` CLI option, a comma-separated list of Ant-style patterns (pass it through the linter arguments variable listed in the block above):

```bash
npm-groovy-lint --ignorepattern "**/test/*,**/vendor/*"
```

## When disabling is legitimate

- Jenkinsfiles legitimately violate general Groovy rules (scripted DSL, no classes): switch `extends` to `recommended-jenkinsfile` or turn the offending rules off rather than fixing each file.
- Documentation rules such as `ClassJavadoc` are often intentionally not enforced on internal scripts — disable them in the configuration file project-wide.
- `NoDef` and typing rules conflict with idiomatic dynamic Groovy scripts; disabling them is a legitimate style choice when the team standard allows `def`.
- Generated or vendored Groovy sources should be excluded with `--ignorepattern` instead of being fixed.

Disabling the whole linter at MegaLinter level is the last resort — prefer rule-level or file-level exclusions above.
