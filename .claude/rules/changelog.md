---
description: CHANGELOG.md writing rules — audience and style
globs: ["CHANGELOG.md"]
---

# CHANGELOG Rules

## Audience

`CHANGELOG.md` is release notes for **end users** of MegaLinter (people who run it in CI or locally), not for maintainers. Every entry must answer, from the user's point of view: *what changes for me, and what do I do about it?*

## Entry style

- One entry = one or two short sentences leading with the user benefit or the required action
- Keep sentences short. When an entry needs more than ~2 lines, write a short lead line and put the details in **sub-bullets** (one fact per sub-bullet) instead of chaining clauses into a long sentence
- Highlight the key words/expressions in **bold** so the page can be scanned: the feature name, the variable/option, or the headline figure — one or two bold spans per entry, never whole sentences
- Name the things users interact with: configuration variables, linter keys, CLI options, documentation pages. Link doc pages and fixed issues
- In user-facing sections, do NOT include implementation details: internal module/class/file names, build-system mechanics, refactoring narratives, how a fix works internally, why CI is faster — that detail belongs under the `Dev`/`CI` sections (see below)
- Every markdown table must have an **empty line before and after it** (Zensical and markdownlint requirement), including tables nested under a bullet
- Performance and size improvements are shown as **before/after tables** (`| ... | Before | After | Delta |`): user-visible measures (Docker image sizes, MegaLinter run duration, startup time) as a table in the user-facing section; repository CI job timings as a table in the `CI` section. Put the numbers in the table, not inline in the bullets. Lead image-size tables with the main and flavor images (the most used), then standalone images; measure sizes from ghcr.io manifests (sum of amd64 `layers[].size` = compressed download size — Docker Hub tags are stale)

## What goes where

- User-facing sections (`Breaking changes`, `Core`, `Fixes`, `Reporters`, linter sections, `mega-linter-runner`, `Agent Skills`): user-facing behavior changes, new configuration variables/options, breaking changes, notable performance or image-size improvements, fixes of user-visible bugs — written per the entry style above
- `Agent Skills` section: changes to the agent skills shipped in `skills/` (`megalinter`, `megalinter-setup`, `megalinter-check`, `megalinter-fix`) and to the sub-agent definitions they install. Its readers drive MegaLinter through a coding agent, so describe **what the agent now does for them**, and name the skill in bold as the entry subject (`**megalinter-check** now ...`). It sits with `mega-linter-runner` in the section order: both are companion tools installed separately from the Docker image. Changes to MegaLinter itself go in the regular sections even when a skill relays them
- `Dev` and `CI` sections: internal/technical changes (refactors, descriptor/build-system properties, test-suite work, repository CI/workflow changes, repo tooling). Technical detail and implementation specifics are fine **here** — these sections are the home for them, so they never leak into the user-facing sections. If an internal change also has a user-observable effect, describe the observable effect in the matching user-facing section and keep the technical detail under `Dev`/`CI`
- Never an entry anywhere: linter version bumps (the auto-upgrade workflow owns **Linter versions upgrades**), CVE-ignore entries, and refreshes of the generated `generated-descriptor-info` blocks in `skills/megalinter-fix/linters/*.md` (owned by the auto-update workflow, like linter versions)
