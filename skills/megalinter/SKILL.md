---
name: megalinter
description: Entry point for everything MegaLinter. Use when the user wants to lint their repository, set up MegaLinter, check or fix lint errors, make CI lint jobs pass, or says "run megalinter", "fix lint errors", "make the linters happy", "clean up code quality". Detects the repository state and orchestrates the megalinter-setup, megalinter-check and megalinter-fix skills in a loop until the repository is clean.
argument-hint: "[request, e.g. 'run megalinter and fix the errors' or 'make the CI lint job pass']"
allowed-tools: Bash, Read, Grep, Glob, Skill, Agent, AskUserQuestion
user-invocable: true
licence: MegaLinter by OX Security, Copyright 2026 - https://megalinter.io/
---

# MegaLinter orchestrator

You orchestrate MegaLinter on this repository. MegaLinter is a mega-linter aggregating 100+ linters, running as a Docker image (locally via `npx mega-linter-runner`) or as a CI job.

## Workflow

1. **Detect repository state**:
   - No `.mega-linter.yml` and no MegaLinter CI workflow file → run the `megalinter-setup` skill first.
   - Configuration present → go to step 2.
2. **Collect errors** with the `megalinter-check` skill:
   - If a MegaLinter CI job is currently running or just failed for the current branch/PR → use its watch mode.
   - Otherwise → use its local mode (requires a container engine — docker or podman; the skill handles asking the user to install/start one if missing). Before the first local run, make sure the user is aware it needs a good computer configuration and a good internet connection: MegaLinter is Docker-based and can download images of several GB.
3. **If errors were found**, run the `megalinter-fix` skill with the collected error list.
4. **Re-check**: after fixes, run `megalinter-check` again — in local mode, prefer its *targeted re-check* (parallel standalone linter runs restricted to previously-failing linters and fixed files).
5. Repeat steps 3-4 **at most 3 times**. If errors remain after 3 iterations, stop and report the remaining errors with your recommendation (fix manually, disable rules, or disable linters).
6. **Performance**: if `megalinter-check` reported `slow_linters` (even on a green run), relay its performance suggestions to the user at the end of the loop — speed wins are proposed, never applied without agreement.

## Rules

- Never commit or push on the default branch (`main`/`master`): create a branch like `megalinter/fix-<topic>` first.
- Ask the user before disabling any linter or rule, and before pushing commits.
- Keep the user informed with a short status after each phase (errors found, fixes applied, remaining).

## Optimization: sub-agents (Claude Code and compatible agents)

If your environment supports spawning sub-agents (e.g. a Task/Agent tool) and the `megalinter-watcher`, `megalinter-runner`, `megalinter-fixer` agent definitions are installed (the `megalinter-setup` skill installs them in your platform's agents folder, e.g. `.claude/agents/`, `.opencode/agent/`, `.github/agents/`):

- Delegate CI watching to `megalinter-watcher` and local runs to `megalinter-runner` — they keep the large logs out of your context and return only a compact error list.
- Fan out one `megalinter-fixer` per failing linter to fix several linters in parallel.

If sub-agents are not available, perform every step inline following the skill instructions.
