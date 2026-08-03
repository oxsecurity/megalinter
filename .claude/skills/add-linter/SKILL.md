---
name: add-linter
description: Guided workflow for adding a new linter to MegaLinter. Use when a contributor needs to add support for a new linting tool.
allowed-tools: Read Grep Glob Bash Edit Write WebSearch WebFetch
argument-hint: [linter-name]
model: sonnet
---

Guide me through adding the linter `$ARGUMENTS` to MegaLinter. If no linter name was provided, ask me for:
1. The linter tool name (CLI executable)
2. The language/format it lints
3. Whether it belongs to an existing descriptor or needs a new one

## Step 1 — Research the Linter

**Search the internet** to gather all available information about the linter:
- Official website URL and GitHub repository URL
- Rules/checks listing URL
- Configuration file format and default filename
- CLI flags: lint command, fix flag, version flag, help flag, config arg
- SARIF output support (can it output SARIF?)
- Available IDE extensions (VS Code, JetBrains, Sublime, Emacs, Eclipse, Atom, Visual Studio)
- SPDX license identifier (MIT, Apache-2.0, GPL-2.0, etc.)
- Whether it's a formatter (`is_formatter: true`) or a linter
- Current latest stable version for pinning
- What package manager installs it (pip, npm, apk, gem, cargo, or raw Dockerfile)
- Supported platforms (linux/amd64, linux/arm64)
- Ignore file support (e.g., `.eslintignore`)

## Step 2 — Create/Update the Descriptor

Check if a descriptor exists in `megalinter/descriptors/` for this language. If not, create a new `<lang>.megalinter-descriptor.yml`.

Add the linter entry with **as many properties as possible**. Even though the JSON schema only requires `linter_name`, `linter_url`, and `examples`, aim for maximum completeness. Fill in ALL of these when applicable:

**Identity (required):**
- `linter_name` — CLI executable name, lowercase
- `linter_url` — tool website
- `examples` — CLI usage (with and without config file)

**Documentation (strongly recommended):**
- `linter_text` — rich markdown description: features, what it checks, when to use it
- `linter_repo` — GitHub repository URL
- `linter_rules_url` — URL listing all rules
- `linter_rules_configuration_url` — how to configure
- `linter_rules_inline_disable_url` — how to suppress rules inline
- `linter_rules_ignore_config_url` — how to ignore files
- `linter_spdx_license` — SPDX license ID
- `linter_speed` — 1 (very slow) to 5 (very fast)
- `linter_image_url`, `linter_icon_png_url`, `linter_banner_image_url` — logos/banners

**CLI configuration (always fill):**
- `cli_lint_mode` — default mode: `file`, `list_of_files`, or `project`
- `supported_cli_lint_modes` — every mode the linter can run in (subset of `file` / `list_of_files` / `project`; defaults to `["file"]`, must include `cli_lint_mode`). Success/failure tests run once per declared mode, so only list modes the tool actually supports
- `cli_executable` — if different from `linter_name`
- `config_file_name` — default config file (e.g., `.pylintrc`)
- `cli_config_arg_name` — config argument (e.g., `--config`)
- `cli_lint_extra_args` — default extra arguments
- `cli_lint_fix_arg_name` — fix argument (e.g., `--fix`)
- `cli_lint_fix_remove_args` — args to remove in fix mode
- `cli_version_arg_name` — if not `--version`
- `cli_help_arg_name` — if not `--help`
- `ignore_file_name`, `cli_lint_ignore_arg_name` — ignore file support

**Error parsing (important for accurate counts):**
- `cli_lint_errors_count` — `regex_count`, `regex_number`, `regex_sum`, `total_lines`, or `sarif`
- `cli_lint_errors_regex` — regex matching error lines in output

**SARIF support (if available):**
- `can_output_sarif: true`
- `cli_sarif_args` — with `{{SARIF_OUTPUT_FILE}}` placeholder

**Behavior flags:**
- `is_formatter: true` — if it's a formatter
- `activation_rules` — if it depends on env vars (e.g., style preference)
- `active_only_if_file_found` — only activate if certain config files exist

**Install (required):**
- Use renovate-compatible version pinning:
  ```yaml
  install:
    dockerfile:
      - |-
        # renovate: datasource=pypi depName=tool-name
        ARG PIP_TOOL_VERSION=1.2.3
    pip:
      - tool-name==${PIP_TOOL_VERSION}
  ```
- Set `supported_platforms` with `install_override` for ARM if needed

**IDE section (always fill):**
- `ide.vscode`, `ide.idea`, `ide.eclipse`, `ide.sublime`, `ide.emacs`, `ide.atom`, `ide.visual_studio`
- Each: `[{name: "Extension Name", url: "marketplace-url"}]`

**Testing:**
- `test_folder` — if different from lowercase descriptor_id
- `test_variables` — env vars for tests

Look at existing well-populated descriptors like `megalinter/descriptors/python.megalinter-descriptor.yml` for reference.

## Step 3 — Test Fixtures

Create two test files in `.automation/test/<test_folder>/`:
- A "good" file that passes linting cleanly
- A "bad" file that triggers at least one lint error matching `cli_lint_errors_regex`

## Step 4 — Custom Class (only if needed)

Create a minimal class in `megalinter/linters/` extending `megalinter.Linter`. Only override what the YAML descriptor can't express.

## Step 5 — Build

Run `make megalinter-build` to auto-generate Dockerfiles, test classes, schemas.

**Do NOT run `make megalinter-build-with-doc`** — documentation is handled by auto-update workflows and generating it in PRs causes merge conflicts.

## Step 6 — Validate in Docker

```bash
LINTER="<descriptor_id_lowercase>_<linter_name>"
docker buildx build --platform linux/amd64 --file linters/$LINTER/Dockerfile --tag $LINTER .
docker run --rm --env TEST_CASE_RUN=true --env OUTPUT_DETAIL=detailed \
  --env TEST_KEYWORDS="${LINTER}_test" --env MEGALINTER_VOLUME_ROOT="." \
  --volume "$(pwd):/tmp/lint" $LINTER
```

## Step 7 — Finalize

- Add one line under **New linters** in `CHANGELOG.md` (repo root, beta section):
  ```text
  - Add [linter-name](linter_url) linter for <language> — <what it detects, one sentence>
  ```
- Branch naming: `user/add-<linter-name>`
- Use `quick build` + `TEST_KEYWORDS=<linter>_test` in commit message body during dev
- Last commit before PR merge must be a full build (~45 min)
