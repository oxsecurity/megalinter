# Fix TSX_ESLINT errors

<!-- generated-descriptor-info-start -->
- Linter: **eslint** (MegaLinter key: `TSX_ESLINT`)
- Descriptor: **TSX** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/tsx_eslint/>
- Official documentation: <https://github.com/Rel1cx/eslint-react>
- Auto-fix support: **yes** — add `TSX_ESLINT` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter TSX_ESLINT --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `eslint.config.cjs` (custom path can be defined with `TSX_ESLINT_CONFIG_FILE`)
- Rules index: <https://eslint-react.xyz/docs/rules/overview>
- Rules configuration: <https://eslint-react.xyz/docs/getting-started/installation>
- How to disable rules inline: <https://eslint.org/docs/latest/use/configure/rules#disabling-rules>
- How to ignore files and directories: <https://eslint.org/docs/latest/use/configure/ignore#the-eslintignore-file>
- Error line format (regex): `✖ ([0-9]+) problem`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `TSX_ESLINT` to fully disable this linter
  - `TSX_ESLINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `TSX_ESLINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `TSX_ESLINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `TSX_ESLINT_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `TSX_ESLINT_ERROR_PLUGIN_NOT_FOUND`
  - `TSX_ESLINT_ERROR_PARSER_NOT_FOUND`
  - `TSX_ESLINT_ERROR_FLAT_CONFIG_MODULE_NOT_FOUND`
  - `TSX_ESLINT_ERROR_OUT_OF_MEMORY`
<!-- generated-descriptor-info-end -->

## Fix instructions

This linter runs ESLint with the `@eslint-react/eslint-plugin` package on TSX files: it checks React/TSX code for correctness bugs, DOM misuse, resource leaks and naming conventions, on top of core ESLint and typescript-eslint rules.

- Run the linter's own auto-fix first: `npx eslint . --fix` — fixable rules (e.g. `no-useless-fragment`, `no-children-prop`) are corrected automatically.
- `no-missing-key`: add a stable, unique `key` prop to every element produced in a list rendering (`.map(...)`), never the array index when the list can reorder.
- Web API leak rules (`no-leaked-timeout`, `no-leaked-event-listener`): return a cleanup function from the effect that calls `clearTimeout` / `removeEventListener`.
- `no-dangerously-set-innerhtml`: replace `dangerouslySetInnerHTML` with rendered children, or sanitize the HTML if it is unavoidable.
- `no-nested-component-definitions`: move the inner component definition out of the parent component's body to module scope.
- Naming-convention rules (`context-name`, `ref-name`): rename identifiers to carry the expected `Context` / `Ref` suffix.
- Rules use origin prefixes such as `@eslint-react/`, `@eslint-react/dom/`, `@eslint-react/web-api/` — look the exact rule name up in the rules index above before changing code.

## Inline disable

Use standard ESLint disable comments with the fully prefixed rule name.

```tsx
// eslint-disable-next-line @eslint-react/no-missing-key
const rows = items.map((item) => <Row {...item} />);

const legacy = html; // eslint-disable-line @eslint-react/dom/no-dangerously-set-innerhtml
```

Inside JSX markup, wrap the comment in braces: `{/* eslint-disable-next-line @eslint-react/no-missing-key */}`. `/* eslint-disable rule */` ... `/* eslint-enable rule */` block comments disable a rule for a whole region or file.

## Ignore via configuration

In the flat configuration file, set a rule to `"off"` (or `"warn"`) in a `rules` block, and exclude files with `ignores`:

```js
module.exports = [
  {
    ignores: ["**/generated/**", "dist/**"],
  },
  {
    files: ["**/*.tsx"],
    rules: {
      "@eslint-react/no-missing-key": "off",
    },
  },
];
```

Flat config has no separate `.eslintignore` file: global `ignores` entries (or the `globalIgnores()` helper from `eslint/config`) replace it, and only global patterns can match whole directories.

## When disabling is legitimate

- Generated TSX (design-system output, GraphQL codegen, storybook artifacts): exclude the directories via `ignores` instead of fixing files that will be regenerated.
- Type-aware rules misfire when the TypeScript project service is not configured; fix `parserOptions` (`projectService`, `tsconfigRootDir`) before disabling the rule itself.
- Intentional `dangerouslySetInnerHTML` on already-sanitized CMS content: disable inline on that line with a justifying comment, not globally.
- Naming-convention rules may conflict with an established in-house convention; turning them off repo-wide in the configuration file is acceptable.

Disabling the linter at MegaLinter level is the last resort — prefer fixing the code, then inline disables, then configuration-level rule tuning.
