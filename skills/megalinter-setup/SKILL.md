---
name: megalinter-setup
description: Install or upgrade MegaLinter on a repository, in CI, natively on the machine, or both. Use when the user wants to add MegaLinter to a project, set up linting CI, set up fast local checks or pre-commit hooks without Docker (native mode, beta), update MegaLinter configuration or version, or says "install megalinter", "setup linting", "add code quality checks", "update megalinter skills". Always goes through mega-linter-runner (--install, --upgrade, --native-setup), then refines .mega-linter.yml. In upgrade mode it also refreshes the installed MegaLinter skills and sub-agents. Also sets up a MegaLinter custom flavor repository when the user explicitly asks for one.
argument-hint: "[install|upgrade|native|custom-flavor] [flavor, e.g. python|javascript|all]"
allowed-tools: Bash, Read, Grep, Glob, Edit, Write, WebFetch, Skill, AskUserQuestion
user-invocable: true
license: MegaLinter by OX Security, Copyright 2026 - https://megalinter.io/
---

# MegaLinter setup

Install or upgrade MegaLinter on the current repository. **Always use `npx mega-linter-runner` to scaffold or upgrade the configuration — never write `.mega-linter.yml` or CI workflow files from scratch.** Only refine the generated files afterwards.

**Custom flavor repositories**: if — and only if — the user explicitly asks to create or maintain a **custom MegaLinter flavor** (their own image with just the linters they need, published from a dedicated `megalinter-custom-flavor-*` repository), this is a different job from the install flow below: load `custom-flavor.md` from this skill's directory and follow it instead. Everything else on this page targets a project that *consumes* MegaLinter.

## 1. Analyze the repository

Gather what you need to answer the installer's options:

