---
name: megalinter-fix
description: Fix the errors reported by MegaLinter. Use after megalinter-check found errors, or when the user pastes MegaLinter/CI lint errors and wants them fixed. Applies safe fixes automatically (auto-fix linters first, then guided manual fixes using per-linter fix guides), asks the user when fixing is ambiguous, and can disable rules or linters with user confirmation. Never pushes to the default branch.
argument-hint: "[linter keys or pasted MegaLinter error list]"
allowed-tools: Bash, Read, Grep, Glob, Edit, Write, Agent, Skill, AskUserQuestion, WebSearch, WebFetch
user-invocable: true
licence: MegaLinter by OX Security, Copyright 2026 - https://megalinter.io/
---

# MegaLinter fix

Fix the MegaLinter errors you were given (output contract of `megalinter-check`: linter keys, error counts, files, sample error lines).

## 1. Prepare

- If the current branch is the default branch (`main`/`master`), create a branch first: `git checkout -b megalinter/fix-<topic>`.
- Group the errors by linter key. Handle **blocking** linters (❌) first; mention non-blocking ones (⚠️) to the user but don't fix them unless asked.

## 2. Load the fix guides — lazily

For **each failing linter only**, read its fix guide from this skill's directory: `linters/<linter_key_lower>.md` (e.g. `linters/python_ruff.md`). The index is in `linters/README.md`.

Each guide contains a generated block (auto-fix support, config/ignore files, rule documentation URLs, tuning variables, known non-lint failure patterns) and researched fix instructions. Never load guides for linters without errors.

## 3. Fix

In this order:

1. **Auto-fixable linters** (guide says auto-fix supported): if a container engine is available, run `npx mega-linter-runner --linter <KEY> --fix [failing files...]` (add `--container-engine podman` when using podman; use `npx mega-linter-runner@beta` when `.mega-linter.yml` pins `MEGALINTER_VERSION: beta` — see the version rule in `megalinter-check`). Otherwise apply the underlying tool's documented fix behavior manually. If no engine is installed/running, ask the user first, then follow `container-engine.md` in the `megalinter-check` skill directory.
2. **Manual fixes**: fix remaining errors file by file following the guide's instructions. Consult the rule documentation URLs when unsure what a rule means.
3. **Errors not covered by the guide** (unknown rule, missing/outdated guide): browse the web — fetch the rule's official documentation (start from the URLs in the guide's generated block) or search for the exact error message — before deciding on a fix. Never guess a fix or a suppression syntax.
4. **Ambiguous cases** (fix would change behavior, several valid approaches, false positive suspected): ask the user, presenting the options — fix this way, inline-disable with justification, or ignore.

## 4. Disabling (always with user confirmation)

When fixing is not relevant (false positives, rule conflicts with project style, linter not applicable):

- Narrowest first: inline-disable comment on the line → rule exclusion in the linter's config file → `<KEY>_FILTER_REGEX_EXCLUDE` → `<KEY>_DISABLE_ERRORS: true` (non-blocking) → `DISABLE_LINTERS` (last resort).
- The guide gives the exact syntax for each level. **Never** disable anything without explicit user confirmation.
- If a project-mode linter reports unexpected results tied to its exclusions or config resolution, check its console log for `[Excluded directories]` lines: MegaLinter automatically forwards excluded directories through extra CLI arguments or generated ignore/config files. Disabling that forwarding for the linter (`<LINTER_KEY>_FORWARD_EXCLUDED_DIRECTORIES: false`) restores the tool's native behavior — useful when the repository's own ignore/config files are already complete.

## 5. Verify and finish

1. Re-check with the `megalinter-check` skill (targeted re-check mode: only the fixed linters/files). Iterate at most 3 times in total.
2. Show the user a summary: fixed / disabled (with justification) / remaining.
3. Commit on the working branch with a clear message. **Ask before pushing**; never push to the default branch.

## Optimization: sub-agents (Claude Code and compatible agents)

If sub-agents are available and `megalinter-fixer` is installed (see `megalinter-setup`), fan out **one `megalinter-fixer` per failing linter in parallel**, giving each: the linter key, its error list, and the content of its fix guide. Each fixer returns its fixed count, modified files, and an `unresolved` list (possibly containing `proposed_disable` suppressions — fixers never apply disables themselves). Consolidate, ask the user about every unresolved item and proposed disable, apply the confirmed ones yourself, then run the targeted re-check (via `megalinter-runner` agents when available).

Without sub-agents, fix linters sequentially inline.
