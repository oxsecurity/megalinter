# Fix REPOSITORY_GRYPE errors

<!-- generated-descriptor-info-start -->
- Linter: **grype** (MegaLinter key: `REPOSITORY_GRYPE`)
- Descriptor: **REPOSITORY** (other)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/repository_grype/>
- Official documentation: <https://github.com/anchore/grype>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.grype.yaml` (custom path can be defined with `REPOSITORY_GRYPE_CONFIG_FILE`)
- Rules index: <https://github.com/anchore/grype#vulnerability-summary>
- Rules configuration: <https://github.com/anchore/grype#configuration>
- Error line format (regex): `(Low|Medium|High|Critical)`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `REPOSITORY_GRYPE` to fully disable this linter
  - `REPOSITORY_GRYPE_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `REPOSITORY_GRYPE_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `REPOSITORY_GRYPE_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `REPOSITORY_GRYPE_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `REPOSITORY_GRYPE_ERROR_DB_UPDATE_FAILED`
  - `REPOSITORY_GRYPE_ERROR_DB_CORRUPT`
  - `REPOSITORY_GRYPE_ERROR_TLS_TIMEOUT`
<!-- generated-descriptor-info-end -->

## Fix instructions

grype is a vulnerability scanner: it matches OS packages and language dependencies (npm, pip, gem, Java, Go, .NET, PHP, Rust...) found in the repository against known CVE databases. Findings are vulnerable dependency versions, not code-style issues, so the remediation flow is:

- Identify the vulnerable package, its installed version and the fixed version in the report line.
- Upgrade the dependency to a fixed version in the relevant manifest (`package.json`, `requirements.txt`, `go.mod`, `pom.xml`...), then regenerate the lock file. Prefer the smallest upgrade that reaches the fixed version.
- For transitive dependencies, upgrade the direct parent that pulls them in, or pin/override the transitive version with your package manager's resolution mechanism.
- For vulnerabilities in vendored files or container base images referenced by the repo, rebuild from an updated base or re-vendor a patched release.
- When a finding has no available fix, either wait (track it) or suppress it with an ignore rule scoped to that CVE (see below). To only fail on fixable findings, pass `--only-fixed`; to raise the blocking threshold, pass `--fail-on <severity>` (negligible, low, medium, high, critical) via the linter arguments variable.
- If a finding is proven not exploitable in context, document it in an OpenVEX document and pass it with `--vex <file>` so grype filters it out with an auditable justification.

grype has no auto-fix command: remediation is always a manual dependency upgrade.

## Inline disable

grype scans dependency manifests and artifacts, so there is no inline comment suppression syntax. The closest alternatives are `ignore` rules in the configuration file (see below) or an OpenVEX document passed with `--vex`.

## Ignore via configuration

Add `ignore` rules to the configuration file. A match is suppressed when it meets all criteria of any rule; every field is optional, so scope rules as narrowly as possible:

```yaml
ignore:
  # Ignore one CVE only while no fix exists
  - vulnerability: CVE-2008-4318
    fix-state: unknown
    package:
      name: libcurl
      version: 1.5.1
      type: npm
      location: "/usr/local/lib/node_modules/**"
  # Ignore a CVE everywhere (use sparingly)
  - vulnerability: CVE-2014-54321
```

Valid `fix-state` values: `fixed`, `not-fixed`, `wont-fix`, `unknown`. VEX-based rules use `vex-status: not_affected` with a `vex-justification` such as `vulnerable_code_not_present`.

Exclude paths from scanning with glob patterns in the same file:

```yaml
exclude:
  - './tests/fixtures/**'
  - './out/**/*.json'
```

Equivalent global filters also exist as config keys: `only-fixed: true`, `fail-on-severity: high`.

## When disabling is legitimate

- The vulnerability has no released fix (`fix-state: not-fixed` or `wont-fix`): add a narrowly scoped ignore rule and revisit when a fix ships.
- The vulnerable code path is not reachable in your usage, ideally documented via a VEX statement (`not_affected` with a justification) rather than a bare ignore.
- The match is a false positive (wrong package identification, e.g. a name collision across ecosystems): ignore it scoped to package name, type and location, and consider reporting it upstream.
- Test fixtures or vendored sample data intentionally contain old dependency manifests: exclude those paths with `exclude` globs.

Always prefer a scoped ignore rule in the grype configuration over weakening MegaLinter itself; disabling at MegaLinter level (`DISABLE_LINTERS` / `_DISABLE_ERRORS`) is the last resort.
