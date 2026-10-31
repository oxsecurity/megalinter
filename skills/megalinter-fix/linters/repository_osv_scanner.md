# Fix REPOSITORY_OSV_SCANNER errors

<!-- generated-descriptor-info-start -->
- Linter: **osv-scanner** (MegaLinter key: `REPOSITORY_OSV_SCANNER`)
- Descriptor: **REPOSITORY** (other)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/repository_osv_scanner/>
- Official documentation: <https://google.github.io/osv-scanner/>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `osv-scanner.toml` (custom path can be defined with `REPOSITORY_OSV_SCANNER_CONFIG_FILE`)
- Rules configuration: <https://google.github.io/osv-scanner/configuration/>
- How to ignore files and directories: <https://google.github.io/osv-scanner/usage/scan-source#ignored-files>
- Error line format (regex): `(osv\.dev/GHSA-)`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `REPOSITORY_OSV_SCANNER` to fully disable this linter
  - `REPOSITORY_OSV_SCANNER_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `REPOSITORY_OSV_SCANNER_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `REPOSITORY_OSV_SCANNER_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `REPOSITORY_OSV_SCANNER_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `REPOSITORY_OSV_SCANNER_ERROR_SERVICE_UNAVAILABLE`
  - `REPOSITORY_OSV_SCANNER_ERROR_NO_PACKAGE_SOURCES`
  - `REPOSITORY_OSV_SCANNER_ERROR_LOCKFILE_PARSE`
<!-- generated-descriptor-info-end -->

## Fix instructions

osv-scanner is a dependency vulnerability scanner: it matches lockfiles (package-lock.json, Cargo.lock, requirements.txt...), SBOMs and git directories against the OSV.dev database. Findings are known vulnerabilities (GHSA/CVE/GO ids) in dependencies, not code-style issues.

Remediation flow, in order of preference:

1. Upgrade the vulnerable dependency to the fixed version reported in the advisory, then regenerate the lockfile (`npm install`, `cargo update -p <crate>`, `uv lock`...).
2. If the vulnerability is in a transitive dependency, bump the direct dependency that pulls it in, or force a resolution/override in the manifest.
3. Use osv-scanner's own guided remediation (experimental) when supported:

   ```bash
   osv-scanner fix --strategy=in-place -L path/to/package-lock.json   # npm lockfile
   osv-scanner fix --strategy=relax -M package.json -L package-lock.json
   osv-scanner fix --strategy=override -M path/to/pom.xml             # Maven
   ```

4. If no fixed version exists, verify exploitability (is the vulnerable function even reachable?) and ignore the advisory in the configuration file with a `reason` and an expiry date.

## Inline disable

osv-scanner scans lockfiles and manifests, so there is no inline (in-code) suppression syntax. The only suppression mechanism is the TOML configuration file described below.

## Ignore via configuration

Place the configuration file in the scanned directory (it does not cascade to subdirectories; a custom path can be forced with `--config=<path>`). Ignore a specific vulnerability:

```toml
[[IgnoredVulns]]
id = "GHSA-xxxx-xxxx-xxxx"
ignoreUntil = 2026-12-31  # optional expiry date
reason = "Vulnerable code path not reachable; no fix released yet"
```

Ignoring a vulnerability also ignores its aliases (e.g. the matching CVE id). Ignore an entire package instead:

```toml
[[PackageOverrides]]
name = "lib"
version = "1.0.0"   # optional; all configured fields must match
ecosystem = "npm"
ignore = true       # or vulnerability.ignore = true
effectiveUntil = 2026-12-31
reason = "Dev-only tooling, not shipped"
```

There is no dedicated ignore file for paths: by default osv-scanner already skips files matched by `.gitignore` (override with `--no-ignore`). Skip extra directories with `--experimental-exclude` (exact, `g:` glob or `r:` regex patterns), passed through the extra-arguments tuning variable.

## When disabling is legitimate

- No fixed version has been released yet: ignore the advisory with `ignoreUntil` set to a near review date, so the exception expires instead of rotting.
- The vulnerable function is not reachable from your code (confirmed, e.g. via `--call-analysis=all` for Go): record that in `reason`.
- The finding targets a dev-only or test-only dependency group that never ships to production: use a `PackageOverrides` entry scoped with `group`.
- Vendored or third-party sample lockfiles kept as test fixtures: exclude their path rather than ignoring the vulnerability globally.

Always prefer a scoped, dated, justified entry in the TOML configuration; disabling the linter at MegaLinter level is the last resort.
