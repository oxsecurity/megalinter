# Fix REPOSITORY_LS_LINT errors

<!-- generated-descriptor-info-start -->
- Linter: **ls-lint** (MegaLinter key: `REPOSITORY_LS_LINT`)
- Descriptor: **REPOSITORY** (other)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/repository_ls_lint/>
- Official documentation: <https://ls-lint.org/>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.ls-lint.yml` (custom path can be defined with `REPOSITORY_LS_LINT_CONFIG_FILE`)
- Rules index: <https://ls-lint.org/2.2/configuration/the-rules.html>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `REPOSITORY_LS_LINT` to fully disable this linter
  - `REPOSITORY_LS_LINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `REPOSITORY_LS_LINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `REPOSITORY_LS_LINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `REPOSITORY_LS_LINT_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `REPOSITORY_LS_LINT_ERROR_CONFIG_INVALID`
<!-- generated-descriptor-info-end -->

## Fix instructions

ls-lint checks directory and file **names** (not file contents) against naming-convention
rules declared in the configuration file. There is no auto-fix: every error must be fixed
by renaming the offending file or directory, or by adjusting the rules.

- Read the reported path and the expected rule, then rename the file or directory to match
  it (e.g. `MyComponent.js` -> `my-component.js` for a `kebab-case` rule). Use `git mv` so
  the rename is tracked.
- Built-in rules are: `regex`, `lowercase`, `camelcase` (camelCase), `pascalcase`
  (PascalCase), `snakecase` (snake_case), `screamingsnakecase` (SCREAMING_SNAKE_CASE),
  `kebabcase` (kebab-case) and `pointcase` (point.case).
- If several conventions are legitimate in the same tree, combine rules with the pipe
  operator instead of renaming: `.ts: camelCase | PascalCase`.
- For names that follow a project-specific pattern, use a custom regex rule
  (`regex:` wraps the pattern in `^...$`): `.js: regex:(Schema|Resolver)(\.test)?`.
- Mind sub-extensions: ls-lint treats `.d.ts` or `.umd.js` as their own extensions, so a
  rule on `.ts` does not cover `.d.ts` — add a dedicated rule when needed.
- A `REPOSITORY_LS_LINT_ERROR_CONFIG_INVALID` failure means the YAML configuration itself
  is malformed (not a naming error): fix the configuration file syntax first.

## Inline disable

ls-lint has no inline suppression mechanism: it lints file and directory names, not file
contents, so there is nothing to annotate. The only exclusion mechanism is the `ignore`
section of its configuration file (see below).

## Ignore via configuration

Rules live under the `ls` key (per path, per extension, `.dir` for directory names) and
exclusions under the `ignore` key. Glob patterns (`*`, `**`) and alternatives
(`{src,tests}`) are supported in both sections:

```yaml
ls:
  packages/*/src:
    .js: kebab-case
    .ts: camelCase | PascalCase
    .dir: kebab-case

ignore:
  - .git
  - node_modules
  - dist/**
```

To relax a rule instead of ignoring a path, widen it with `|` alternatives or replace it
with a `regex:` rule scoped to the relevant directory. There is no separate ignore file:
everything is defined in the configuration file named in the block above.

## When disabling is legitimate

- Generated or vendored trees (build output, `node_modules`, generated docs) whose names
  are produced by tools you do not control: add them to the `ignore` section.
- Files whose names are imposed by an external convention (e.g. framework-mandated
  `PascalCase` components inside a kebab-case codebase): scope a dedicated rule or `|`
  alternative to that directory rather than ignoring it.
- Migration periods where renaming would break imports or history at scale: ignore the
  legacy tree temporarily and lint only new directories.
- Disabling at MegaLinter level (`DISABLE_LINTERS` / `REPOSITORY_LS_LINT_DISABLE_ERRORS`)
  is the last resort — prefer fixing names or tuning `.ls-lint.yml`.
