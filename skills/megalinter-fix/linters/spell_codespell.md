# Fix SPELL_CODESPELL errors

<!-- generated-descriptor-info-start -->
- Linter: **codespell** (MegaLinter key: `SPELL_CODESPELL`)
- Descriptor: **SPELL** (other)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/spell_codespell/>
- Official documentation: <https://github.com/codespell-project/codespell>
- Auto-fix support: **yes** — add `SPELL_CODESPELL` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter SPELL_CODESPELL --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `.codespellrc` (custom path can be defined with `SPELL_CODESPELL_CONFIG_FILE`)
- Rules configuration: <https://github.com/codespell-project/codespell?tab=readme-ov-file#using-a-config-file>
- How to disable rules inline: <https://github.com/codespell-project/codespell?tab=readme-ov-file#inline-ignore>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `SPELL_CODESPELL` to fully disable this linter
  - `SPELL_CODESPELL_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `SPELL_CODESPELL_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `SPELL_CODESPELL_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `SPELL_CODESPELL_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `SPELL_CODESPELL_ERROR_DICT_NOT_FOUND`
  - `SPELL_CODESPELL_ERROR_CONFIG_INVALID`
<!-- generated-descriptor-info-end -->

## Fix instructions

codespell looks for a curated set of common misspellings in text and source files (it does not validate
every word against a full dictionary, which minimizes false positives on niche terms).

- Read each reported line: codespell prints the misspelled word and its suggested correction. Apply the
  suggestion when it fits the sentence.
- To fix in bulk, run `codespell -w` (`--write-changes`): without `-w` the tool only does a dry run.
  Combine with `-i` (`--interactive`) to review each correction before it is applied, which is safer
  when a misspelling has several candidate corrections.
- Beware of identifiers: if the "misspelling" is a variable, function or API name, renaming may break
  code — fix all occurrences consistently or suppress it instead (see below).
- More misspellings can be detected by enabling extra built-in dictionaries with `--builtin` (e.g.
  `--builtin=all`, incompatible with a custom `-D` dictionary).

## Inline disable

Append a `codespell:ignore` comment on the offending line, listing the words to ignore (a bare
`codespell:ignore` ignores every misspelling on that line):

```python
def wrod():  # codespell:ignore wrod
    pass
```

To suppress the following line instead, use `# codespell:ignore-next-line wrod` (or the bare form
`# codespell:ignore-next-line` to ignore all errors on the next line).

## Ignore via configuration

Options go in a `[codespell]` INI section (or `[tool.codespell]` in `pyproject.toml`). Files are read
in order `pyproject.toml`, `setup.cfg`, `.codespellrc`, then any `--config` file; command-line
arguments override configuration file settings.

```ini
[codespell]
skip = *.po,*.ts,./src/3rdParty,./src/Test
ignore-words-list = wrod,teh
ignore-words = .codespell-ignore
quiet-level = 3
```

- `skip` (CLI: `-S`/`--skip`) takes comma-separated glob patterns of files or directories to exclude.
- `ignore-words-list` (CLI: `-L word1,word2`) is a comma-separated allowlist of words.
- `ignore-words` (CLI: `-I`) points to a file with one word to ignore per line. Note: spelling errors
  are case-insensitive but words to ignore are case-sensitive — list the word as it appears in the
  codespell dictionary (e.g. `wrod` to also ignore `Wrod`).

## When disabling is legitimate

- The flagged word is a real identifier, product name, person name, or domain-specific term that
  happens to match a known misspelling (e.g. `als`, `crate`-adjacent terms).
- The file intentionally contains misspellings: test fixtures for spell checkers, historical quotes,
  changelogs reproducing an old typo, or non-English content.
- Generated or vendored files (minified assets, lock files, third-party sources) — exclude them with
  `skip` rather than editing them.

Disabling the whole linter at MegaLinter level is the last resort — prefer an inline ignore, an
allowlisted word, or a `skip` pattern.
