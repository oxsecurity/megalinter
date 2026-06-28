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

The mechanical transformation is done by the bundled helper script
`.claude/skills/prepare-release/prepare_changelog.py` (stdlib only, no venv needed). It:

- converts the `## [Unreleased]` block into a dated `## [RELEASE_VERSION] - YYYY-MM-DD` entry;
- prunes empty sections from the release entry;
- collapses the linter-version bumps to **one line per linter**, alphabetically sorted, using the **chronological first-seen `from` → last-seen `to`** range with no date (this is intentional: it stays correct across renumberings, e.g. cfn-lint `3.14 → 1.52.0`, where a naive semver-min/max would print a backwards range);
- strips `<!-- linter-versions-end -->` from the release entry;
- prepends a fresh empty `## [Unreleased]` block that holds the **sole** marker and keeps the repo's `(N)` placeholder on the linter-versions header.

PR-number backfill is the one **judgment** part, so the script splits it into `analyze` (lists the lines that need a PR) and `apply` (consumes your decisions).

### 2a — List the lines that need a PR number

```bash
python .claude/skills/prepare-release/prepare_changelog.py analyze
```

This prints a JSON array of candidates `{id, section, text}` — every content line (`  - …`) in a non-version section that does **not** already carry a MegaLinter reference. A line counts as already-referenced only if it has `(#N)`, a bare `#N` after a space/paren, or an `oxsecurity/megalinter` URL. A line that merely links an external repo/issue (e.g. the linter's own GitHub page) is **not** considered referenced and will appear as a candidate.

### 2b — Decide the PR(s) for each candidate

Build the commit map for the release window:

```bash
PREV_TAG="$(git tag --sort=-creatordate | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | head -1)"
git log "$PREV_TAG"..HEAD --oneline --no-merges
```

For each candidate, extract distinctive keywords (linter name, descriptor ID, quoted identifier) and find the PR:

- `grep -i "KEYWORD"` against the commit map (squash-merge subjects end in `(#NNNN)`);
- for terms not in commit subjects, `gh pr list --state merged --search "KEYWORD in:title" --json number,title --limit 5`.

Write the **confident** matches to a JSON file, keyed by candidate `id`, value = PR number(s) (comma-separated for multiple):

```json
{ "0": "8216", "1": "8216", "5": "7907", "12": "8133,8134" }
```

Leave a candidate **out** of the JSON when no PR is found, the match is ambiguous, or the matching commit has no PR number. Unmatched lines are simply left as-is — do **not** report them or ask the user about them.

### 2c — Apply the transformation

```bash
python .claude/skills/prepare-release/prepare_changelog.py apply \
  --version RELEASE_VERSION --date "$(date +%F)" --prs /path/to/prs.json
```

This rewrites `CHANGELOG.md` in place. (For a dry run, add `--out /some/tmp/path` to write elsewhere and leave `CHANGELOG.md` untouched.)

## Step 3 — Confirm the CHANGELOG

Show the diff:

```bash
git diff CHANGELOG.md
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
