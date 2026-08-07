# MegaLinter performance improvement playbook

Load this guide when a run reports slow linters (see the thresholds in the check skill). Suggestions are **informational**: present them to the user with the measured times; apply a change only after the user agrees. Re-measure on the next run to confirm the gain.

Before hand-tuning with the table below, consider a prerun analysis (`npx mega-linter-runner --prerun`, MegaLinter v10 or beta): it computes exclusion and flavor suggestions from the actual file collection - see "First local run: prerun analysis" in the check skill.

## Known slow-linter causes and remedies

| Symptom                                                                                              | Cause                                                                                                                                                                | Remedy                                                                                                                                                              |
|:-----------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `REPOSITORY_GRYPE` or `REPOSITORY_TRIVY` takes 1-3 minutes                                           | Vulnerability DB downloaded on every CI run                                                                                                                          | Cache the DB between runs: `actions/cache` on a workspace folder + `GRYPE_DB_CACHE_DIR` (grype) or `TRIVY_CACHE_DIR` (trivy) pointing to it                         |
| Several security scanners each take significant time                                                 | `REPOSITORY_TRIVY`, `REPOSITORY_GRYPE`, `REPOSITORY_OSV_SCANNER` largely overlap on dependency CVEs                                                                  | Suggest keeping the fastest (osv-scanner is usually seconds) plus one deep scanner, and adding the others to `DISABLE_LINTERS` — user's call                        |
| `SPELL_LYCHEE` takes minutes                                                                         | It checks every external URL of every file over the network                                                                                                          | Enable `cache = true` in `lychee.toml`; exclude folders whose links are already curated (`SPELL_LYCHEE_FILTER_REGEX_EXCLUDE`)                                       |
| `REPOSITORY_SECRETLINT` slow on big repos                                                            | It scans every file, including documentation                                                                                                                         | Add bulky folders and `**/*.md` to `.secretlintignore` when other secret scanners (gitleaks-like, trufflehog...) already cover them                                 |
| `COPYPASTE_JSCPD` slow or noisy                                                                      | Scanning generated/templated files that are similar by design                                                                                                        | Add those folders to the `ignore` list of `.jscpd.json`                                                                                                             |
| `REPOSITORY_CHECKOV` takes minutes                                                                   | It scans every IaC framework it can find                                                                                                                             | Limit with `--framework` in `REPOSITORY_CHECKOV_ARGUMENTS` to the frameworks actually used                                                                          |
| `REPOSITORY_CHECKOV` very slow or stalled, `git cat-file` children visible                           | Its default `secrets` framework duplicates dedicated secret scanners (gitleaks, trufflehog...) and reads git objects file by file                                    | Add `--skip-framework` + `secrets` to `REPOSITORY_CHECKOV_ARGUMENTS` when another secret scanner is active (recent MegaLinter versions apply this automatically)    |
| Many linters each spend time on the same vendored/generated files                                    | No global exclusion                                                                                                                                                  | Add vendored/generated/build folders to `FILTER_REGEX_EXCLUDE` or `ADDITIONAL_EXCLUDED_DIRECTORIES`                                                                 |
| Whole run slow, many irrelevant linters                                                              | `all` flavor used on a single-stack repository                                                                                                                       | Set `MEGALINTER_FLAVOR` to the matching [flavor](https://megalinter.io/flavors/), or build a [custom flavor](https://megalinter.io/custom-flavors/)                 |
| A single linter dominates and is not valued by the team                                              | —                                                                                                                                                                    | Suggest `DISABLE_LINTERS` (requires user confirmation, like any disable)                                                                                            |
| A project-mode linter behaves unexpectedly after an upgrade                                          | Automatic excluded-directories forwarding (see below) conflicts with the repo's own ignore/config                                                                    | Disable forwarding for that linter with `<LINTER_KEY>_FORWARD_EXCLUDED_DIRECTORIES: false`                                                                          |
| Local run saturates the machine, or every linter is slow at once                                     | MegaLinter runs one parallel linter process per CPU core (`PARALLEL_PROCESS_NUMBER` default), so a local run competes with Docker and everything else on the machine | Cap it on local runs with `-e PARALLEL_PROCESS_NUMBER=4` (the check skill's default for local mode); keep it out of `.mega-linter.yml` so CI keeps full parallelism |
| On Windows, local run stalls right after file collection; container up for hours with seconds of CPU | Repo bind-mounted from a Windows path into a WSL2-backed engine: every file access crosses the Windows/WSL2 boundary                                                 | See "Windows bind-mount slowness" below                                                                                                                             |

## Windows bind-mount slowness (WSL2-backed engines)

Mounting a repository from a Windows filesystem path (`C:\...`) into a container engine backed by WSL2 (Docker Desktop on Windows, `podman machine`) makes filesystem-heavy operations dramatically slower than on Linux/macOS - sometimes pathologically, to the point of looking hung. MegaLinter itself runs a git-based gitignore detection (`git ls-files`) on the workspace before any linter starts, so the run can stall right at the file-collection phase; linters that walk many files or the git history (secret scanners especially) hit the same wall. Recent MegaLinter versions bound that internal git call with a timeout and degrade gracefully; older pinned `MEGALINTER_VERSION` values can hang there indefinitely.

Symptoms: the run appears frozen just after "...collects the files to analyse"; `<engine> exec <name> ps aux` shows negligible cumulative CPU time against a long container uptime (the stall checklist in the check skill's local mode).

Mitigations to propose to the user:

- Keep the repo on a WSL2-native filesystem path (a clone inside the WSL2 distro) rather than a Windows-mounted one when running many local MegaLinter checks.
- Verify antivirus/EDR real-time scanning excludes the engine's VM disk and the repo folder.
- If local runs keep proving unreliable on that host, prefer watch mode (CI does the work) instead of repeatedly fighting local mode.

## Automatic excluded-directories forwarding

MegaLinter forwards `EXCLUDED_DIRECTORIES` + `ADDITIONAL_EXCLUDED_DIRECTORIES` (plus directories identified from `FILTER_REGEX_EXCLUDE`) to linters running in `project` CLI lint mode, so they stop crawling folders like `node_modules`, `.git` or build caches. Depending on the linter this is done by:

- appending the tool's native exclusion arguments (e.g. trivy `--skip-dirs`, grype/syft `--exclude`, checkov `--skip-path`)
- generating an ignore file or a config file into the report folder that merges or extends the one resolved from the repository (e.g. trufflehog, prettier, jscpd, yamllint, rubocop, swiftlint, betterleaks)

Each forwarded exclusion is traced in the linter's console log with an `[Excluded directories]` line, so a generated file or extra argument is always visible in the run output.

Disable it when it causes issues, or when the repository already maintains up-to-date ignore/config files for its linters (making the merge redundant):

- globally: `FORWARD_EXCLUDED_DIRECTORIES: false` in `.mega-linter.yml`
- for one linter only: `<LINTER_KEY>_FORWARD_EXCLUDED_DIRECTORIES: false` (e.g. `REPOSITORY_TRIVY_FORWARD_EXCLUDED_DIRECTORIES: false`)

Like any performance change, propose the disable to the user first; point at the `[Excluded directories]` log lines of the affected linter as evidence.

## How to present findings

Give the user a short table of the slowest linters with their measured time and the matching remedy, for example:

```text
Performance report (total lint: 4m10s):
- SPELL_LYCHEE      118s → enable lychee cache, exclude curated docs folders
- REPOSITORY_GRYPE  116s → cache the vulnerability DB in CI (actions/cache + GRYPE_DB_CACHE_DIR)
Apply any of these? (none is failing — purely a speed win)
```
