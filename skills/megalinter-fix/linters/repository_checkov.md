# Fix REPOSITORY_CHECKOV errors

<!-- generated-descriptor-info-start -->
- Linter: **checkov** (MegaLinter key: `REPOSITORY_CHECKOV`)
- Descriptor: **REPOSITORY** (other)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/repository_checkov/>
- Official documentation: <https://www.checkov.io/>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.checkov.yml` (custom path can be defined with `REPOSITORY_CHECKOV_CONFIG_FILE`)
- Rules index: <https://www.checkov.io/5.Policy%20Index/all.html>
- Rules configuration: <https://github.com/bridgecrewio/checkov#configuration-using-a-config-file>
- How to disable rules inline: <https://www.checkov.io/2.Basics/Suppressing%20and%20Skipping%20Policies.html>
- Error line format (regex): `, Failed checks: ([0-9]+), Skipped checks`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `REPOSITORY_CHECKOV` to fully disable this linter
  - `REPOSITORY_CHECKOV_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `REPOSITORY_CHECKOV_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `REPOSITORY_CHECKOV_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `REPOSITORY_CHECKOV_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

checkov is a static security scanner for infrastructure-as-code: it evaluates Terraform, CloudFormation, Kubernetes, Helm, Dockerfile, serverless and secrets against policies identified by IDs such as `CKV_AWS_20`. There is no auto-fix: remediate by editing the flagged resource.

- Look up each reported check ID in the policy index to understand the misconfiguration it detects.
- Harden the flagged resource rather than suppressing: typical fixes are enabling encryption, blocking public access, restricting overly permissive IAM/security-group rules, enforcing HTTPS/TLS, enabling logging or versioning, and pinning image versions in Dockerfiles.
- For secrets findings, remove the hardcoded credential from the file, rotate it, and load it from a secret store or environment variable instead.
- Re-run the scan until `Failed checks` reaches 0; fix every failed check ID, not only the first one reported.

## Inline disable

Add a `checkov:skip` comment inside the scope of the resource block, with the check ID and a justification.

```hcl
resource "aws_s3_bucket" "foo-bucket" {
  region = var.region
  #checkov:skip=CKV_AWS_20:The bucket is a public static content host
  bucket = local.bucket_name
}
```

In a Dockerfile the comment can be placed anywhere in the file (e.g. `#checkov:skip=CKV_DOCKER_5: reason`). For Kubernetes manifests, use an annotation of the form `checkov.io/skip#: <check_id>=<comment>`. For secrets findings, place the comment directly before, after, or on the flagged line.

## Ignore via configuration

Declare skipped checks or excluded paths in the configuration file. CLI equivalents (`--skip-check`, `--check`, `--skip-path`) can also be passed through the arguments variable; `--skip-check` accepts wildcards like `CKV_AWS*`.

```yaml
skip-check:
  - CKV_DOCKER_2
  - CKV_DOCKER_3
skip-path:
  - "examples/.*"
quiet: true
```

There is no dedicated ignore file: use `skip-path` regexes to exclude directories such as vendored modules or test fixtures.

## When disabling is legitimate

- The flagged resource is intentionally non-compliant, e.g. an S3 bucket that must be public because it hosts a static website: skip inline with a justification comment.
- The finding is in example, test-fixture, or vendored third-party IaC that you do not maintain: exclude it with `skip-path`.
- A policy does not apply to your platform or compliance scope (e.g. a cloud-provider check for a provider you do not use): add it to `skip-check`.
- The check is a false positive on dynamically resolved values (variables or modules checkov cannot evaluate): suppress the specific check ID inline, never wholesale.
- Disabling the linter at MegaLinter level is the last resort: prefer inline skips or configuration-level exclusions scoped to specific checks and paths.
