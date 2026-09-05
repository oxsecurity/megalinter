# Fix REPOSITORY_BETTERLEAKS errors

<!-- generated-descriptor-info-start -->
- Linter: **betterleaks** (MegaLinter key: `REPOSITORY_BETTERLEAKS`)
- Descriptor: **REPOSITORY** (other)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/repository_betterleaks/>
- Official documentation: <https://github.com/betterleaks/betterleaks>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.betterleaks.toml` (custom path can be defined with `REPOSITORY_BETTERLEAKS_CONFIG_FILE`)
- Ignore file: `.betterleaksignore`
- Rules configuration: <https://github.com/betterleaks/betterleaks#configuration>
- How to disable rules inline: <https://github.com/betterleaks/betterleaks#betterleaksallow>
- How to ignore files and directories: <https://github.com/betterleaks/betterleaks#betterleaksignore>
- Error line format (regex): `leaks found: ([0-9]+)`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `REPOSITORY_BETTERLEAKS` to fully disable this linter
  - `REPOSITORY_BETTERLEAKS_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `REPOSITORY_BETTERLEAKS_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `REPOSITORY_BETTERLEAKS_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `REPOSITORY_BETTERLEAKS_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

betterleaks scans repository files and git history for hardcoded secrets (API keys, tokens,
credentials) using regex rules, keyword prefilters and Expr-based filters. There is no auto-fix:
every finding must be remediated manually.

For each reported leak:

1. Treat the secret as compromised: revoke or rotate it in the issuing service.
2. Remove it from the code and load it at runtime instead (environment variable, CI secret store, vault).
3. Deleting the line is not enough if the secret was ever committed — it stays in git history, which betterleaks also scans. Rotate it regardless, then ignore the historical finding by fingerprint (see below).
4. For fake placeholder values in tests or docs, use an inline allow comment or a fingerprint entry rather than weakening detection rules.

To accept all current findings and fail only on new ones, generate a JSON report and reuse it as baseline:

```bash
betterleaks dir . --report-path findings.json --report-format json
betterleaks dir . --baseline-path findings.json
```

## Inline disable

Append a `betterleaks:allow` comment on the flagged line (`gitleaks:allow` is also accepted for
backwards compatibility):

```yaml
api_key: 'example-key-for-documentation' # betterleaks:allow
```

## Ignore via configuration

In the ignore file, list one finding fingerprint per line, exactly as printed in the scan output.
The format is `commit:file:rule-id:start-line` for git scans, or `file:rule-id:start-line` for
directory scans:

```text
2a9f3c1d8b7e6f5a4c3b2a1d9e8f7c6b5a4d3e2f:config/settings.py:generic-api-key:12
```

In the configuration file, skip files globally with a `prefilter` Expr expression, or discard
matches of a single rule with a rule-level `filter`:

```toml
prefilter = '''
filter.matchesAny(get(attributes, "path", ""), [
  `(?:^|/)node_modules(?:/.*)?$`
])
'''

[[rules]]
id = "github-fine-grained-pat"
description = "GitHub Fine-Grained Personal Access Token"
regex = '''github_pat_\w{82}'''
keywords = ["github_pat_"]
filter = '''finding["secret"] contains "TESTING"'''
```

If no betterleaks configuration is present, a `.gitleaks.toml` in the scanned path is used as
fallback before the built-in default config.

## When disabling is legitimate

- Clearly fake example credentials in documentation or test fixtures — prefer an inline `betterleaks:allow` comment.
- Secrets already revoked or rotated that persist in git history — ignore the exact fingerprint instead of rewriting published history.
- Generated files or vendored dependencies triggering high-entropy false positives — exclude their paths with a `prefilter` expression.
- Never ignore a live secret: rotate it first. Disabling the linter at MegaLinter level is the last resort.
