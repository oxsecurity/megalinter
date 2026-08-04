# Fix REPOSITORY_SYFT errors

<!-- generated-descriptor-info-start -->
- Linter: **syft** (MegaLinter key: `REPOSITORY_SYFT`)
- Descriptor: **REPOSITORY** (other)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/repository_syft/>
- Official documentation: <https://github.com/anchore/syft>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.syft.yaml` (custom path can be defined with `REPOSITORY_SYFT_CONFIG_FILE`)
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `REPOSITORY_SYFT` to fully disable this linter
  - `REPOSITORY_SYFT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `REPOSITORY_SYFT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `REPOSITORY_SYFT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `REPOSITORY_SYFT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

syft is not a code-quality linter: it generates a Software Bill of Materials (SBOM) inventorying the
packages and dependencies found in the repository (`syft scan` over the whole project, JSON output).
It has no rules and no auto-fix; a failure means syft itself could not complete the scan, not that the
code is wrong. Remediation flow:

- Read the syft error message in the MegaLinter log to identify the failing step (config parsing, file access, cataloger crash).
- If the configuration file is rejected, validate its YAML syntax and keys against the configuration reference (<https://oss.anchore.com/docs/reference/syft/configuration/>).
- If a specific path or artifact makes the scan fail (corrupt archive, huge vendored tree), exclude it with `--exclude` glob patterns or the `exclude` config key, then re-run.
- For directory scans, exclusion globs must start with `./`, `*/` or `**/` (resolved relative to the scanned directory); absolute paths like `/etc` only work when scanning images.
- Reproduce locally with `syft scan . -o json` (any setting can also be passed as a `SYFT_*` environment variable, e.g. `SYFT_PARALLELISM`).
- If a package ecosystem cataloger misbehaves, restrict catalogers via the `catalogers` / `select-catalogers` config keys instead of disabling the whole scan.

## Inline disable

syft has no inline suppression mechanism: it inventories files and packages, it does not evaluate
rules that could be disabled with a code comment. The closest alternative is excluding paths from the
scan, either on the command line or in the configuration file:

```bash
syft scan . --exclude './out/**/*.json' --exclude './vendor/**'
```

## Ignore via configuration

Use the `exclude` key of the configuration file (searched in `./.syft.yaml`, `./.syft/config.yaml`,
`~/.syft.yaml`, then `$XDG_CONFIG_HOME/syft/config.yaml`) to remove paths from the SBOM, and the
cataloger keys to control which package ecosystems are scanned:

```yaml
exclude:
  - "./node_modules/**"
  - "**/*.tmp"

catalogers:
  - golang
  - python
```

There is no separate ignore file; all filtering goes through the configuration file or `--exclude`
arguments. Note that MegaLinter runs syft in project mode, so `FILTER_REGEX_EXCLUDE`-style variables
do not reduce what syft scans — only syft's own exclusions do.

## When disabling is legitimate

- The repository contains no distributable software (pure documentation or infrastructure repos) and an SBOM brings no value.
- Another pipeline stage already produces the authoritative SBOM (e.g. syft/grype on the built container image, which is more accurate than a source scan).
- A cataloger crashes on a file that cannot be excluded and no fixed syft release is available yet — prefer `REPOSITORY_SYFT_DISABLE_ERRORS` to keep the report visible.
- Vendored or generated dependency trees produce a misleading inventory that path exclusions cannot cleanly separate.

Disabling the linter at MegaLinter level (`DISABLE_LINTERS`) is the last resort: prefer path
exclusions and cataloger selection in the syft configuration first.
