---
name: fix-security-issue
description: Handle CVE/vulnerability reports from security linters (trivy, osv-scanner, etc.). Tries to upgrade first; ignores only when safe and justified; disables an unmaintained linter (with user confirmation) when a dangerous CVE has no fix.
allowed-tools: Read Grep Glob Edit Write Bash WebFetch WebSearch
argument-hint: "[CVE-ID or vulnerability description]"
model: opus
---

Investigate and fix the security issue `$ARGUMENTS` reported by trivy, osv-scanner, grype, or another security linter.

> **Delegation hint** — for non-trivial CVEs, delegate the applicability/exploitability analysis to the `security-analyst` agent (opus) and the mechanical version bump (once decided) to the `version-bumper` agent (haiku). This keeps deep reasoning on opus and pin edits on haiku, minimising token spend.

## Step 1 — Research the CVE

Browse the internet to gather full context:

- Visit the CVE URL from the scan output (e.g. `https://avd.aquasec.com/nvd/<cve-id>`)
- Check the fixed version, affected component, and attack vector
- Understand the exploit mechanism: what input/behavior triggers the vulnerability?

## Step 2 — Locate the vulnerable dependency

Find where the vulnerable package comes from:

- **Go binary** (e.g. `stdlib`): check which linter binary embeds it — the scan output names the file (e.g. `usr/bin/actionlint`). Find the linter's descriptor in `megalinter/descriptors/` and its pinned version.
- **Python package**: check `pyproject.toml`, `uv.lock`, `.config/python/dev/requirements.txt`, `server/requirements.txt`.
- **npm package** (direct): search descriptors for `npm:` blocks containing the package name.
- **npm package** (transitive): identify the top-level npm package that brings it in, then check its upstream changelog/release notes.
- **OS package** (Alpine apk): find the descriptor that installs it.

## Step 3 — Try to upgrade

Check whether a fixed version is available and reachable:

- For linter **binary** CVEs (Go stdlib, etc.): check if a newer release of the linter exists that was compiled with a fixed runtime. Look at GitHub releases.
- For **Python** packages: update the version pin in `pyproject.toml` / requirements files, then run `uv lock --python 3.12` to regenerate `uv.lock`.
- For **npm** packages (direct descriptor): bump the `ARG ..._VERSION=` line in the descriptor, then run `make megalinter-build`.
- For **npm** packages (transitive): upgrade the parent package to a version whose `package.json` lists a fixed transitive version.
- For **OS packages**: bump the apk package version in the descriptor if pinned.

If an upgrade is possible and available: **do it, then stop here.** No ignore entry needed.

## Step 4 — Assess impact when upgrade is not possible

If no fixed version exists yet (latest release is still affected), analyze whether the vulnerability is exploitable in MegaLinter's context:

Ask:
1. **How is the vulnerable code path triggered?** (e.g. parsing attacker-controlled input, making network requests, running a server)
2. **Does MegaLinter invoke that code path?** Linters run as static analysis tools — they read source files, they do not serve HTTP, process untrusted templates, or accept external network connections.
3. **What is the actual impact?** Consider:
   - DoS / resource exhaustion → generally not exploitable in a one-shot CI linter
   - Credential theft / data exfiltration → only relevant if the linter makes outbound connections or reads secrets from env
   - Arbitrary code execution → serious; check if the attack vector reaches the linter's execution environment

## Step 5 — Decide: block, ignore, or disable

**Stop and warn the user** if:
- The vulnerability involves credential theft, secret exposure, or supply-chain compromise
- The attack vector is reachable (e.g. a linter that fetches remote configs or calls an external API)
- The severity is CRITICAL and the exploit mechanism is not ruled out

**Add an exception** only when the CVE is genuinely not exploitable in MegaLinter's context. Acceptable reasons:
- DoS via crafted input that the linter never receives (e.g. `crypto/tls` in a tool that makes no TLS calls)
- Template/injection attack requiring untrusted user-controlled input that MegaLinter never passes
- Server-side vulnerability in a tool used only as a CLI client
- Debug/tooling CVE (e.g. `cilium-bugtool`) in a package imported only for its data types

**Consider disabling the linter** when the CVE is genuinely dangerous (reachable in MegaLinter's context, or CRITICAL with an exploit path you cannot rule out) **and** there is no upgrade path because the tool looks unmaintained or abandoned. Signals of abandonment:
- No commit / release on the source repo for 6+ months (check the linter's `linter_repo` on GitHub)
- The fixing version is never going to ship (archived repo, maintainer stepped away, issue open for a long time with no response)
- Upstream explicitly declined to fix, or the project is deprecated

When you judge that disabling is the right call, **ALWAYS ask the user first** via `AskUserQuestion` — never disable a linter autonomously. In the question, explain concretely:
- The CVE, its severity, and why it is reachable/dangerous here (not a routine unreachable-DoS ignore)
- The evidence of abandonment (e.g. "last commit 2024-01, no release in 14 months, fix requires vX.Y which does not exist")
- What disabling means for users (the linter stops running; another linter for the same language may still cover it)
- The alternative (keep it enabled with a documented ignore) so the user can choose

Only after the user confirms, disable it per Step 6.

## Step 6 — Add the exception

### `.trivyignore` (for trivy findings)

Append to the appropriate section (or create a new one):

```text
# <linter/package>: <one-line explanation of why not exploitable in MegaLinter>
CVE-XXXX-XXXXX
```

### `osv-scanner` config (for osv-scanner findings)

Check for an osv-scanner config file (e.g. `.osv-scanner.toml` or `osv-scanner.toml`) and add an ignore entry following its schema.

### General rule

Always include:
- The CVE ID
- A comment naming the affected package and the specific reason it is not exploitable
- A note if the ignore should be revisited (e.g. "remove when <linter> releases a version compiled with Go X.Y.Z")

### Disabling a linter (only after user confirmation in Step 5)

Edit the linter's entry in its `megalinter/descriptors/<lang>.megalinter-descriptor.yml` and add:

```yaml
  - linter_name: <tool>
    disabled: true
    disabled_reason: "Security: <CVE-ID> (<severity>) unpatched; upstream unmaintained (<evidence>). Re-enable when a fixed release ships. <advisory-url>"
```

Notes:
- `disabled` / `disabled_reason` are real descriptor properties (see e.g. `repository.megalinter-descriptor.yml` `kics`, disabled for a supply-chain compromise).
- After editing the descriptor, run `make megalinter-build` (NEVER `make megalinter-build-with-doc`) to regenerate Dockerfiles, test classes, and schemas.
- Disabling a linter **is** user-facing — add a `CHANGELOG.md` **Fixes** line per Step 7.
- Do NOT also add a `.trivyignore` entry for the same CVE: once the linter is disabled its image is no longer built/scanned, so an ignore would be dead weight. Ignore is the alternative to disabling, not a companion to it.

## Step 7 — Update CHANGELOG

Do **not** update `CHANGELOG.md` for:
- CVE ignore entries — not user-facing
- Linter version bumps — the auto-upgrade workflow owns **Linter versions upgrades**

If you made a real behavior change (e.g. a linter disabled due to a security incident, a config workaround added), add one line under **Fixes** in the beta section:
```text
- Fix <linter/component>: <what changed and why, one sentence for users>
```
