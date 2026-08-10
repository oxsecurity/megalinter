---
name: megalinter-setup
description: Install or upgrade MegaLinter on a repository. Use when the user wants to add MegaLinter to a project, set up linting CI, update MegaLinter configuration or version, or says "install megalinter", "setup linting", "add code quality checks", "update megalinter skills". Always goes through npx mega-linter-runner (--install or --upgrade), then refines .mega-linter.yml. In upgrade mode it also refreshes the installed MegaLinter skills and sub-agents. Also sets up a MegaLinter custom flavor repository when the user explicitly asks for one.
argument-hint: "[install|upgrade|custom-flavor] [flavor, e.g. python|javascript|all]"
allowed-tools: Bash, Read, Grep, Glob, Edit, Write, WebFetch, Skill, AskUserQuestion
user-invocable: true
licence: MegaLinter by OX Security, Copyright 2026 - https://megalinter.io/
---

# MegaLinter setup

Install or upgrade MegaLinter on the current repository. **Always use `npx mega-linter-runner` to scaffold or upgrade the configuration — never write `.mega-linter.yml` or CI workflow files from scratch.** Only refine the generated files afterwards.

**Custom flavor repositories**: if — and only if — the user explicitly asks to create or maintain a **custom MegaLinter flavor** (their own image with just the linters they need, published from a dedicated `megalinter-custom-flavor-*` repository), this is a different job from the install flow below: load `custom-flavor.md` from this skill's directory and follow it instead. Everything else on this page targets a project that *consumes* MegaLinter.

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

<!-- MAJOR-RELEASE-IMPACTED (example tags below) -->
**Mandatory after `--upgrade` — migrate Docker image references to ghcr.io.** Since MegaLinter v9.5.0, images are **only published to GitHub Container Registry** (Docker Hub is frozen at v9.4.0), and `--upgrade` does NOT rewrite the registry: it normalizes references to the bare `oxsecurity/megalinter...` form. So always finish with this pass:

1. Search every CI/workflow file of the repository (`.github/workflows/*`, `.gitlab-ci.yml`, `azure-pipelines.yml`, `bitbucket-pipelines.yml`, `Jenkinsfile`, `.drone.yml`, shell scripts...) for `oxsecurity/megalinter` occurrences.
2. Rewrite every occurrence used as a **Docker image** (after `image:`, `container:`, `services:`, `docker run`, `docker pull`, or any `oxsecurity/megalinter[-<flavor>]:<tag>` form, including `megalinter-only-*` standalone images and `docker.io/`-prefixed references) to the same reference prefixed with `ghcr.io/` — keep flavor and tag unchanged: `oxsecurity/megalinter-python:v10` becomes `ghcr.io/oxsecurity/megalinter-python:v10`.
3. Leave untouched: references already prefixed with `ghcr.io/`, GitHub Action references (`uses: oxsecurity/megalinter@...` — actions are not Docker images), and documentation URLs.

### Also upgrade the MegaLinter skills and sub-agents

The repository configuration is only half of the setup. The MegaLinter skills you are running, and the sub-agent
definitions they installed, were copied into the project (or the user profile) when they were added and **do not
update themselves** — so an upgraded repository can still be driven by guidance written for an older MegaLinter.
Refresh them whenever you run an upgrade, and whenever the user asks to update the MegaLinter skills.

Check first how they are installed:

```bash
npx skills list
```

