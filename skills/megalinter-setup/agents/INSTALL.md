# Installing the MegaLinter sub-agents on your platform

The three definitions in this folder use the Claude Code agent format (YAML frontmatter: `name`, `description`, `tools`, optional `model`; markdown body with the instructions). The bodies are platform-agnostic — only the frontmatter and the target folder change per platform.

Load only the section matching the platform you are running on. In every case: create the target folder if missing, and ask the user before overwriting an existing file.

## Installed as an agent plugin — nothing to do

If MegaLinter was installed as an [agent plugin](https://megalinter.io/latest/agent-plugins/), the three definitions ship with it: the plugin declares them for Claude Code and Cursor, and carries them as `com.github.copilot/agents/*.agent.md` for the Copilot clients (VS Code, Copilot CLI, the Copilot app). Do not copy them anywhere — a second set would drift on the next plugin update.

Depending on the platform they are listed either under a namespaced name (`megalinter:megalinter-watcher`) or under the bare name (`megalinter-watcher`). **Do not try to infer the install mode from the name.** If you cannot see the three agents in the list of agents available to you, ask the user whether MegaLinter was installed as a plugin or as skills, and only follow the sections below if they confirm it was installed as skills.

## Claude Code

Copy the files as-is:

```bash
mkdir -p .claude/agents && cp <skill_dir>/agents/megalinter-*.md .claude/agents/
```

## OpenCode

Target folder: `.opencode/agent/`. Adapt the frontmatter: set `mode: subagent`, translate `tools` to OpenCode's `tools:` map (e.g. `bash: true`, `edit: false` for the read-only watcher/runner), and replace `model: haiku` with a cheap model available in your configuration (e.g. `anthropic/claude-haiku-4-5`). Keep `description` and the body unchanged.

## GitHub Copilot (custom agents)

Target folder: `.github/agents/`, and the file name **must** end with `.agent.md` (`megalinter-watcher.agent.md`) or Copilot will not load it:

```bash
mkdir -p .github/agents
for agent in watcher runner fixer; do
  cp "<skill_dir>/agents/megalinter-$agent.md" ".github/agents/megalinter-$agent.agent.md"
done
```

Then adapt the frontmatter: keep `name`, `description` and `tools` — Copilot's tool aliases are case-insensitive and already accept the names used here (`Read` → `read`, `Grep`/`Glob` → `search`, `Bash` → `execute`, `WebFetch`/`WebSearch` → `web`) — and **remove the `model: haiku` line**, which is not a Copilot model id. Keep the body unchanged.

See the [custom agents configuration reference](https://docs.github.com/en/copilot/reference/custom-agents-configuration) for the full frontmatter schema.

## Codex and other platforms

If your platform documents custom agent/subagent definition files, mirror the pattern above: keep the body, translate the frontmatter to the platform's schema, place the files in the platform's agents location. If the platform only supports a single instructions file (e.g. `AGENTS.md`), do NOT install these files — the MegaLinter skills already degrade to inline execution.

## Model guidance

`megalinter-watcher` and `megalinter-runner` do mechanical work (poll, download, digest): map them to the cheapest/fastest model tier your platform offers. `megalinter-fixer` edits code: leave it on the session's default model (no model override).
