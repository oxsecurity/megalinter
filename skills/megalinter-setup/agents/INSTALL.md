# Installing the MegaLinter sub-agents on your platform

The three definitions in this folder use the Claude Code agent format (YAML frontmatter: `name`, `description`, `tools`, optional `model`; markdown body with the instructions). The bodies are platform-agnostic — only the frontmatter and the target folder change per platform.

Load only the section matching the platform you are running on. In every case: create the target folder if missing, and ask the user before overwriting an existing file.

## Claude Code

Copy the files as-is:

```bash
mkdir -p .claude/agents && cp <skill_dir>/agents/megalinter-*.md .claude/agents/
```

## OpenCode

Target folder: `.opencode/agent/`. Adapt the frontmatter: set `mode: subagent`, translate `tools` to OpenCode's `tools:` map (e.g. `bash: true`, `edit: false` for the read-only watcher/runner), and replace `model: haiku` with a cheap model available in your configuration (e.g. `anthropic/claude-haiku-4-5`). Keep `description` and the body unchanged.

## GitHub Copilot (custom agents)

Target folder: `.github/agents/`. Keep `name` and `description` in the frontmatter; drop `tools`/`model` if your Copilot version doesn't accept them; keep the body unchanged.

## Codex and other platforms

If your platform documents custom agent/subagent definition files, mirror the pattern above: keep the body, translate the frontmatter to the platform's schema, place the files in the platform's agents location. If the platform only supports a single instructions file (e.g. `AGENTS.md`), do NOT install these files — the MegaLinter skills already degrade to inline execution.

## Model guidance

`megalinter-watcher` and `megalinter-runner` do mechanical work (poll, download, digest): map them to the cheapest/fastest model tier your platform offers. `megalinter-fixer` edits code: leave it on the session's default model (no model override).
