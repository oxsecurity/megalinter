# Fix REPOSITORY_DUSTILOCK errors

<!-- generated-descriptor-info-start -->
- Linter: **dustilock** (MegaLinter key: `REPOSITORY_DUSTILOCK`)
- Descriptor: **REPOSITORY** (other)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/repository_dustilock/>
- Official documentation: <https://github.com/Checkmarx/dustilock>
- Auto-fix support: no (errors must be fixed manually)
- Error line format (regex): `(error )`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `REPOSITORY_DUSTILOCK` to fully disable this linter
  - `REPOSITORY_DUSTILOCK_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `REPOSITORY_DUSTILOCK_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `REPOSITORY_DUSTILOCK_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `REPOSITORY_DUSTILOCK_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

dustilock scans `package.json` (npm) and `requirements.txt` (Python) files and reports any dependency name that is still available for public registration on the public registry — a supply-chain risk known as dependency confusion: an attacker could publish a malicious package under that name (with a higher version) and get it installed instead of your private package.

An error looks like:

```text
error - npm package "private-org-infra" is available for public registration. /path/to/package.json
```

For each reported package name, remediate as follows:

- If the name is a typo or a package that no longer exists, remove or correct the dependency entry.
- If it is a genuinely private/internal package, register a dummy placeholder package under the same name on the public registry (npmjs.com or PyPI) so nobody else can claim it — this is the mitigation recommended by the tool's documentation.
- For npm private packages, prefer a scoped name (`@your-org/package`) tied to your organization, which prevents public squatting of the bare name.
- Ensure your package manager resolves internal names only from your private registry (registry/scope configuration, index URLs) so a public package can never shadow the private one.

There is no auto-fix: the finding disappears once the name is claimed, corrected, or removed. Useful CLI flags (via the tuning variable for extra arguments): `-r` for a recursive scan, `-p <path>` to scan a custom path, and `-a` for audit-only mode, which reports findings without failing the run.

## Inline disable

dustilock has no inline suppression mechanism — there is no comment syntax to ignore a specific dependency in `package.json` or `requirements.txt`. The closest alternatives are fixing the finding (claim or rename the package), running in audit-only mode with `-a`, or excluding the file from the scan at MegaLinter level.

## Ignore via configuration

dustilock has no configuration file and no ignore file: its only tuning is done through CLI flags. To keep findings visible without blocking the build, pass audit mode through MegaLinter:

```yaml
REPOSITORY_DUSTILOCK_ARGUMENTS: "-a"
```

Note that dustilock runs in `project` CLI lint mode (called once on the whole repository), so per-file filtering with MegaLinter regex variables is not effective; use `-p <path>` to restrict the scanned directory if needed.

## When disabling is legitimate

- The flagged package is intentionally private and your organization has verified that installs can only resolve from the private registry (scoped packages, locked registry configuration), making public registration harmless.
- The flagged file is a test fixture or example manifest that references fake package names on purpose.
- You cannot claim the public name (e.g. registry naming policy) but compensating controls (lockfiles with integrity hashes, private-registry-only resolution) are in place.

Prefer fixing or claiming the package name, then audit-only mode (`-a`), then file/path restriction; disabling the linter at MegaLinter level is the last resort.
