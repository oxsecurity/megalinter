# Fix JAVASCRIPT_STANDARD errors

<!-- generated-descriptor-info-start -->
- Linter: **standard** (MegaLinter key: `JAVASCRIPT_STANDARD`)
- Descriptor: **JAVASCRIPT** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/javascript_standard/>
- Official documentation: <https://standardjs.com/>
- Auto-fix support: **yes** — add `JAVASCRIPT_STANDARD` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter JAVASCRIPT_STANDARD --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Rules index: <https://standardjs.com/rules.html>
- Rules configuration: <https://standardjs.com/#how-do-i-ignore-files>
- How to disable rules inline: <https://standardjs.com/#how-do-i-disable-a-rule>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `JAVASCRIPT_STANDARD` to fully disable this linter
  - `JAVASCRIPT_STANDARD_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `JAVASCRIPT_STANDARD_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `JAVASCRIPT_STANDARD_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `JAVASCRIPT_STANDARD_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

standard enforces JavaScript Standard Style — a zero-configuration preset of formatting and code-quality rules (2-space indentation, no semicolons, single quotes, spaces after keywords and before function parentheses, `===` instead of `==`, no unused variables, curly braces for multi-line `if`, always handle the `err` callback parameter).

- Run `standard --fix` (or the MegaLinter auto-fix described above) first: it automatically corrects most formatting violations (indentation, semicolons, quotes, spacing).
- Fix the remaining errors manually — they are usually code-quality issues auto-fix cannot solve: remove unused variables, replace `==` with `===`, handle the `err` parameter in Node.js callbacks, wrap conditional assignments in extra parentheses, remove `debugger`/`eval()` and unreachable code.
- For "x is not defined" errors on legitimate globals, declare them with `/* global myVar1, myVar2 */` at the top of the file, or for test frameworks add `/* eslint-env mocha */` (or pass `--env mocha` / `--global myVar1` via the linter arguments).

## Inline disable

standard uses ESLint suppression comments.

```js
file = 'text' // eslint-disable-line no-use-before-define

/* eslint-disable no-use-before-define */
// ... block where the rule is off ...
/* eslint-enable no-use-before-define */
```

Omitting the rule name (`// eslint-disable-line`) disables all rules on that line; always prefer naming the specific rule.

## Ignore via configuration

standard is intentionally not configurable rule-by-rule ("no bikeshedding"): you cannot turn individual rules off in a config file. Configuration in `package.json` is limited to ignores, globals and env:

```json
{
  "standard": {
    "ignore": ["**/out/", "/lib/select2/"],
    "globals": ["myVar1"]
  }
}
```

`node_modules/`, `coverage/`, `vendor/`, `*.min.js`, dotfiles and paths listed in `.gitignore` are already ignored by default. If rule-level tuning is really required, switch to `semistandard`, `standardx`, or ESLint with `eslint-config-standard`.

## When disabling is legitimate

- Generated, bundled or minified files not already covered by the default ignores — add them to `standard.ignore`.
- Third-party or vendored code that must keep its upstream style.
- Globals injected by the runtime or a test framework — prefer `globals`/`eslint-env` declarations over disabling the linter.
- Temporary, documented workarounds during a refactor, using a rule-specific inline disable.
- Disabling at MegaLinter level (`DISABLE_LINTERS` / `..._DISABLE_ERRORS`) is the last resort, only when the project deliberately does not follow Standard Style.
