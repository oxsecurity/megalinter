# Fix REPOSITORY_TRIVY_SBOM errors

<!-- generated-descriptor-info-start -->
- Linter: **trivy-sbom** (MegaLinter key: `REPOSITORY_TRIVY_SBOM`)
- Descriptor: **REPOSITORY** (other)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/repository_trivy_sbom/>
- Official documentation: <https://aquasecurity.github.io/trivy/>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `trivy-sbom.yaml` (custom path can be defined with `REPOSITORY_TRIVY_SBOM_CONFIG_FILE`)
- Rules configuration: <https://aquasecurity.github.io/trivy/latest/docs/configuration/>
- How to ignore files and directories: <https://aquasecurity.github.io/trivy/latest/docs/configuration/filtering/#by-inline-comments>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `REPOSITORY_TRIVY_SBOM` to fully disable this linter
  - `REPOSITORY_TRIVY_SBOM_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `REPOSITORY_TRIVY_SBOM_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `REPOSITORY_TRIVY_SBOM_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `REPOSITORY_TRIVY_SBOM_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `REPOSITORY_TRIVY_SBOM_ERROR_TOOMANYREQUESTS`
  - `REPOSITORY_TRIVY_SBOM_ERROR_DB_DOWNLOAD_FAILED`
<!-- generated-descriptor-info-end -->

## Fix instructions

This linter does not report code-style errors: it runs `trivy fs --format cyclonedx .` to
generate a CycloneDX Software Bill of Materials of the repository (in CycloneDX mode Trivy
disables security scanning, so failures are generation problems, not vulnerabilities). When
it fails:

- Read the Trivy error message in the log first; it names the file or subsystem that broke.
- Fix or regenerate any corrupt/unparsable lockfile or manifest it points at (for example
  re-run the package manager to rebuild `package-lock.json`, `poetry.lock`, `go.sum`...).
- Exclude vendored or third-party trees Trivy cannot parse with `scan.skip-dirs` /
  `scan.skip-files` (see below) instead of deleting them.
- For DB download or `TOOMANYREQUESTS` failures, follow the resolutions of the known error
  patterns listed above (retry, authenticate registry pulls, mirror the DB via
  `TRIVY_DB_REPOSITORY`, or pre-populate the Trivy cache in CI).
- Reproduce locally with `trivy fs --format cyclonedx .` at the repository root to iterate
  faster than through MegaLinter.

## Inline disable

There is no inline suppression for SBOM generation: the run produces an inventory, not
per-line findings. Trivy's inline comments (`#trivy:ignore:<rule-id>` above a resource,
e.g. `#trivy:ignore:AVD-GCP-0051` in Terraform) only apply to misconfiguration scanning of
Terraform, CloudFormation, Helm and Dockerfile files, so they have no effect here. Use the
configuration exclusions below instead.

## Ignore via configuration

Trivy reads any CLI option from its YAML configuration file (CLI flags take precedence over
the file). To keep problematic paths out of the SBOM scan:

```yaml
scan:
  skip-dirs:
    - vendor
    - node_modules
  skip-files:
    - "generated/schema.lock"
```

Trivy also supports a `.trivyignore` file (one `CVE-...`/`AVD-...` ID per line, optional
`exp:YYYY-MM-DD` expiry) and a structured `.trivyignore.yaml` (passed with `--ignorefile`),
but those filter security findings and are not useful in pure SBOM mode.

## When disabling is legitimate

- The repository vendors third-party or generated dependency trees whose manifests Trivy
  cannot parse; prefer `scan.skip-dirs` over disabling the whole linter.
- SBOM generation is already handled by another supply-chain tool in the pipeline and a
  second CycloneDX artifact is redundant.
- The CI environment is air-gapped and cannot reach a Trivy DB mirror, making every run
  fail for environmental reasons.

Disabling the linter at MegaLinter level is the last resort: exclude paths in the Trivy
configuration first.
