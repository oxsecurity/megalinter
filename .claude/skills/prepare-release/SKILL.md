---
name: prepare-release
description: Prepare a MegaLinter release — update CHANGELOG (prune empty sections, collapse linter versions, backfill PR numbers), run the release build, push commit and tag, and guide GitHub release creation.
allowed-tools: Bash Read Grep Glob Edit Write AskUserQuestion
argument-hint: "[vX.Y.Z]"
user-invocable: true
model: opus
---

Prepare a MegaLinter release.

## Step 1 — Resolve the version

Parse `$ARGUMENTS`. Validate against `^v[0-9]+\.[0-9]+\.[0-9]+$`. If absent or invalid:

```
AskUserQuestion: "What semver version should this release have? (format: vX.Y.Z)"
```

Call the resolved value `RELEASE_VERSION` (e.g. `v9.6.0`).

## Step 2 — Rewrite CHANGELOG.md

Read `CHANGELOG.md` in full. Identify the **Unreleased block**: everything from `## [Unreleased] (beta, main branch content)` down to (but not including) the next `## [` header. Everything before the `## [Unreleased]` line (the file preamble) is preserved verbatim.

### 2a — Capture section structure

Inside the Unreleased block, parse every **section header**: a line that starts with exactly `- ` (no indentation) followed by a section name, e.g. `- Breaking changes`, `- Linter versions upgrades (N)`. Capture them **in order** — this list drives the fresh Unreleased block in step 2e.

**Content items** are lines with exactly two-space indent: `  - …`.
**Sub-bullets** have more than two-space indent: `    - …` — never process these.

### 2b — Backfill PR numbers on section content lines

Determine the previous release tag:

```bash
git tag --sort=-creatordate | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | head -1
```

Build the commit map since that tag:

```bash
git log PREV_TAG..HEAD --oneline --no-merges
```

For every **content item** (`  - ` line) in every section **except** `Linter versions upgrades`:

1. **Skip** the line if it already contains `(#`, `#[0-9]`, or a `github.com` URL.
2. Extract 2–4 distinctive keywords from the line: linter names, descriptor IDs (e.g. `SWIFT_SWIFTLINT`), quoted identifiers, bare issue refs.
3. Search the commit map: `grep -i "KEYWORD"` for each keyword. Also run:
   ```bash
   gh pr list --state merged --search "KEYWORD in:title" --json number,title --limit 5
   ```
   for terms not found in commit subjects.
4. **Confident single match** → append ` (#N)` where N is the PR number.
5. **Multiple related matches** (same feature/fix) → append all: ` (#N1, #N2)`.
6. **No match or ambiguous** → leave line unchanged; add to an *unmatched lines* list shown at step 3.

Do not process sub-bullets (indent > 2 spaces) for PR backfill.

### 2c — Collapse the linter version lines

Collect every `  - ` line under the `- Linter versions upgrades` header, stopping at `<!-- linter-versions-end -->`. Each line has the format:

```
  - [name](url) from X to **Y** on YYYY-MM-DD
```

Parse with this pattern per line: `\[([^\]]+)\]\(([^)]+)\)\s+from\s+(\S+)\s+to\s+\*\*([^*]+)\*\*`

Group lines by linter `name`. For each group:

1. Collect all version strings that appear as `from X` or `to **Y**` across every line in the group.
2. Parse each version string as semver: split on `.`, pad with `.0` to reach three parts (e.g. `3.14` → `3.14.0`). Ignore any trailing non-numeric suffixes.
3. Find the **semver minimum** and **semver maximum** across the collected set (compare major, then minor, then patch).
4. Keep the URL from the first line for that linter.
5. Produce: `  - [name](url) from MIN to **MAX**` (no date).

Sort all produced lines **alphabetically by linter name** (case-insensitive). Count them → `N_LINTERS`.

Replace the section header with: `- Linter versions upgrades (N_LINTERS)`

### 2d — Prune empty sections from the released entry

A section is **empty** when its `- SectionName` header has no `  - ` content items before the next `- SectionName` or end of block. Remove empty sections entirely, including their surrounding blank lines.

Always keep `- Linter versions upgrades` regardless of line count.

### 2e — Assemble the new CHANGELOG.md

Build the file from four parts:

**Part 1 — File preamble** (unchanged):
Everything before the original `## [Unreleased]` line.

**Part 2 — Fresh Unreleased block:**

```
## [Unreleased] (beta, main branch content)

Note: Can be used with `oxsecurity/megalinter@beta` in your GitHub Action mega-linter.yml file, or with `oxsecurity/megalinter:beta` docker image

- Breaking changes

- Core

[... every section header captured in 2a, in original order, each followed by a blank line ...]

- Linter versions upgrades (0)
<!-- linter-versions-end -->

```

