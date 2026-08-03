# MegaLinter performance improvement playbook

Load this guide when a run reports slow linters (see the thresholds in the check skill). Suggestions are **informational**: present them to the user with the measured times; apply a change only after the user agrees. Re-measure on the next run to confirm the gain.

## Known slow-linter causes and remedies

| Symptom                                                           | Cause                                                                                               | Remedy                                                                                                                                              |
|:------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------|
| `REPOSITORY_GRYPE` or `REPOSITORY_TRIVY` takes 1-3 minutes        | Vulnerability DB downloaded on every CI run                                                         | Cache the DB between runs: `actions/cache` on a workspace folder + `GRYPE_DB_CACHE_DIR` (grype) or `TRIVY_CACHE_DIR` (trivy) pointing to it         |
| Several security scanners each take significant time              | `REPOSITORY_TRIVY`, `REPOSITORY_GRYPE`, `REPOSITORY_OSV_SCANNER` largely overlap on dependency CVEs | Suggest keeping the fastest (osv-scanner is usually seconds) plus one deep scanner, and adding the others to `DISABLE_LINTERS` — user's call        |
| `SPELL_LYCHEE` takes minutes                                      | It checks every external URL of every file over the network                                         | Enable `cache = true` in `lychee.toml`; exclude folders whose links are already curated (`SPELL_LYCHEE_FILTER_REGEX_EXCLUDE`)                       |
| `REPOSITORY_SECRETLINT` slow on big repos                         | It scans every file, including documentation                                                        | Add bulky folders and `**/*.md` to `.secretlintignore` when other secret scanners (gitleaks-like, trufflehog...) already cover them                 |
| `COPYPASTE_JSCPD` slow or noisy                                   | Scanning generated/templated files that are similar by design                                       | Add those folders to the `ignore` list of `.jscpd.json`                                                                                             |
| `REPOSITORY_CHECKOV` takes minutes                                | It scans every IaC framework it can find                                                            | Limit with `--framework` in `REPOSITORY_CHECKOV_ARGUMENTS` to the frameworks actually used                                                          |
| Many linters each spend time on the same vendored/generated files | No global exclusion                                                                                 | Add vendored/generated/build folders to `FILTER_REGEX_EXCLUDE` or `ADDITIONAL_EXCLUDED_DIRECTORIES`                                                 |
| Whole run slow, many irrelevant linters                           | `all` flavor used on a single-stack repository                                                      | Set `MEGALINTER_FLAVOR` to the matching [flavor](https://megalinter.io/flavors/), or build a [custom flavor](https://megalinter.io/custom-flavors/) |
| A single linter dominates and is not valued by the team           | —                                                                                                   | Suggest `DISABLE_LINTERS` (requires user confirmation, like any disable)                                                                            |

## How to present findings

Give the user a short table of the slowest linters with their measured time and the matching remedy, for example:

```text
Performance report (total lint: 4m10s):
- SPELL_LYCHEE      118s → enable lychee cache, exclude curated docs folders
- REPOSITORY_GRYPE  116s → cache the vulnerability DB in CI (actions/cache + GRYPE_DB_CACHE_DIR)
Apply any of these? (none is failing — purely a speed win)
```
