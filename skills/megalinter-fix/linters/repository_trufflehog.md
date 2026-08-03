# Fix REPOSITORY_TRUFFLEHOG errors

<!-- generated-descriptor-info-start -->
- Linter: **trufflehog** (MegaLinter key: `REPOSITORY_TRUFFLEHOG`)
- Descriptor: **REPOSITORY** (other)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/repository_trufflehog/>
- Official documentation: <https://github.com/trufflesecurity/trufflehog>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.trufflehog.yml` (custom path can be defined with `REPOSITORY_TRUFFLEHOG_CONFIG_FILE`)
- Rules configuration: <https://github.com/trufflesecurity/trufflehog#regex-detector-alpha>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `REPOSITORY_TRUFFLEHOG` to fully disable this linter
  - `REPOSITORY_TRUFFLEHOG_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `REPOSITORY_TRUFFLEHOG_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `REPOSITORY_TRUFFLEHOG_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `REPOSITORY_TRUFFLEHOG_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

trufflehog is a secret scanner: it detects 800+ types of credentials (API keys, tokens, passwords) in the repository and can verify against live APIs whether a found credential is still active. Findings are leaked secrets, not code-style issues — there is no auto-fix.

Remediation flow for each finding:

1. Confirm the string is a real credential, not test/dummy data. A `Verified` result means trufflehog validated it against the provider's API: treat it as an active leak.
2. Rotate or revoke the credential at the provider immediately — once committed, consider it compromised even after deletion, because it stays in git history.
3. Remove the secret from the code: load it at runtime from an environment variable or a secret manager, and add the file holding real values to `.gitignore`.
4. If the secret was pushed, purge it from git history (e.g. `git filter-repo` or BFG) in addition to rotating it.
5. Re-run the scan to confirm the finding is gone.

Useful triage flags (pass via the linter arguments variable): `--results=verified` limits output to secrets confirmed valid by API, and `--exclude-detectors` takes a comma-separated list of detector types to skip.

## Inline disable

Add a `trufflehog:ignore` comment on the line containing the secret (works for sources that support line numbers, such as git and filesystem scans):

```python
EXAMPLE_KEY = "AKIA_SHORT_DUMMY"  # trufflehog:ignore
```

Only the annotated line is ignored; other findings in the file are still reported.

## Ignore via configuration

The configuration file passed with `--config` defines custom detectors and their filters. Tune a custom detector to reduce false positives with `exclude_words` (ignore matches containing these words), `entropy` (minimum randomness threshold), `exclude_regexes_match` and `exclude_regexes_capture`:

```yaml
detectors:
  - name: HogTokenDetector
    keywords:
      - hog
    regex:
      token: '[^A-Za-z0-9+\/]{0,1}([A-Za-z0-9+\/]{40})[^A-Za-z0-9+\/]{0,1}'
    exclude_words:
      - "EXAMPLE"
```

To exclude whole files or directories, create a file with one regex per line (e.g. `exclude-patterns.txt`):

```text
(.*/)?test/fixtures/
.*\.sample$
```

and pass it with `--exclude-paths exclude-patterns.txt` (via the linter arguments variable). Built-in detectors are skipped with `--exclude-detectors=<name-or-id>`.

## When disabling is legitimate

- The string is intentional fake/example data (documentation samples, placeholder keys in tests) — prefer a line-level `trufflehog:ignore` over any broader exclusion.
- High-entropy but non-secret content (minified bundles, lockfiles, generated fixtures) triggers detectors — exclude those paths with `--exclude-paths`.
- A detector is irrelevant to the stack and produces recurring unverified noise — exclude that single detector rather than the scan.
- A finding is a already-rotated historical credential that cannot be purged from history — suppress it explicitly, never by turning the scanner off.

Disabling the linter at MegaLinter level (`DISABLE_LINTERS` / `REPOSITORY_TRUFFLEHOG_DISABLE_ERRORS`) is the last resort: it silences every future secret leak, not just the current finding.
