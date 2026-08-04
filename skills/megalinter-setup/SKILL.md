---
name: megalinter-setup
description: Install or upgrade MegaLinter on a repository. Use when the user wants to add MegaLinter to a project, set up linting CI, update MegaLinter configuration or version, or says "install megalinter", "setup linting", "add code quality checks". Always goes through npx mega-linter-runner (--install or --upgrade), then refines .mega-linter.yml.
argument-hint: "[install|upgrade] [flavor, e.g. python|javascript|all]"
allowed-tools: Bash, Read, Grep, Glob, Edit, Write, WebFetch, AskUserQuestion
user-invocable: true
licence: MegaLinter by OX Security, Copyright 2026 - https://megalinter.io/
---

# MegaLinter setup

Install or upgrade MegaLinter on the current repository. **Always use `npx mega-linter-runner` to scaffold or upgrade the configuration — never write `.mega-linter.yml` or CI workflow files from scratch.** Only refine the generated files afterwards.

## 1. Analyze the repository

Gather what you need to answer the installer's options:

- **Flavor**: detect the main technology and pick a [flavor](https://megalinter.io/flavors/) (`python`, `javascript`, `java`, `go`, `php`, `ruby`, `rust`, `salesforce`, `swift`, `terraform`, `dotnet`, `dotnetweb`, `c_cpp`, `documentation`, `formatters`, `security`, ...). Mixed or unclear → `all`.
- **CI system**: from existing config (`.github/` → `gitHubActions`, `.gitlab-ci.yml` → `gitLabCI`, `azure-pipelines.yml` → `azure`, `bitbucket-pipelines.yml` → `bitbucket`, `Jenkinsfile` → `jenkins`, `.drone.yml` → `droneCI`) or the git remote host. None → `other`.
- **Default branch**: `git remote show origin` or the current repository default.

## 2. Install or upgrade

**No MegaLinter configuration yet** — run the installer non-interactively:

```bash
npx mega-linter-runner --install --no-prompt \
  --flavor <flavor> \
  --setup-ci <ci> \
  --setup-default-branch <branch> \
  --fix
```

If the runner rejects one of the options above ("Invalid option" error), the resolved mega-linter-runner version is outdated: re-run with `npx mega-linter-runner@latest` (the `--setup-*` and `--linter` options need a recent version).

Notes:

- The whole codebase is validated on each run (default). Pass `--setup-validate-all-code-base diff` only if the user explicitly asks to lint updated files only.
- Add `--release beta` only if the user asks for the beta version (the installer then writes `MEGALINTER_VERSION: beta` in `.mega-linter.yml`).
- **Version rule (all skills)**: runner and Docker image versions always follow `MEGALINTER_VERSION` from `.mega-linter.yml` — invoke `npx mega-linter-runner@beta` when it is `beta`, plain `npx mega-linter-runner` in every other case, and never pass `--release` outside of this install step.
- `--fix` enables auto-fixes (`APPLY_FIXES: all`); omit it if the user doesn't want automatic formatting.
- If the user is present and wants to choose interactively, run plain `npx mega-linter-runner --install` instead and let them answer.

**Preserve existing customizations.** In non-interactive mode the installer overwrites conflicting files, but it first backs up every pre-existing target as `<file>.megalinter-setup.bak` (config files and the CI workflow file). After the install:

1. Diff each `.megalinter-setup.bak` file against its regenerated version.
2. Re-apply the user's customizations that are still relevant (extra workflow steps, env vars, custom triggers, added config entries...). When a customization conflicts with the new template or its intent is unclear, **ask the user** what to keep.
3. Delete the `.megalinter-setup.bak` files once merged.

**Configuration already exists** — upgrade it:

```bash
npx mega-linter-runner --upgrade --no-prompt
```

`--upgrade` migrates every MegaLinter reference of the repository to the current major version: image tags and action versions in the CI workflow files, deprecated variable names, and the `MEGALINTER_VERSION` property of `.mega-linter.yml`. Run it whenever the repository references an older MegaLinter major version (e.g. `v8` image tags), even if the user only asked for a "check".

After upgrading, check the CI files for Docker image references still pointing to Docker Hub (`docker.io/oxsecurity/megalinter*` or bare `oxsecurity/megalinter:*` image references): since MegaLinter v9.5.0, images are **only published to GitHub Container Registry** — rewrite them to `ghcr.io/oxsecurity/megalinter...` (Docker Hub is frozen at v9.4.0). GitHub Action references (`uses: oxsecurity/megalinter@...`) are not affected.

## 3. Refine `.mega-linter.yml` (only AFTER install/upgrade)

Once the runner has generated/upgraded the files, you may adjust `.mega-linter.yml`:

- Ensure `MEGALINTER_FLAVOR` and `MEGALINTER_VERSION` are set (the installer writes them; add them if upgrading an older config) — they drive which Docker image `mega-linter-runner` and these skills use.
- Add `DISABLE` / `DISABLE_LINTERS` entries the user asks for.
- Add `FILTER_REGEX_EXCLUDE` for generated or vendored folders (e.g. `(dist/|build/|vendor/|node_modules/)`).

Validate the file against its JSON schema: <https://raw.githubusercontent.com/oxsecurity/megalinter/main/megalinter/descriptors/schemas/megalinter-configuration.jsonschema.json>

## 4. Install the MegaLinter sub-agents (if your platform supports them)

This skill ships three sub-agent definitions in its `agents/` folder (`megalinter-watcher`, `megalinter-runner`, `megalinter-fixer`) that make the other MegaLinter skills faster and cheaper by keeping CI logs and linter output out of the main context.

If the coding agent you are running on supports custom sub-agent definitions (Claude Code, OpenCode, GitHub Copilot, Codex... — you know whether you do), read `agents/INSTALL.md` in this skill's directory and follow the instructions for your platform: copy the three `agents/*.md` files to your platform's agents folder, adapting the frontmatter when needed.

If a target file already exists, ask the user before overwriting it. If your platform has no sub-agent support, skip this step — the skills degrade gracefully to inline execution.

## 5. Wrap up

- Show the user the generated/updated files.
- Suggest the two ways to see MegaLinter in action (first install and upgrade alike), and offer to do it for them:
  - **Run MegaLinter locally** through the `megalinter-check` skill (local mode) to preview and fix errors before pushing anything.
  - **Create a pull request** with the generated/updated files (commit on the current branch if it is already a feature branch, otherwise on a new branch — never on the default branch —, push, open the PR), then run the `megalinter-check` skill (watch mode) on the created PR to watch the CI job results and fix the errors.
- Do not commit or push without user confirmation, and never on the default branch.