Use the **exact header text** captured in 2a (e.g. `- mega-linter-runner`, `- CI`). Every section is empty. Set the linter-versions count to `(0)`. Place `<!-- linter-versions-end -->` immediately after the `- Linter versions upgrades (0)` line with no blank line between them. Add one blank line after the marker before Part 3.

**Part 3 — Released entry:**

```
## [RELEASE_VERSION] - TODAY_DATE

- SectionA
  - item with PR (#N)
  - item with PR (#N1, #N2)

- SectionB
  - ...

- Linter versions upgrades (N_LINTERS)
  - [aardvark](url) from X to **Y**
  - [zebra](url) from X to **Y**
```

- Use today's date in `YYYY-MM-DD` format.
- Include only non-empty sections (step 2d), in their original order.
- PR numbers are backfilled (step 2b).
- Linter versions are collapsed and alpha-sorted (step 2c).
- **No** `Note:` line. **No** `<!-- linter-versions-end -->` marker.
- Add one blank line after this block before Part 4.

**Part 4 — Rest of file:**
Everything from the previous release's `## [v…] -` header to the end of file, verbatim.

Write the assembled content to `CHANGELOG.md`.

## Step 3 — Confirm the CHANGELOG

Show the diff:

```bash
git diff CHANGELOG.md
```

If the *unmatched lines* list (from step 2b) is non-empty, display it explicitly:

```
Lines where no PR was found — review and add manually if needed:
  - <line text>
  - <line text>
```

Ask:

> **AskUserQuestion**: "Is the updated CHANGELOG correct? Proceed to create the release?"
>
> Options: **Yes, proceed** / **No, let me edit it first**

If **No**: stop. The user edits `CHANGELOG.md` manually, then re-invokes `/prepare-release RELEASE_VERSION`.

## Step 4 — Confirm deploy-BETA-linters was run

Ask:

> **AskUserQuestion**: "Did you manually run the **deploy-BETA-linters** GitHub Actions workflow and confirm it completed successfully? The release workflow reuses the BETA linter images — the release will be incomplete if those images have not been built."
>
> Options: **Yes, it completed successfully** / **No / not sure**

If **No / not sure**: stop. Guide the user:

1. Trigger: `gh workflow run deploy-BETA-linters.yml` (or GitHub UI → Actions → **Deploy BETA linters** → Run workflow).
2. Wait for it to finish green.
3. Re-invoke `/prepare-release RELEASE_VERSION`.

## Step 5 — Run the release build

Warn the user: this step regenerates all documentation and Dockerfiles and may take several minutes.

```bash
make megalinter-release RELEASE_VERSION=RELEASE_VERSION
```

The Makefile activates the venv automatically. This runs:
- `build.sh --doc --version RELEASE_VERSION` — regenerates docs/Dockerfiles stamped with the release version.
- `build.sh --release RELEASE_VERSION` — stages all changed files, creates commit `"Release MegaLinter RELEASE_VERSION"`, and creates a git tag `RELEASE_VERSION`.

Do not run `make megalinter-build-with-doc` separately.

If the command fails, show the error output and stop.

## Step 6 — Confirm before pushing

Show what will be pushed:

```bash
git log -1 --oneline
git tag --sort=-creatordate | head -1
```

Ask:

> **AskUserQuestion**: "Release commit and tag are ready. Push to origin now?"
>
> Options: **Yes, push** / **No, I'll push manually**

If **Yes**:

```bash
BRANCH="$(git branch --show-current)"
git push origin "$BRANCH"
git push origin RELEASE_VERSION
```

> **Main-push exception**: pushing to `main` is the one authorized exception to the global "never push to main" rule in CLAUDE.md. MegaLinter releases are always cut from `main`, and the release commit must land there. This skill explicitly owns this exception.

## Step 7 — Guide GitHub release creation

Tell the user:

1. Open: `https://github.com/oxsecurity/megalinter/releases/new?tag=RELEASE_VERSION`
2. Set the release **title** to `RELEASE_VERSION`.
3. Paste **Part 3** from step 2e (the released CHANGELOG section, starting at `## [RELEASE_VERSION]`) as the release description.
4. Tick **"Set as the latest release"**.
5. Click **"Publish release"**.

## Step 8 — Remind about pending workflows

Tell the user:

- The push and tag trigger **deploy-RELEASE**, **deploy-RELEASE-linters**, and **deploy-RELEASE-flavors** workflows.
- Go to **GitHub → Actions** and approve any runs awaiting manual approval.
- Monitor those three workflows until they all complete green before announcing the release publicly.
