# MegaLinter skills for coding agents

Skills that make [MegaLinter](https://megalinter.io/) easy to drive from any coding agent (Claude Code, Cursor CLI, GitHub Copilot CLI, Codex, Antigravity, OpenCode...).

## Installation

With **Claude Code** (the skills are copied directly into `.claude/skills/`):

```bash
npx skills add oxsecurity/megalinter/skills -s '*' -a claude-code -y
```

With **another coding agent**, replace `claude-code` with your agent's identifier (`cursor`, `github-copilot`, `codex`, `antigravity`, `opencode`... full list in the [skills CLI documentation](https://github.com/vercel-labs/skills#supported-agents)) — or let the CLI **detect your installed agents** and install the skills for all of them at once:

```bash
npx skills add oxsecurity/megalinter/skills -s '*' -y --copy
```

## Skills

| Skill                                         | Purpose                                                                                                                                                                          |
|:----------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [megalinter](megalinter/SKILL.md)             | Entry point: detects the repository state and orchestrates setup, check and fix in a loop until the repository is clean                                                          |
| [megalinter-setup](megalinter-setup/SKILL.md) | Install or upgrade MegaLinter on a repository with `npx mega-linter-runner --install` / `--upgrade`                                                                              |
| [megalinter-check](megalinter-check/SKILL.md) | Collect lint errors: watch a running CI job (GitHub, GitLab, Azure, Bitbucket) or run MegaLinter locally with docker or podman (offering to install/start the engine if missing) |
| [megalinter-fix](megalinter-fix/SKILL.md)     | Fix the collected errors using per-linter fix guides, or disable rules/linters when fixing is not relevant                                                                       |

## Sub-agents optimization

The skills are agent-agnostic but optimized for platforms supporting sub-agents (Claude Code, OpenCode, GitHub Copilot custom agents, Codex...):

- `megalinter-setup` installs three sub-agent definitions in your platform's agents folder (e.g. `.claude/agents/`, `.opencode/agent/`, `.github/agents/`)
- `megalinter-watcher` (low-cost model) watches CI jobs and returns only the relevant error excerpts
- `megalinter-runner` (low-cost model) runs MegaLinter locally and digests the reports
- `megalinter-fixer` fixes the errors of one linter, so several linters can be fixed in parallel

On agents without sub-agent support, every skill degrades gracefully to inline execution.

## Performance suggestions

`megalinter-check` always collects per-linter elapsed times: when a linter is unusually slow (over 30 seconds or 25% of the run), it reports speed improvement suggestions from its `performance.md` playbook (DB caching for security scanners, targeted exclusions, flavor selection, diff-only CI linting...) — even when nothing is failing. Suggestions are never applied without user agreement.

## Safety rules

- Fixes are applied automatically only when safe; ambiguous cases are asked to the user
- Disabling a linter or a rule always requires user confirmation
- Commits are never pushed to the default branch (`main`/`master`)

## Maintenance

The per-linter fix guides in `megalinter-fix/linters/` contain a block generated from the
[YAML linter descriptors](https://github.com/oxsecurity/megalinter/tree/main/megalinter/descriptors)
by `.automation/build.py` (between `generated-descriptor-info` markers, refreshed by automated workflows)
and hand-maintained fix instructions below the markers.
