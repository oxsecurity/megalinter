# Fix ACTION_ZIZMOR errors

<!-- generated-descriptor-info-start -->
- Linter: **zizmor** (MegaLinter key: `ACTION_ZIZMOR`)
- Descriptor: **ACTION** (tooling_format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/action_zizmor/>
- Official documentation: <https://zizmor.sh/>
- Auto-fix support: **yes** — add `ACTION_ZIZMOR` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter ACTION_ZIZMOR --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `zizmor.yml` (custom path can be defined with `ACTION_ZIZMOR_CONFIG_FILE`)
- Rules index: <https://docs.zizmor.sh/audits/>
- Rules configuration: <https://docs.zizmor.sh/configuration/>
- How to disable rules inline: <https://docs.zizmor.sh/usage/#with-comments>
- Error line format (regex): `([0-9]+) findings?`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `ACTION_ZIZMOR` to fully disable this linter
  - `ACTION_ZIZMOR_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `ACTION_ZIZMOR_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `ACTION_ZIZMOR_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `ACTION_ZIZMOR_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `ACTION_ZIZMOR_ERROR_GITHUB_API_UNREACHABLE`
<!-- generated-descriptor-info-end -->

## Fix instructions

zizmor is a static security auditor for GitHub Actions workflow files (plus Dependabot and pre-commit configs). Fix findings by hardening the workflow, per rule category:

- `excessive-permissions`: add an explicit minimal `permissions:` block (e.g. `permissions: {}` at workflow level, then `contents: read` per job as needed).
- `template-injection`: never expand attacker-controllable `${{ ... }}` expressions inside `run:` scripts; pass the value through an intermediate `env:` variable and reference it as `"$VAR"` in the shell.
- `unpinned-uses` / `unpinned-images`: pin third-party actions to a full commit SHA (`uses: actions/checkout@<40-char-sha> # vX.Y.Z`) and container images to a `sha256:` digest.
- `known-vulnerable-actions` / `archived-uses`: upgrade the action to a patched release, or replace an archived/unmaintained action with a maintained alternative.
- `dangerous-triggers`: avoid `pull_request_target` and `workflow_run` on workflows that check out or execute untrusted PR code; prefer `pull_request` or split privileged steps into a separate trusted workflow.
- `secrets-inherit` / `overprovisioned-secrets`: pass only the individual secrets a reusable workflow needs instead of `secrets: inherit` or the whole `secrets` context.
- `github-env` / `insecure-commands`: avoid writing untrusted data to `GITHUB_ENV`/`GITHUB_PATH` and remove deprecated workflow commands like `set-env`.

Many rules are auto-fixable (`artipacked`, `bot-conditions`, `cache-poisoning`, `insecure-commands`, `known-vulnerable-actions`, `obfuscation`, ...): run `zizmor --fix <file>` locally (safe fixes only; `--fix=all` also applies fixes needing manual review), or use the MegaLinter auto-fix described in the block above. Some audits need GitHub API access: set `GH_TOKEN` (or run with `--offline` and accept fewer audits).

## Inline disable

Add a `# zizmor: ignore[rulename]` YAML comment anywhere inside the span of the finding (multiple rules comma-separated, optional trailing justification). It cannot be placed inside a string or block literal — put it on the key line instead:

```yaml
run: | # zizmor: ignore[template-injection] title is sanitized upstream
  echo "${{ github.event.issue.title }}"
```

## Ignore via configuration

In the configuration file (auto-discovered at the repository root or under `.github/`), disable a rule globally or ignore specific findings by `filename[:line[:column]]`:

```yaml
rules:
  template-injection:
    disable: true
  unpinned-uses:
    ignore:
      - ci.yml            # whole file
      - release.yml:100   # specific line
```

Severity can also be remapped per rule (`remap: {severity: low}`), and some audits accept a `config:` block (see each audit's page in the rules index). There is no separate ignore-file mechanism.

## When disabling is legitimate

- The expanded expression is provably not attacker-controllable (e.g. a value you fully define in the same workflow) and `template-injection` still flags it.
- First-party actions maintained in the same organization where SHA-pinning every internal release adds churn without a trust boundary crossing — scope the `unpinned-uses` ignore to those files only.
- `dangerous-triggers` on a workflow that genuinely needs `pull_request_target` and already never checks out or executes PR-controlled code.
- Findings raised only under `--persona=pedantic`/`auditor` that are accepted code-smell trade-offs, not security issues.

Prefer an inline `# zizmor: ignore[...]` with a justification, then a scoped entry in the configuration file; disabling the linter at MegaLinter level is the last resort.