MegaLinter entries show their install path and `Source`. A `local` source means the files are not managed by the
skills CLI (the MegaLinter repository's own `skills/` folder, or a manual copy): leave those alone and tell the user.

Otherwise update them, naming the skills explicitly — a bare `npx skills update` would also update every unrelated
skill installed in the project:

```bash
npx skills update megalinter megalinter-setup megalinter-check megalinter-fix -y
```

Add `-p` to restrict to project-level skills, or `-g` for the user-level ones, when both exist and only one should move.

If the update reports nothing to do (skills added with `--copy` are not always tracked), re-run the install command
instead — it overwrites the installed copies with the current version:

```bash
npx skills add oxsecurity/megalinter/skills -s '*' -a <agent> -y
```

Then **refresh the sub-agents**: `skills update` rewrites the skill folders only, never the copies made into your
platform's agents folder (`.claude/agents/`, `.opencode/agent/`, `.github/agents/`). Re-apply step 4 below for the
three definitions so they match the refreshed skills, asking the user before overwriting any they customized.

Finally, note that **the skill you are currently executing may have just been rewritten**. After the refresh, re-read
`SKILL.md` in this skill's directory and continue from the updated instructions if they differ from what you loaded.

## 3. Refine `.mega-linter.yml` (only AFTER install/upgrade)

Once the runner has generated/upgraded the files, you may adjust `.mega-linter.yml`:

- Ensure `MEGALINTER_FLAVOR` and `MEGALINTER_VERSION` are set (the installer writes them; add them if upgrading an older config) — they drive which Docker image `mega-linter-runner` and these skills use.
- Add `DISABLE` / `DISABLE_LINTERS` entries the user asks for.
- Add `FILTER_REGEX_EXCLUDE` for generated or vendored folders (e.g. `(dist/|build/|vendor/|node_modules/)`). Excluded directories (and folders identified from these regexes) are also automatically forwarded to project-mode linters through their native exclusion arguments or generated ignore/config files; if the repository already maintains its own up-to-date ignore/config files for a linter, that forwarding can be turned off with `FORWARD_EXCLUDED_DIRECTORIES: false` (global) or `<LINTER_KEY>_FORWARD_EXCLUDED_DIRECTORIES: false` (per linter).

Validate the file against its JSON schema: <https://raw.githubusercontent.com/oxsecurity/megalinter/main/megalinter/descriptors/schemas/megalinter-configuration.jsonschema.json>

## 4. Install or refresh the MegaLinter sub-agents (if your platform supports them)

This skill ships three sub-agent definitions in its `agents/` folder (`megalinter-watcher`, `megalinter-runner`, `megalinter-fixer`) that make the other MegaLinter skills faster and cheaper by keeping CI logs and linter output out of the main context.

If the coding agent you are running on supports custom sub-agent definitions (Claude Code, OpenCode, GitHub Copilot, Codex... — you know whether you do), read `agents/INSTALL.md` in this skill's directory and follow the instructions for your platform: copy the three `agents/*.md` files to your platform's agents folder, adapting the frontmatter when needed.

If a target file already exists, ask the user before overwriting it. In upgrade mode the existing files are precisely
what needs replacing: show the user what changed, and preserve any customization they made (a model override, an
adapted `tools` list) when re-applying the new version. If your platform has no sub-agent support, skip this step —
the skills degrade gracefully to inline execution.

## 5. Observability dashboards (optional)

MegaLinter can send its results to observability platforms (Grafana, Datadog, Elastic, New Relic) and ships ready-to-use dashboards: quality gate, error trends, top rules and files across repositories. Documentation: <https://megalinter.io/latest/observability/>

Offer this to the user only if they seem interested in monitoring or already use one of these platforms. If accepted:

1. Ask which provider they use, and make sure the provider auth environment variables are available (never write secrets in committed files):
   - grafana: `GRAFANA_URL` + `GRAFANA_TOKEN` (service account token)
   - datadog: `DD_SITE` + `DD_API_KEY` + `DD_APP_KEY` (or `DD_BEARER_TOKEN`)
   - elastic: `KIBANA_URL` + `ELASTIC_API_KEY`
   - newrelic: `NEW_RELIC_API_KEY` + `NEW_RELIC_ACCOUNT_ID` + `NEW_RELIC_REGION`
2. Provision the dashboards: `npx mega-linter-runner --upload-dashboards <provider>` (idempotent, re-run anytime to refresh).
3. Add to `.mega-linter.yml`: `API_REPORTER: true`, `API_REPORTER_PROVIDER: <provider>`, and the provider's non-secret variables (endpoints, site, region — see the documentation page of the provider). Point the user to the CI secrets to define for the auth variables (`API_REPORTER_*` tokens/keys).

## 6. Wrap up

- Show the user the generated/updated files.
- Propose the two ways to see MegaLinter in action (first install and upgrade alike), and offer to do it for them. A local run is **resource-consuming** (Docker-based, downloads an image of several GB on first run, then loads CPU/RAM/disk), so **running in CI is usually the recommended option** — ask the user which one they want (use your platform's structured question mechanism if it has one, with the CI option first/recommended) instead of picking silently:
  - **Create a pull request** (recommended) with the generated/updated files (commit on the current branch if it is already a feature branch, otherwise on a new branch — never on the default branch —, push, open the PR), then run the `megalinter-check` skill (watch mode) on the created PR to watch the CI job results and fix the errors.
  - **Run MegaLinter locally** through the `megalinter-check` skill (local mode) to preview and fix errors before pushing anything. Its first run starts with a prerun analysis (`--prerun`, MegaLinter v10 or beta) that suggests `.mega-linter.yml` performance tuning (directories to exclude, flavor) before the real lint.
- Do not commit or push without user confirmation, and never on the default branch.
