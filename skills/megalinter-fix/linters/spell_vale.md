# Fix SPELL_VALE errors

<!-- generated-descriptor-info-start -->
- Linter: **vale** (MegaLinter key: `SPELL_VALE`)
- Descriptor: **SPELL** (other)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/spell_vale/>
- Official documentation: <https://vale.sh/>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.vale.ini` (custom path can be defined with `SPELL_VALE_CONFIG_FILE`)
- Rules index: <https://vale.sh/hub/>
- Rules configuration: <https://vale.sh/explorer/>
- How to disable rules inline: <https://vale.sh/docs/topics/vocab/>
- Error line format (regex): `([0-9]+) errors?`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `SPELL_VALE` to fully disable this linter
  - `SPELL_VALE_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `SPELL_VALE_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `SPELL_VALE_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `SPELL_VALE_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

Vale is a syntax-aware prose linter: it checks natural-language content (Markdown, reStructuredText, AsciiDoc, HTML...) against style rules grouped in styles (e.g. `Vale`, `Google`, `Microsoft`) plus spelling. There is no auto-fix command; edit the text manually:

- Spelling alerts (`Vale.Spelling` or `spelling`-based rules): fix the typo, or add legitimate project terms to a vocabulary (see below) instead of rewording.
- Terminology/substitution alerts: replace the flagged word with the suggested preferred term given in the alert message.
- Style alerts (passive voice, sentence length, headings casing...): reword the sentence to satisfy the rule of the named style.
- Each alert is identified as `StyleName.RuleName`; look it up in the styles under the `StylesPath` directory (or the rules index above) to understand what it enforces before rewriting.
- If a whole style package is missing, ensure it is declared and synced rather than deleting `BasedOnStyles` entries.

## Inline disable

Use Vale comment directives inside the document. In Markdown/HTML:

```markdown
<!-- vale off -->
This block is not checked at all.
<!-- vale on -->

<!-- vale Google.Headings = NO -->
## this heading may break the casing rule
<!-- vale Google.Headings = YES -->
```

For formats without HTML comments (e.g. MDX), declare the delimiters in `.vale.ini` (`CommentDelimiters = {/*, */}`) and use `{/* vale off */}` ... `{/* vale on */}` the same way.

## Ignore via configuration

In `.vale.ini`, disable a rule or lower its severity inside the glob section that applies to the file:

```ini
MinAlertLevel = suggestion

[*.md]
BasedOnStyles = Vale, Google
Google.Headings = NO          ; disable one rule
Vale.Spelling = warning       ; downgrade severity
```

Scope checks by glob: rules only run on files matched by a section header such as `[*.{md,txt}]`, so leave generated paths out of any section.

For accepted words, add a vocabulary instead of disabling spelling: create `<StylesPath>/config/vocabularies/<Name>/accept.txt` (and optionally `reject.txt`), one case-sensitive regex per line (`#` lines are comments), then enable it with `Vocab = <Name>` in `.vale.ini`.

## When disabling is legitimate

- Product names, acronyms, and domain jargon flagged as spelling errors: add them to a vocabulary `accept.txt` rather than disabling `Vale.Spelling`.
- Generated documentation, changelogs, or vendored docs that you do not author: exclude their globs from `.vale.ini` sections.
- Intentional divergence from an imported style guide (e.g. your headings casing differs from Google's): turn off that single `Style.Rule = NO`, not the whole style.
- Code samples or literal CLI output inside prose that a rule keeps flagging: wrap the block in `<!-- vale off -->` / `<!-- vale on -->`.

Disabling at MegaLinter level (`DISABLE_LINTERS`, `SPELL_VALE_DISABLE_ERRORS`) is the last resort.
