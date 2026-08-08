# Fix REPOSITORY_TRIVY errors

<!-- generated-descriptor-info-start -->
- Linter: **trivy** (MegaLinter key: `REPOSITORY_TRIVY`)
- Descriptor: **REPOSITORY** (other)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/repository_trivy/>
- Official documentation: <https://aquasecurity.github.io/trivy/>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `trivy.yaml` (custom path can be defined with `REPOSITORY_TRIVY_CONFIG_FILE`)
- Rules configuration: <https://aquasecurity.github.io/trivy/latest/docs/configuration/>
- How to ignore files and directories: <https://aquasecurity.github.io/trivy/latest/docs/configuration/filtering/#by-inline-comments>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `REPOSITORY_TRIVY` to fully disable this linter
  - `REPOSITORY_TRIVY_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `REPOSITORY_TRIVY_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `REPOSITORY_TRIVY_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `REPOSITORY_TRIVY_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `REPOSITORY_TRIVY_ERROR_TOOMANYREQUESTS`
  - `REPOSITORY_TRIVY_ERROR_DB_DOWNLOAD_FAILED`
  - `REPOSITORY_TRIVY_ERROR_REGISTRY_UNAUTHORIZED`
<!-- generated-descriptor-info-end -->

## Fix instructions

In repository mode, trivy scans lockfiles (`package-lock.json`, `Gemfile.lock`, `Pipfile.lock`, `Cargo.lock`, etc.) for dependency vulnerabilities, IaC files for misconfigurations, and all files for hardcoded secrets. There is no auto-fix; handle each finding type as follows:

- **CVE in a dependency**: upgrade the affected package to the "Fixed Version" shown in the report, then refresh the lockfile:
  - npm/yarn: `npm install <pkg>@<fixed>` or `yarn upgrade <pkg>@<fixed>`
  - Python: bump the pin in `requirements.txt`/`pyproject.toml` and regenerate (`pipenv update <pkg>`, `poetry update <pkg>`, `uv lock`)
  - Ruby: `bundle update <pkg>`
  - Rust: `cargo update -p <pkg>`
- **CVE with no fixed version**: assess exploitability in your context; if acceptable, ignore it temporarily in `.trivyignore` with an `exp:` expiry date and re-evaluate when a patch ships.
- **IaC misconfiguration (AVD-xxx id)**: open the check's documentation link in the report and apply the recommended resource change (e.g. enable encryption, restrict the CIDR, add a `USER` instruction).
- **Secret finding**: rotate the credential immediately, remove it from the file, purge it from git history, and load it from a secret manager or environment variable instead.

## Inline disable

For Terraform, CloudFormation, Helm and Dockerfile files, place a `trivy:ignore:<check-id>` comment (using the format's line-comment token) directly above the resource; an expiry can be appended as `:exp:YYYY-MM-DD`:

```hcl
#trivy:ignore:AVD-AWS-0088
#trivy:ignore:aws-s3-enable-logging:exp:2026-12-31
resource "aws_s3_bucket" "example" {
  bucket = "example"
}
```

Inline ignores only work for checks tied to an existing resource, not for checks triggered by a missing resource or instruction.

## Ignore via configuration

Create a `.trivyignore` file at the repository root with one CVE/AVD/secret-rule id per line; append `exp:YYYY-MM-DD` to make the exception temporary, and use `#` comments to record the justification:

```text
# Not exploitable: dev-only dependency
CVE-2018-14618
# Accepted until patched upstream
CVE-2019-14697 exp:2026-12-31
AVD-DS-0002
```

In `trivy.yaml`, tune which scanners run and where the ignore file lives:

```yaml
scan:
  scanners:
    - vuln
    - secret
ignorefile: .trivyignore
```

## When disabling is legitimate

- The vulnerability is not exploitable in your context (vulnerable code path never reached, mitigating controls in place) — document why in a `.trivyignore` comment.
- The finding is in a dev-only or test-only dependency that never ships to production.
- No fixed version exists yet and the risk is formally accepted — always set an `exp:` date so the exception is re-assessed.
- The secret finding is a false positive (sample/placeholder value); prefer a scoped ignore over disabling the secret scanner.

Disabling the linter at MegaLinter level (`DISABLE_LINTERS` or `REPOSITORY_TRIVY_DISABLE_ERRORS`) is a last resort; prefer targeted ignores with documented justification.