- **Flavor**: detect the main technology and pick a [flavor](https://megalinter.io/flavors/) (`python`, `javascript`, `java`, `go`, `php`, `ruby`, `rust`, `salesforce`, `swift`, `terraform`, `dotnet`, `dotnetweb`, `c_cpp`, `documentation`, `formatters`, `security`, ...). Mixed or unclear → `all`.
- **CI system**: from existing config (`.github/` → `gitHubActions`, `.gitlab-ci.yml` → `gitLabCI`, `azure-pipelines.yml` → `azure`, `bitbucket-pipelines.yml` → `bitbucket`, `Jenkinsfile` → `jenkins`, `.drone.yml` → `droneCI`) or the git remote host. None → `other`.
- **Default branch**: `git remote show origin` or the current repository default.

## 1b. Choose where MegaLinter runs

MegaLinter can run in CI (Docker, every active linter), natively on the user's machine (a fast subset of the linters, no Docker, beta), or both. Ask the user (a structured question when your platform has one), unless the request already says it:

| Choice                               | Commands                                 | What runs where                                                                                                    |
|:-------------------------------------|:-----------------------------------------|:-------------------------------------------------------------------------------------------------------------------|
| **CI and native (recommended)**      | step 2 (`--install`), then "Native mode" | CI checks every active linter in Docker. The user's machine runs the `NATIVE_LINTERS` subset in seconds            |
| **CI only**                          | step 2 (`--install`)                     | CI checks every active linter. Local runs use Docker                                                               |
| **Native only** (no CI, or CI later) | "Native mode" alone, skip `--install`    | The user's machine runs the `NATIVE_LINTERS` subset. `--native-setup` creates `.mega-linter.yml` when it is absent |

- Without an answer (non-interactive run, or a request that only says "install MegaLinter"), do **CI only**.
- Always run `--install` **before** `--native-setup`: the installer backs up and overwrites `.mega-linter.yml`. When adding CI to a native-only repository, re-apply `NATIVE_LINTERS` from the `.megalinter-setup.bak` file.
- `NATIVE_LINTERS` is a subset of what CI runs: never copy the CI list into it.
- Native mode is the fast local path, not a replacement for Docker: it works next to CI and Docker, so do not offer it only to users without a container engine.
- Docker commands follow `MEGALINTER_VERSION`. Native commands follow the "Runner command" rule of the Native mode section, whatever `MEGALINTER_VERSION` says.

## 2. Install or upgrade

Skip this step for a **native-only** setup (go to the Native mode section), and for the other choices run it first.

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

**First determine how MegaLinter was installed**, because the two install modes update differently. Namespacing is
not a reliable signal: only some platforms prefix plugin skills with the plugin name (`megalinter:megalinter-setup`),
and no platform lets you query where a skill came from. Determine it from the filesystem, and ask the user when it
stays ambiguous:

| Evidence in the repository or user profile                                                                                  | Install mode |
|:----------------------------------------------------------------------------------------------------------------------------|:-------------|
| A MegaLinter plugin folder (`megalinter` under a `plugins/` directory of your platform)                                     | plugin       |
| `.claude/skills/megalinter*`, `.github/skills/megalinter*`, `.agents/skills/megalinter*` or the same under the user profile | skills       |
| Neither, or both                                                                                                            | ask the user |

**If it was installed as an agent plugin**, the skills CLI does not manage it: update the plugin instead, and skip the
rest of this section — the sub-agents are refreshed with it.

| Platform                 | Update command                                      |
|:-------------------------|:----------------------------------------------------|
| Claude Code              | `/plugin update megalinter@megalinter`              |
| Cursor                   | **Customize → Plugins**, then update **MegaLinter** |
| GitHub Copilot           | `copilot plugin install megalinter@megalinter`      |
| Codex                    | `codex plugin marketplace upgrade megalinter`       |
| Gemini CLI / Antigravity | `gemini extensions update megalinter`               |

Otherwise, check how they are installed:

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
- When the user chose native mode in step 1b (alone or with CI), follow "Native mode" below. Docker runs of a repository without `NATIVE_LINTERS` print a suggestion to try native mode, which points users to this skill; `NATIVE_SUGGESTIONS: false` hides it if they do not want native mode.
- Add `FILTER_REGEX_EXCLUDE` for generated or vendored folders (e.g. `(dist/|build/|vendor/|node_modules/)`). Excluded directories (and folders identified from these regexes) are also automatically forwarded to project-mode linters through their native exclusion arguments or generated ignore/config files; if the repository already maintains its own up-to-date ignore/config files for a linter, that forwarding can be turned off with `FORWARD_EXCLUDED_DIRECTORIES: false` (global) or `<LINTER_KEY>_FORWARD_EXCLUDED_DIRECTORIES: false` (per linter).

Validate the file against its JSON schema: <https://raw.githubusercontent.com/oxsecurity/megalinter/main/megalinter/descriptors/schemas/megalinter-configuration.jsonschema.json>

### Native mode (beta)

Native mode lints on the user's machine without Docker, and a run takes seconds. Recommend it next to CI (step 1b), and propose it when the user wants fast local checks, has no container engine, or asks for pre-commit hooks. For a **native-only** setup, run this section without `--install`.

**`NATIVE_LINTERS` is a subset of what CI runs.** CI keeps running every active linter: the variable only scopes local runs. Slow linters (spell checkers, type checkers, link checkers) and the ones scanning the whole repository (`REPOSITORY_*`, copy-paste detection) are better left to CI, so never copy the CI list into it, and say so to the user.

**Runner command**: use `mega-linter-runner` from `PATH` when its `--help` lists `--native-setup`, otherwise `npx mega-linter-runner@beta`. While native mode is in beta (until MegaLinter v11), a global runner installed before native mode lacks these options, so check `--help` instead of assuming. Never pass `--release` for native commands: `beta` is the default.

1. **Analyze** (no linter is run, nothing is installed):

   ```bash
   <runner> --native --prerun
   ```

   Read `megalinter-reports/prerun-report.json`. The suggestion whose `variable` is `NATIVE_LINTERS` has the recommended keys in `values` and one row per active linter in `details`: `recommended`, `reason`, `cli_lint_mode`, `linter_speed`, `measured_seconds` (from the previous run), `native_status`.

2. **Confirm with the user.** Show two lists, each linter with its `reason`: the ones proposed for native runs, and the ones left to CI. Let the user move linters between them. Never use `all` without their explicit, informed consent: it installs and trusts every matching linter.
3. **Apply** with the confirmed keys. This writes `NATIVE_LINTERS` in `.mega-linter.yml`, installs the linters and runs a first lint:

   ```bash
   <runner> --native-setup PYTHON_BLACK MARKDOWN_MARKDOWNLINT --json
   ```

   Without the runner option (`--help` does not list it) or when the prerun fails because the installed core does not know it, add `NATIVE_LINTERS` to `.mega-linter.yml` yourself, choosing the linters from the technologies of the repository, then run `<runner> --install-linters`.

   When the setup fails on a prerequisite (`uv`, Git Bash, a language runtime) and `--help` lists `--doctor`, run `<runner> --doctor` and relay its findings. Use `<runner>` for every native command: never call the `megalinter` engine or install it yourself, the runner is the only entry that verifies it.

4. **Offer pre-commit hooks.** Native mode does not run on commits by itself. Unless the user already answered, ask (a structured question when your platform has one):

   - **On commit only (recommended)**: `megalinter-native-incremental` lints the files of each commit
   - **On commit and push**: `megalinter-native-incremental`, plus `megalinter-native-full` on push
   - **No hooks**: skip the rest of this step

   Say before they answer that the hooks run `NATIVE_LINTERS`, **apply fixes** to the committed files, block the commit or push on an error, and that each teammate has to run `pre-commit install` once.

   If they accept:

   1. Take the newest `vX.Y.Z` tag, and check that it ships the native hooks:

      ```bash
      git ls-remote --tags --refs --sort=-v:refname https://github.com/oxsecurity/megalinter 'v*'
      curl -fsSL https://raw.githubusercontent.com/oxsecurity/megalinter/<tag>/.pre-commit-hooks.yaml | grep megalinter-native-incremental
      ```

   2. Add the hooks to `.pre-commit-config.yaml`. **Merge them into an existing file**, never replace it, and keep `megalinter-native-full` only for the commit and push choice. When the tag ships the hooks:

      ```yaml
      repos:
        - repo: https://github.com/oxsecurity/megalinter
          rev: vX.Y.Z
          hooks:
            - id: megalinter-native-incremental
              stages:
                - pre-commit
            - id: megalinter-native-full
              stages:
                - pre-push
      ```

      Then install the linters with the same version, as a hook can not ask questions: `npx mega-linter-runner@X.Y.Z --install-linters --release X.Y.Z`.

      When no release ships them yet, use local hooks on the beta runner instead (never `rev: main`, a moving reference):

      ```yaml
      repos:
        - repo: local
          hooks:
            - id: megalinter-native-incremental
              name: MegaLinter native (files of the commit)
              entry: npx --yes mega-linter-runner@beta --native --fix --env CLEAR_REPORT_FOLDER=true --env LOG_LEVEL=warning --filesonly
              language: system
              require_serial: true
              stages:
                - pre-commit
            - id: megalinter-native-full
              name: MegaLinter native
              entry: npx --yes mega-linter-runner@beta --native --fix --env CLEAR_REPORT_FOLDER=true --env LOG_LEVEL=warning
              language: system
              require_serial: true
              stages:
                - pre-push
      ```

   3. Make sure `megalinter-reports/` is in `.gitignore`.
   4. Activate the hooks, adding `--hook-type pre-push` for the commit and push choice. When `pre-commit` is missing, install it first with `uv tool install pre-commit`:

      ```bash
      pre-commit validate-config
      pre-commit install --hook-type pre-commit
      ```

   See <https://megalinter.io/latest/install-native/#pre-commit-hook>.

Requirements: `uv` and Node.js, plus Git Bash on Windows. Linters run with the user's privileges: native mode is for repositories the user trusts, and `--trust-repo-commands` is never passed on your own initiative.

## 4. Install or refresh the MegaLinter sub-agents (if your platform supports them)

This skill ships three sub-agent definitions in its `agents/` folder (`megalinter-watcher`, `megalinter-runner`, `megalinter-fixer`) that make the other MegaLinter skills faster and cheaper by keeping CI logs and linter output out of the main context.

**Skip this whole step if MegaLinter was installed as an agent plugin**: the plugin already ships the three
definitions (declared for Claude Code and Cursor, and carried as `com.github.copilot/agents/*.agent.md` for the
Copilot clients). Copying them again would install a second set that drifts on the next plugin update.

Confirm before skipping: check that the three agents are actually listed among the agents available to you, under
either their namespaced (`megalinter:megalinter-watcher`) or bare (`megalinter-watcher`) name. If they are not — the
platform may not load the plugin's agents — tell the user, and install them from `agents/` as described below.

If the coding agent you are running on supports custom sub-agent definitions (Claude Code, OpenCode, GitHub Copilot, Codex... — you know whether you do), read `agents/INSTALL.md` in this skill's directory and follow the instructions for your platform: copy the three `agents/*.md` files to your platform's agents folder, adapting the file name and the frontmatter when needed. Copilot in particular requires a `.agent.md` suffix in `.github/agents/`, and rejects the `model: haiku` override.

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
