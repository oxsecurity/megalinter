---
name: fix-security-issue
description: Handle CVE/vulnerability reports from security linters (trivy, osv-scanner, etc.). Tries to upgrade first; ignores only when safe and justified.
allowed-tools: Read Grep Glob Edit Write Bash WebFetch WebSearch
argument-hint: "[CVE-ID or vulnerability description]"
---

Investigate and fix the security issue `$ARGUMENTS` reported by trivy, osv-scanner, or another security linter.

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

## Step 5 — Decide: block or ignore

**Stop and warn the user** if:
- The vulnerability involves credential theft, secret exposure, or supply-chain compromise
- The attack vector is reachable (e.g. a linter that fetches remote configs or calls an external API)
- The severity is CRITICAL and the exploit mechanism is not ruled out

**Add an exception** only when the CVE is genuinely not exploitable in MegaLinter's context. Acceptable reasons:
- DoS via crafted input that the linter never receives (e.g. `crypto/tls` in a tool that makes no TLS calls)
- Template/injection attack requiring untrusted user-controlled input that MegaLinter never passes
- Server-side vulnerability in a tool used only as a CLI client
- Debug/tooling CVE (e.g. `cilium-bugtool`) in a package imported only for its data types

## Step 6 — Add the exception

### `.trivyignore` (for trivy findings)

Append to the appropriate section (or create a new one):

```
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

## Step 7 — Update CHANGELOG

Do **not** update `CHANGELOG.md` for:
- CVE ignore entries — not user-facing
- Linter version bumps — the auto-upgrade workflow owns **Linter versions upgrades**

If you made a real behavior change (e.g. a linter disabled due to a security incident, a config workaround added), add one line under **Fixes** in the beta section:
```
- Fix <linter/component>: <what changed and why, one sentence for users>
```
