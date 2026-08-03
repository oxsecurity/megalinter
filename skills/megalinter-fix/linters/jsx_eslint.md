# Fix JSX_ESLINT errors

<!-- generated-descriptor-info-start -->
- Linter: **eslint** (MegaLinter key: `JSX_ESLINT`)
- Descriptor: **JSX** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/jsx_eslint/>
- Official documentation: <https://github.com/Rel1cx/eslint-react>
- Auto-fix support: **yes** — add `JSX_ESLINT` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter JSX_ESLINT --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `eslint.config.cjs` (custom path can be defined with `JSX_ESLINT_CONFIG_FILE`)
- Rules index: <https://eslint-react.xyz/docs/rules/overview>
- Rules configuration: <https://eslint-react.xyz/docs/getting-started/installation>
- How to disable rules inline: <https://eslint.org/docs/latest/use/configure/rules#disabling-rules>
- How to ignore files and directories: <https://eslint.org/docs/latest/user-guide/configuring/ignoring-code#the-eslintignore-file>
- Error line format (regex): `✖ ([0-9]+) problem`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `JSX_ESLINT` to fully disable this linter
  - `JSX_ESLINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `JSX_ESLINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `JSX_ESLINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `JSX_ESLINT_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `JSX_ESLINT_ERROR_PLUGIN_NOT_FOUND`
  - `JSX_ESLINT_ERROR_CONFIG_NOT_FOUND`
  - `JSX_ESLINT_ERROR_FLAT_CONFIG_MODULE_NOT_FOUND`
<!-- generated-descriptor-info-end -->

## Fix instructions

ESLint with the `@eslint-react/eslint-plugin` plugin lints JSX/React code for correctness,
JSX pitfalls, DOM security and Web API resource leaks. Rules are prefixed `@eslint-react/`.

- Run `npx eslint . --fix` (or MegaLinter auto-fix) first: many rules are auto-fixable,
  e.g. `@eslint-react/jsx-no-useless-fragment`, `@eslint-react/jsx-no-children-prop`,
  `@eslint-react/dom-no-missing-button-type`, `@eslint-react/dom-no-unsafe-target-blank`.
- Hooks errors (`rules-of-hooks`, `exhaustive-deps`): call hooks only at the top level of
  components/custom hooks, and list every reactive value in the dependency array.
- Core React errors (e.g. `no-missing-key`): fix the component logic — add a stable `key`
  to list items, remove unsafe lifecycle methods, migrate deprecated Context API usage.
- DOM security errors: add `type="button"` to non-submit buttons and add
  `rel="noopener noreferrer"` to `target="_blank"` links.
- Web API errors: clean up timers, listeners and observers in the effect cleanup function.

## Inline disable

Use standard ESLint suppression comments with the full rule name:

```jsx
{/* eslint-disable-next-line @eslint-react/no-missing-key */}
{items.map((item) => <Item {...item} />)}
```

Other forms: `// eslint-disable-line <rule>` (same line), and block scope with
`/* eslint-disable <rule> */` ... `/* eslint-enable <rule> */`. A `/* eslint-disable */`
comment at the top of a file disables rules for the whole file.

## Ignore via configuration

In the flat configuration file, lower or disable a rule in the `rules` object, and exclude
files with `globalIgnores()` (evaluated relative to the config file; end directory patterns
with `/`):

```js
const { defineConfig, globalIgnores } = require("eslint/config");

module.exports = defineConfig([
  globalIgnores(["dist/", "**/*.generated.jsx"]),
  {
    rules: {
      "@eslint-react/no-missing-key": "off",
    },
  },
]);
```

Flat config has no separate ignore file: `**/node_modules/` and `.git/` are ignored by
default, and `--ignore-pattern` can be passed on the command line for one-off exclusions.

## When disabling is legitimate

- Generated or vendored JSX (build output, codegen, storybook artifacts): exclude the paths
  with `globalIgnores()` instead of littering the files with disable comments.
- `exhaustive-deps` false positives on values that are intentionally stable (refs, setState
  functions): suppress inline with a comment explaining why the dependency is omitted.
- React 19+ codemod rules (e.g. deprecated Context API replacements) on a codebase pinned
  to an older React version: turn the rule off in the config until the upgrade.
- Keys genuinely unavailable for a static, never-reordered list: a targeted inline disable
  is acceptable; never disable DOM security rules globally.

Disabling the linter at MegaLinter level is the last resort — prefer fixing, then inline
suppression, then configuration-level exclusion.
