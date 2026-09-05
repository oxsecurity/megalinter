# Fix SPELL_PROSELINT errors

<!-- generated-descriptor-info-start -->
- Linter: **proselint** (MegaLinter key: `SPELL_PROSELINT`)
- Descriptor: **SPELL** (other)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/spell_proselint/>
- Official documentation: <https://github.com/amperser/proselint>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.proselintrc.json` (custom path can be defined with `SPELL_PROSELINT_CONFIG_FILE`)
- Rules index: <https://github.com/amperser/proselint#checks>
- Rules configuration: <https://github.com/amperser/proselint#checks>
- Error line format (regex): `:([0-9]+):([0-9]+): (.*)`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `SPELL_PROSELINT` to fully disable this linter
  - `SPELL_PROSELINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `SPELL_PROSELINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `SPELL_PROSELINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `SPELL_PROSELINT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

proselint lints English prose (Markdown and text files) for style problems: typography, clichés, jargon, redundancy, hedging, spelling consistency and more. There is no auto-fix: apply each suggestion manually — every error message ends with the check ID and usually a suggested replacement, so follow that suggestion.

- Typography (`typography.symbols`, e.g. `typography.symbols.curly_quotes`): replace the flagged characters with the symbol the message suggests (curly quotes, real ellipsis, etc.), or disable the check if the repository mandates plain ASCII.
- Clichés and corporate speak (`cliches.misc`, `cliches.hell`): rewrite the phrase in plain, direct words.
- Redundancy (`redundancy.ras_syndrome`, e.g. "PIN number"): delete the redundant word.
- Hedging and weasel words (`hedging`): remove the qualifier or state the claim directly.
- Spelling consistency (`spelling.consistency`): pick one spelling variant and use it throughout the file.
- Uncomparables (`uncomparables`): drop the modifier before an absolute adjective ("very unique" becomes "unique").
- Dates and times (`dates_times.am_pm`, `dates_times.dates`): normalize to the format the message recommends.

Reproduce locally with `proselint check myfile.md` (version 0.16+ requires the `check` subcommand).

## Inline disable

proselint has no inline suppression syntax: no comment or marker in the linted text can silence a check. Disable the check in the configuration file or exclude the file from the linter instead (see below).

## Ignore via configuration

Disable checks through the `"checks"` map of the configuration file. Keys cascade: a category entry covers all its checks, and a more specific key overrides it:

```json
{
  "max_errors": 1000,
  "checks": {
    "typography.symbols": false,
    "typography.symbols.curly_quotes": true,
    "cliches.misc": false
  }
}
```

`max_errors` caps the number of reported errors. The `per_file_checks` section of the same file applies check overrides only to files matching glob patterns. proselint has no separate ignore file: to skip whole files, use file exclusion at the MegaLinter level.

## When disabling is legitimate

- Prose style is opinionated: documentation that intentionally uses an informal tone, marketing wording or domain jargon can legitimately turn off `cliches.*` or hedging-related checks.
- Typography checks such as `typography.symbols` conflict with repositories that require plain-ASCII Markdown; disabling them in the configuration file is standard practice.
- Auto-generated Markdown (changelogs, API docs) triggers false positives on capitalization and symbols; exclude those paths rather than editing generated text.
- Disabling the whole linter at MegaLinter level is the last resort — prefer fixing the prose, then per-check configuration, then file exclusion.
