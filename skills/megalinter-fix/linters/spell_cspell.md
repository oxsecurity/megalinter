# Fix SPELL_CSPELL errors

<!-- generated-descriptor-info-start -->
- Linter: **cspell** (MegaLinter key: `SPELL_CSPELL`)
- Descriptor: **SPELL** (other)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/spell_cspell/>
- Official documentation: <https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.cspell.json` (custom path can be defined with `SPELL_CSPELL_CONFIG_FILE`)
- Rules configuration: <https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell#customization>
- How to disable rules inline: <https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell#enable--disable-checking-sections-of-code>
- Error line format (regex): `Issues found: ([0-9]+) in .* file`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `SPELL_CSPELL` to fully disable this linter
  - `SPELL_CSPELL_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `SPELL_CSPELL_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `SPELL_CSPELL_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `SPELL_CSPELL_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

cspell spell-checks source code and text files, splitting identifiers written in CamelCase,
snake_case or compound style into words and validating them against language dictionaries.
There is no auto-fix: every reported word must be handled manually. Triage each finding:

- Real typo (misspelled word, comment, string, identifier): correct the spelling in the source.
  Remember cspell is case insensitive and only checks words longer than three characters, so a
  reported word is about spelling, not casing.
- Legitimate project word (product name, acronym, library, domain identifier): add it to the
  `words` list of `.cspell.json` so it is accepted repository-wide.
- Whole vocabulary category (e.g. TypeScript, Node, medical terms): enable the matching
  dictionary in the `dictionaries` list instead of adding words one by one.

MegaLinter generates a ready-to-use `.cspell.json` (containing all currently unknown words) in
its TextReporter artifacts: copy it to the repository root, fix the real typos in the source,
remove them from the generated list, and keep only the legitimate words.

## Inline disable

Use cspell control comments in any comment style supported by the file type:

- `// cspell:disable-line` — skip the current line
- `/* cspell:disable-next-line */` — skip the next line
- `/* cspell:disable */` ... `/* cspell:enable */` — skip a whole section
- `// cspell:ignore word1 word2` — ignore the listed words for the entire file
- `// cspell:words word1 word2` — declare the listed words as correct for the file

```js
const wierdName = "kept"; // cspell:disable-line
/* cspell:disable */
const zaallano = "not checked";
/* cspell:enable */
// cspell:ignore mkdirp tsmerge
```

## Ignore via configuration

Declare accepted words and exclusions in `.cspell.json` at the repository root:

- `words`: project terms considered correct (also suggested to contributors)
- `ignoreWords`: words to silently skip (never suggested)
- `ignorePaths`: glob patterns of files to skip entirely (e.g. lock files, vendored code)
- `ignoreRegExpList`: regex patterns whose matches are skipped (e.g. hashes, hex values)
- `dictionaries`: extra dictionaries to enable (e.g. `typescript`, `node`)

```json
{
  "version": "0.2",
  "language": "en",
  "words": ["megalinter", "mkdirp"],
  "ignoreWords": ["zaallano"],
  "ignorePaths": ["node_modules/**", "**/*.lock"],
  "ignoreRegExpList": ["0x[0-9a-f]+"],
  "dictionaries": ["typescript", "node"]
}
```

## When disabling is legitimate

- Foreign-language content in a project checked with an English dictionary (prefer enabling the
  matching language dictionary when one exists).
- Generated files containing hashes, minified code, or machine-produced identifiers: exclude
  them with `ignorePaths` rather than polluting the words list.
- Base64 blobs, hex dumps, or encoded payloads: match them with `ignoreRegExpList` or an inline
  `cspell:disable` section.
- File names that legitimately contain non-words: set `SPELL_CSPELL_ANALYZE_FILE_NAMES: false`
  in `.mega-linter.yml` instead of disabling the linter.

Disabling the whole linter via `DISABLE_LINTERS` or `SPELL_CSPELL_DISABLE_ERRORS` is a last
resort: prefer fixing typos and curating `.cspell.json`.
