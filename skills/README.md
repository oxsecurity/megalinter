# MegaLinter skills for coding agents

Skills that make [MegaLinter](https://megalinter.io/) easy to drive from any coding agent (Claude Code, Cursor CLI, GitHub Copilot CLI, Codex, Antigravity, OpenCode...).

## Installation

### As an agent plugin (recommended)

A single command installs the four skills and the three sub-agents together, and keeps them updated.

| Platform                 | Install                                                                                                    |
|:-------------------------|:-----------------------------------------------------------------------------------------------------------|
| Claude Code              | `/plugin marketplace add oxsecurity/megalinter` then `/plugin install megalinter@megalinter`               |
| Cursor                   | Add `https://github.com/oxsecurity/megalinter` from **Customize → Plugins**, then install **MegaLinter**   |
| GitHub Copilot           | `copilot plugin marketplace add oxsecurity/megalinter` then `copilot plugin install megalinter@megalinter` |
| Codex                    | `codex plugin marketplace add oxsecurity/megalinter`, then install from the `/plugins` browser             |
| Gemini CLI / Antigravity | `gemini extensions install https://github.com/oxsecurity/megalinter`                                       |

The sub-agents ship with the plugin on Claude Code and Cursor, where they are namespaced
(`megalinter:megalinter-fixer`). The other platforms install the skills only, which degrade gracefully to inline
execution.

### As skills

With **Claude Code** (the skills are copied directly into `.claude/skills/`):

```bash
npx skills add oxsecurity/megalinter/skills -s '*' -a claude-code -y
```

With **another coding agent**, replace `claude-code` with your agent's identifier (`cursor`, `github-copilot`, `codex`, `antigravity`, `opencode`... full list in the [skills CLI documentation](https://github.com/vercel-labs/skills#supported-agents)) — or let the CLI **detect your installed agents** and install the skills for all of them at once:

```bash
npx skills add oxsecurity/megalinter/skills -s '*' -y --copy
```

To update already installed skills to the latest version:

```bash
npx skills update megalinter megalinter-setup megalinter-check megalinter-fix -y
```

`megalinter-setup` runs this for you in upgrade mode, and also refreshes the sub-agent definitions it installed —
those live in your agents folder and are not touched by `skills update`.

Plugin installations are updated by the platform instead (`/plugin update megalinter@megalinter` on Claude
Code), which refreshes the skills and the sub-agents together.

## Skills

| Skill                                         | Purpose                                                                                                                                                                                                 |
|:----------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [megalinter](megalinter/SKILL.md)             | Entry point: detects the repository state and orchestrates setup, check and fix in a loop until the repository is clean                                                                                 |
| [megalinter-setup](megalinter-setup/SKILL.md) | Install or upgrade MegaLinter on a repository with `npx mega-linter-runner --install` / `--upgrade`, and scaffold a [custom flavor](https://megalinter.io/latest/custom-flavors/) repository on request |
| [megalinter-check](megalinter-check/SKILL.md) | Collect lint errors: watch a running CI job (GitHub, GitLab, Azure, Bitbucket) or run MegaLinter locally with docker or podman (offering to install/start the engine if missing)                        |
| [megalinter-fix](megalinter-fix/SKILL.md)     | Fix the collected errors using per-linter fix guides, or disable rules/linters when fixing is not relevant                                                                                              |

## Sub-agents optimization

The skills are agent-agnostic but optimized for platforms supporting sub-agents (Claude Code, OpenCode, GitHub Copilot custom agents, Codex...):

- The plugin ships three sub-agent definitions (Claude Code, Cursor); with a skills installation, `megalinter-setup` copies them into your platform's agents folder (e.g. `.claude/agents/`, `.opencode/agent/`, `.github/agents/`)
- `megalinter-watcher` (low-cost model) watches CI jobs and returns only the relevant error excerpts
- `megalinter-runner` (low-cost model) runs MegaLinter locally and digests the reports
- `megalinter-fixer` fixes the errors of one linter, so several linters can be fixed in parallel

On agents without sub-agent support, every skill degrades gracefully to inline execution.

## Performance suggestions

`megalinter-check` always collects per-linter elapsed times: when a linter is unusually slow (over 30 seconds or 25% of the run), it reports speed improvement suggestions from its `performance.md` playbook (DB caching for security scanners, targeted exclusions, flavor selection, diff-only CI linting...) — even when nothing is failing. Suggestions are never applied without user agreement.

## Custom flavors

`megalinter-setup` can also scaffold and maintain a [custom flavor](https://megalinter.io/latest/custom-flavors/)
repository — your own MegaLinter image containing only the linters you need, so runs start faster.
Ask for it explicitly ("create a custom flavor") and the skill loads its `custom-flavor.md` guide, which first looks
for a flavor you already own or administer (reusing or extending one beats maintaining two), then creates the
repository and runs the generator. It also covers publishing (including the optional, and deliberately not required,
`PAT_TOKEN`), AGPL-3.0 obligations, consuming the published image, and keeping the flavor in sync with new
MegaLinter releases.

## Safety rules

- Fixes are applied automatically only when safe; ambiguous cases are asked to the user
- Disabling a linter or a rule always requires user confirmation
- Commits are never pushed to the default branch (`main`/`master`)
- Force-push is never used, with a single exception: when the MegaLinter CI job pushed its own `[MegaLinter] Apply linters fixes` commit, `megalinter-check` amends it with a 🤖 prefix and re-pushes it with `--force-with-lease`, which re-triggers the CI checks that a token-authored push does not trigger (on the default branch, the user is asked first)

## Maintenance

The per-linter fix guides in `megalinter-fix/linters/` contain a block generated from the
[YAML linter descriptors](https://github.com/oxsecurity/megalinter/tree/main/megalinter/descriptors)
by `.automation/build.py` (between `generated-descriptor-info` markers, refreshed by automated workflows)
and hand-maintained fix instructions below the markers.

The agent plugin manifests live at the repository root (`plugin.json`, `.claude-plugin/`, `.codex-plugin/`,
`.cursor-plugin/`, `.agents/`, `gemini-extension.json`). `plugin.json` is the single source of truth for the plugin
identity and version; `.automation/agent_plugin_manifests.py` mirrors it into the others and
`.automation/validate_agent_plugins.py` checks them in CI.
