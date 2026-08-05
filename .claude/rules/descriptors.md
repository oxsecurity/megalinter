---
description: Rules for working with MegaLinter YAML descriptor files — aim for maximum property completeness
globs: ["megalinter/descriptors/*.megalinter-descriptor.yml"]
---

# Descriptor File Rules

## Schema
Descriptor files conform to `megalinter/descriptors/schemas/megalinter-descriptor.jsonschema.json`. Only `descriptor_id`, `descriptor_type`, `linters` are required at descriptor level, and only `linter_name`, `linter_url`, `examples` at linter level — but **aim to fill every applicable property**.

## Maximize Property Coverage

When creating or modifying a linter entry, **search the internet** to gather all available metadata about the linter tool. Fill in all of these when applicable:

- **Identity**: `linter_name`, `linter_url`, `name`, `linter_text`, `linter_repo`, `examples`
- **Documentation URLs**: `linter_rules_url`, `linter_rules_configuration_url`, `linter_rules_inline_disable_url`, `linter_rules_ignore_config_url`
- **Metadata**: `linter_spdx_license`, `linter_speed` (1-5), `linter_image_url`, `linter_icon_png_url`, `linter_banner_image_url`
- **CLI config**: `cli_lint_mode` (default mode), `supported_cli_lint_modes` (all modes the linter can run in — `file`, `list_of_files`, `project`; defaults to `["file"]`, must include `cli_lint_mode`), `cli_executable`, `config_file_name`, `cli_config_arg_name`, `cli_lint_extra_args`, `cli_lint_fix_arg_name`, `cli_lint_fix_remove_args`, `ignore_file_name`, `cli_lint_ignore_arg_name`, `cli_lint_mode_file_extra_args_after` / `cli_lint_mode_list_of_files_extra_args_after` / `cli_lint_mode_project_extra_args_after` (per-mode trailing args)
- **Project-mode directory exclusions**: `cli_lint_mode_project_exclude_arg_name`, `cli_lint_mode_project_exclude_arg_value`, `cli_lint_mode_project_exclude_separator` (see below)
- **Error parsing**: `cli_lint_errors_count`, `cli_lint_errors_regex`
- **Known non-lint failures**: `common_linter_errors` — list of `{identifier, regex, message}` entries for config/environment errors (service unavailable, missing credentials, malformed config, etc.) that should surface guidance to the user. Only evaluated on non-success. Each entry MUST have an `identifier` starting with the linter key followed by `_ERROR_` (e.g. `REPOSITORY_OSV_SCANNER_ERROR_SERVICE_UNAVAILABLE`). Each `regex` must be specific enough not to match normal lint output; avoid `.*` or single-word patterns. Entries are rendered as a "Known errors and resolutions" section at the end of the generated linter doc page.
- **SARIF**: `can_output_sarif`, `cli_sarif_args`, `sarif_default_output_file`
- **Behavior**: `is_formatter`, `activation_rules`, `active_only_if_file_found`
- **IDE**: `ide` with entries for `vscode`, `idea`, `eclipse`, `sublime`, `emacs` etc.
- **Platforms**: `supported_platforms` with `install_override` for ARM when needed
- **Install**: with renovate-compatible version pinning

## Project Lint Mode: Forwarding Excluded Directories

Linters running in `project` lint mode scan the whole workspace themselves, so MegaLinter's `EXCLUDED_DIRECTORIES` / `ADDITIONAL_EXCLUDED_DIRECTORIES` are otherwise ignored. When the tool has a **native CLI exclusion flag**, declare it so `Linter.build_project_exclude_arguments()` forwards each excluded directory automatically:

```yaml
cli_lint_mode_project_exclude_arg_name: "--ignore-pattern"   # native CLI flag
cli_lint_mode_project_exclude_arg_value: "**/{{DIR}}/**"     # value template, {{DIR}} = directory name
cli_lint_mode_project_exclude_separator: ","                 # only if the flag is NOT repeatable
cli_lint_mode_project_exclude_seed_values: ["**/.git/**"]    # defaults to re-include when the flag REPLACES the tool's built-in defaults
# When the tool takes an ignore FILE instead of inline values:
cli_lint_mode_project_exclude_ignore_file_arg_name: "--ignore-path"          # argument receiving the generated ignore file
cli_lint_mode_project_exclude_ignore_file_seed_files: [".toolignore"]        # workspace files merged into it (first existing wins)
cli_lint_mode_project_exclude_ignore_file_pass_existing: [".gitignore"]      # files re-passed via the same arg when it replaces their discovery
cli_lint_mode_project_exclude_ignore_file_skip_if_config: true               # skip when a config file is resolved
# When the tool only discovers ignore files inside the analyzed repository:
cli_lint_mode_project_exclude_workspace_file_name: ".toolignore"             # written at workspace root only if absent, removed after the run
```

Rules:

- `cli_lint_mode_project_exclude_arg_name` — only a **CLI flag** qualifies. An ignore-file mechanism (`.eslintignore`, `.csharpierignore`) does not: use `ignore_file_name` / `cli_lint_ignore_arg_name` for that. A rule/check disabling flag never qualifies.
- If the arg name ends with `=` or `:` (e.g. `--ignore=`), the value is concatenated to it; otherwise the flag and value are passed as two argv entries.
- `cli_lint_mode_project_exclude_arg_value` — defaults to `{{DIR}}`. Set a glob/regex template matching the tool's own syntax, e.g. `**/{{DIR}}/**` (glob), `./{{DIR}}/**`, `(^|/){{DIR}}/` (regex).
- `cli_lint_mode_project_exclude_separator` — set **only** when the tool does not accept a repeated flag (a second occurrence would override the first, e.g. `,` for comma-separated lists, `|` for regex alternation). Leave unset when the flag accumulates, so it is repeated once per directory.
- **Verify against official docs** which of the three behaviors the tool has (repeatable / comma-separated / literal-paths-only) before filling these — a wrong choice silently drops exclusions.
- Add a test in `megalinter/tests/test_megalinter/` covering the generated command line when adding this to a linter.

## Installation Version Pinning

Always use renovate-compatible comments:
```yaml
install:
  dockerfile:
    - |-
      # renovate: datasource=pypi depName=tool-name
      ARG PIP_TOOL_VERSION=1.2.3
  pip:
    - tool-name==${PIP_TOOL_VERSION}
```

## Naming
- `descriptor_id` UPPERCASE (e.g., `PYTHON`)
- `linter_name` lowercase matching CLI executable
- Generated name: `DESCRIPTOR_LINTERNAME` (e.g., `PYTHON_PYLINT`)

## Test Fixtures (Mandatory)
Every linter must have files in `.automation/test/<test_folder>/`:
- Good file (passes linting)
- Bad file (triggers errors matching `cli_lint_errors_regex`)

## After Modifying
Run `make megalinter-build` to regenerate Dockerfiles, test classes, schemas. **Never run `make megalinter-build-with-doc`** — documentation is handled by auto-update workflows and generating docs in PRs causes merge conflicts.
