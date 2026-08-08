# Fix ENV_DOTENV_LINTER errors

<!-- generated-descriptor-info-start -->
- Linter: **dotenv-linter** (MegaLinter key: `ENV_DOTENV_LINTER`)
- Descriptor: **ENV** (format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/env_dotenv_linter/>
- Official documentation: <https://dotenv-linter.github.io/>
- Auto-fix support: **yes** — add `ENV_DOTENV_LINTER` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter ENV_DOTENV_LINTER --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Rules index: <https://dotenv-linter.github.io/#/?id=dotenv-linter>
- Rules configuration: <https://dotenv-linter.github.io/#/usage/check>
- How to disable rules inline: <https://dotenv-linter.github.io/#/usage/check?id=skip-checks>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `ENV_DOTENV_LINTER` to fully disable this linter
  - `ENV_DOTENV_LINTER_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `ENV_DOTENV_LINTER_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `ENV_DOTENV_LINTER_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `ENV_DOTENV_LINTER_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

dotenv-linter checks `.env` files for 14 problems: DuplicatedKey, EndingBlankLine, ExtraBlankLine,
IncorrectDelimiter, KeyWithoutValue, LeadingCharacter, LowercaseKey, QuoteCharacter, SchemaViolation,
SpaceCharacter, SubstitutionKey, TrailingWhitespace, UnorderedKey and ValueWithoutQuotes.

Almost every check is auto-fixable: prefer running `dotenv-linter fix <file>` (or the MegaLinter
auto-fix described in the block above) instead of editing by hand. Add `--dry-run` to preview the
fixed content, or `--no-backup` to skip backup files. For manual fixes:

- `DuplicatedKey`: keep a single assignment per key; delete or rename the duplicate.
- `UnorderedKey`: sort keys alphabetically, or split them into logical groups separated by a blank line (each group is ordered independently).
- `LowercaseKey` / `IncorrectDelimiter` / `LeadingCharacter`: rename keys to `UPPER_SNAKE_CASE` starting with `A-Z` or `_` (e.g. `foo-bar=1` becomes `FOO_BAR=1`), then update the code reading them.
- `KeyWithoutValue`: write `FOO=` for an intentionally empty value instead of a bare `FOO`.
- `QuoteCharacter` / `ValueWithoutQuotes`: unquote simple values (`FOO=BAR`, not `FOO="BAR"`); quote values containing whitespace (`FOO="BAR BAZ"`).
- `SpaceCharacter` / `TrailingWhitespace` / `EndingBlankLine` / `ExtraBlankLine`: remove spaces around `=` and trailing spaces; end the file with exactly one newline.
- `SubstitutionKey`: close substitution braces properly (`ABC=${BAR}`, not `ABC=${BAR`).
- `SchemaViolation`: make the value match the schema file passed with `check --schema PATH`, or update that schema.

An `export FOO=BAR` prefix is accepted; `.envrc` files are never checked (direnv bash scripts).

## Inline disable

Use control comments inside the `.env` file. At the top of the file, disable checks for the whole
file; around specific lines, disable and re-enable them:

```env
# dotenv-linter:off DuplicatedKey, EndingBlankLine

# dotenv-linter:off UnorderedKey
FOO=BAR
BAR=FOO
# dotenv-linter:on UnorderedKey
```

## Ignore via configuration

dotenv-linter has no configuration file. Disable checks or exclude files with CLI arguments
(pass them through the MegaLinter arguments variable listed above):

```bash
dotenv-linter check --ignore-checks UnorderedKey,EndingBlankLine .   # or -i
dotenv-linter check --exclude .env.test .                            # or -e
```

The `DOTENV_LINTER_IGNORE_CHECKS` environment variable (comma-separated check names) disables
checks globally without touching the command line:

```bash
DOTENV_LINTER_IGNORE_CHECKS=QuoteCharacter dotenv-linter check .
```

## When disabling is legitimate

- `UnorderedKey` on files organized by functional groups: prefer blank lines between groups (ordering restarts per group) before disabling the check.
- `QuoteCharacter` when the consuming framework (e.g. docker-compose, some dotenv parsers) treats quotes as part of the value or requires them.
- `LowercaseKey` when a third-party tool mandates lowercase variable names you cannot rename.
- Template files such as `.env.example` where placeholder values legitimately trigger `KeyWithoutValue`: prefer `--exclude` or the file-level `# dotenv-linter:off` comment.

Disabling the linter at MegaLinter level (`DISABLE_LINTERS` or `..._DISABLE_ERRORS`) is the last
resort, once targeted fixes, control comments and check-level ignores are ruled out.
