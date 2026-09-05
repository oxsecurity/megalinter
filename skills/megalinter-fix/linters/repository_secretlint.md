# Fix REPOSITORY_SECRETLINT errors

<!-- generated-descriptor-info-start -->
- Linter: **secretlint** (MegaLinter key: `REPOSITORY_SECRETLINT`)
- Descriptor: **REPOSITORY** (other)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/repository_secretlint/>
- Official documentation: <https://github.com/secretlint/secretlint>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.secretlintrc.json` (custom path can be defined with `REPOSITORY_SECRETLINT_CONFIG_FILE`)
- Ignore file: `.secretlintignore`
- Rules index: <https://github.com/secretlint/secretlint#rule-packages>
- Rules configuration: <https://github.com/secretlint/secretlint#configuration>
- How to ignore files and directories: <https://github.com/secretlint/secretlint/blob/master/docs/configuration.md#secretlintignore>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `REPOSITORY_SECRETLINT` to fully disable this linter
  - `REPOSITORY_SECRETLINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `REPOSITORY_SECRETLINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `REPOSITORY_SECRETLINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `REPOSITORY_SECRETLINT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

secretlint is a pluggable secret scanner: it detects committed credentials (AWS, GCP, Azure, GitHub, npm, Slack, OpenAI keys, private keys, basic auth...) via rule packages such as `@secretlint/secretlint-rule-preset-recommend`. A finding is a security incident, not a style issue.

For every reported secret, follow this remediation flow:

1. Treat the credential as compromised: revoke or rotate it in the issuing service (cloud console, token settings...).
2. Remove the secret from the file: load it from an environment variable or a secret manager instead of hardcoding it.
3. If the secret was already committed, purge it from git history (e.g. `git filter-repo`) — deleting it in a new commit is not enough.
4. Re-run the scan to confirm: `secretlint "**/*"`.

There is no auto-fix, but secretlint can mask detected secrets in a file in place: `secretlint <file> --format=mask-result --output=<file>`. Use `--no-maskSecrets` locally if you need to see the real value to identify it.

## Inline disable

Inline suppression requires adding the `@secretlint/secretlint-rule-filter-comments` rule to the configuration file. It then supports `secretlint-disable` / `secretlint-enable` blocks, `secretlint-disable-line`, `secretlint-disable-next-line`, optional rule targeting, and a `-- reason` suffix:

```js
// secretlint-disable-next-line @secretlint/secretlint-rule-github -- dummy token for docs
const example = "ghp_exampleShortenedDummyValue";
```

Prefer scoping the disable to a single rule and line rather than a whole block.

## Ignore via configuration

Disable a rule, allow known-safe patterns, or suppress specific message IDs in the configuration file:

```json
{
  "rules": [
    {
      "id": "@secretlint/secretlint-rule-preset-recommend",
      "rules": [
        {
          "id": "@secretlint/secretlint-rule-basicauth",
          "disabled": true
        },
        {
          "id": "@secretlint/secretlint-rule-aws",
          "options": { "allows": ["/dummy_secret/i"] },
          "allowMessageIds": ["AWSAccountID"]
        }
      ]
    }
  ]
}
```

When a rule comes from a preset, nest its entry inside the preset's own `rules` array as above. To skip files entirely, list them in the ignore file, which follows `.gitignore` syntax (`#` comments, `!` negation, forward slashes):

```text
# test fixtures with fake credentials
tests/fixtures/**
```

`.gitignore` entries and `.git`/`node_modules` are already ignored by default.

## When disabling is legitimate

- Documented placeholder or example credentials (docs, samples, test fixtures) that look real to a pattern matcher — prefer `allows` patterns or `allowMessageIds` scoped to the rule.
- Low-entropy identifiers reported by broad rules (e.g. AWS account IDs, basic-auth-looking URLs) that are not actually secret in your context.
- Encrypted or vaulted files (SOPS, Ansible Vault) whose ciphertext triggers pattern rules — exclude those paths in the ignore file.
- Never suppress a real credential: rotate it first, then clean the code and history. Disabling the linter at MegaLinter level is the last resort.
