# Fix REPOSITORY_KINGFISHER errors

<!-- generated-descriptor-info-start -->
- Linter: **kingfisher** (MegaLinter key: `REPOSITORY_KINGFISHER`)
- Descriptor: **REPOSITORY** (other)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/repository_kingfisher/>
- Official documentation: <https://github.com/mongodb/kingfisher>
- Auto-fix support: no (errors must be fixed manually)
- Rules index: <https://mongodb.github.io/kingfisher/rules/builtin-rules>
- How to disable rules inline: <https://mongodb.github.io/kingfisher/usage/advanced/?h=inline#inline-ignore-directives>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `REPOSITORY_KINGFISHER` to fully disable this linter
  - `REPOSITORY_KINGFISHER_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `REPOSITORY_KINGFISHER_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `REPOSITORY_KINGFISHER_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `REPOSITORY_KINGFISHER_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `REPOSITORY_KINGFISHER_ERROR_GITHUB_API_RATE_LIMIT`
  - `REPOSITORY_KINGFISHER_ERROR_GITHUB_TOKEN_UNAUTHORIZED`
  - `REPOSITORY_KINGFISHER_ERROR_RULES_LOAD_FAILED`
<!-- generated-descriptor-info-end -->

## Fix instructions

kingfisher is a secret scanner: it detects hardcoded credentials (API keys, tokens, private keys,
database connection strings...) using 1000+ built-in rules named `kingfisher.<provider>.<number>`
(e.g. `kingfisher.aws.1`), and can live-validate many of them to tell active secrets from stale ones.
There is no auto-fix: remediate each finding instead of editing it away.

- Treat every reported secret as compromised, especially when kingfisher validated it as active.
- Revoke or rotate the credential in the issuing service first (some rules support direct revocation).
- Remove the literal value from the code: read it from an environment variable or a secret manager.
- If the secret was ever committed, rotating it is mandatory — rewriting git history alone is not
  enough once the value has been pushed.
- Re-run the scan to confirm the finding is gone; use `--baseline-file baseline.yaml` (or
  `--manage-baseline`) to record known, accepted findings so they are not re-reported.

## Inline disable

Add a `kingfisher:ignore` token on the line of the finding (or on the lines surrounding a
multi-line value — kingfisher searches nearby lines, no language-specific comment marker required):

```python
API_KEY = "test-not-a-real-key"  # kingfisher:ignore
```

Directives from other scanners can be honored too via `--ignore-comment "gitleaks:allow"` in
`REPOSITORY_KINGFISHER_ARGUMENTS`; `--no-ignore` disables all inline suppressions.

## Ignore via configuration

kingfisher reads a `kingfisher.yaml` file only when passed explicitly with `--config kingfisher.yaml`
(add it through `REPOSITORY_KINGFISHER_ARGUMENTS`); a missing or malformed file is a fatal error.
Disable rules and exclude paths there:

```yaml
rules:
  disabled:
    - kingfisher.github.1
filters:
  exclude:
    - "**/node_modules/**"
    - "[Tt]ests"
  skip_words:
    - EXAMPLE
```

The same filters exist as CLI flags: `--exclude '<gitignore-style glob>'`, `--skip-word <word>`,
`--skip-regex <pattern>`, and `--skip-aws-account <id>` for AWS canary tokens.
Precedence is CLI flag > environment variable > `kingfisher.yaml` > built-in default, and list
values are additive.

## When disabling is legitimate

- Placeholder or documentation values (sample keys in READMEs, fixtures) that match a rule's
  pattern but are not real credentials — prefer inline `kingfisher:ignore` or `skip_words`.
- Test suites that intentionally embed fake secrets to exercise detection or auth code paths.
- Generated or vendored code (lockfiles, minified bundles) — exclude the path rather than the rule.
- Deliberately public tokens (e.g. publishable client-side keys) that the provider documents as
  safe to expose.

Never suppress a finding that kingfisher validated as an active secret — rotate it instead.
Disabling the linter at MegaLinter level is the last resort.
