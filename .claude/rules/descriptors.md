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
# When the tool only discovers ignore files inside the analyzed repository:
cli_lint_mode_project_exclude_workspace_file_name: ".toolignore"             # written at workspace root only if absent, removed after the run
```

One more property preserves config-file lists that the CLI flag would replace:

```yaml
cli_lint_mode_project_exclude_config_key: "scan.skip-dirs"   # dotted key path of the resolved config list the flag REPLACES: its entries are re-emitted first
```

**Choosing the mechanism** (exactly ONE per linter — the base class applies all declared mechanisms, so declaring two forwards twice):

1. Native CLI exclusion flag → `..._exclude_arg_name` (+ value template / separator / seed values / config key).
2. Flag taking an ignore FILE → `..._exclude_ignore_file_*` (generated in the report folder, merged with seeds).
3. Tool only discovers ignore files inside the repo → `..._exclude_workspace_file_name` (temp file at workspace root, only if absent, auto-removed).
4. Anything needing a generated/merged CONFIG (yamllint extends, rubocop inherit_from, phpstan includes, TOML/PHP configs…) → override `manage_excluded_directories_config(cmd)` in the linter class. It is called only in project mode when forwarding is active (single gate: `is_project_exclude_forwarding_active`, overridable via `FORWARD_EXCLUDED_DIRECTORIES` / `<LINTER_KEY>_FORWARD_EXCLUDED_DIRECTORIES`). Use the base helpers `find_cli_argument_value_index`, `replace_or_append_cli_argument`, `write_report_generated_file`, `write_workspace_generated_file`, `read_workspace_file_lines`, and call `log_project_exclude_forwarding` so the action shows in the console log.

Rules and known traps (each was hit for real — verify against official docs/source before filling anything):

- Only a **CLI flag** qualifies for mechanism 1. An ignore-file flag is mechanism 2; a rule/check-disabling flag never qualifies (perlcritic/rubocop `--exclude` are RULES).
- Arg name ending with `=`/`:` → value concatenated; empty arg name `""` → bare positional values (ktlint/jsonlint negated globs).
- `..._exclude_arg_value` defaults to `{{DIR}}`; templates go through `replace_vars`, so `{{WORKSPACE}}` is available. Anchor on it when the tool matches patterns against absolute enumerated paths (jsonlint). Prefix `./` when the tool fnmatches `./`-walked paths (bandit).
- `..._exclude_separator` — set ONLY when a repeated flag overrides the previous occurrence (phpcs `--ignore=` is even first-wins). Unset = flag repeated per directory.
- `..._exclude_seed_values` — when the flag REPLACES the tool's built-in defaults (bandit `-x`, devskim `-g`), re-include them here, in the tool's own matching syntax.
- `..._exclude_config_key` — when the flag REPLACES the same list in the tool's config file (checkov `skip-path`, grype/syft `exclude`, trivy `scan.skip-dirs`, devskim `Globs`), name that key so the resolved config's entries are preserved. Without it, forwarding silently discards the user's configured exclusions.
- **Custom classes overriding `build_lint_command` WITHOUT calling `super()`** (e.g. JavaPmdLinter) bypass all forwarding: they must apply `build_project_exclude_arguments()` themselves in their project branch, gated by `is_project_exclude_forwarding_active()`.
- Glob semantics differ per tool: `**/` prefix requirements (grype/syft error without `./`, `*/` or `**/`), dot-directory handling, quantifier traps. When unsure, prefer the form the tool's own docs use.
- Only excluded directories **existing at the workspace root** are forwarded (`get_project_exclude_directories`): arguments and generated files stay minimal, and nothing is forwarded at all when none exists. Custom classes calling forwarding outside the base gate must apply the same `len(self.get_project_exclude_directories()) > 0` guard.

**Poison fixture (mandatory when adding forwarding):** create a deliberately failing file for the linter inside `.automation/test/<test_folder>/good/.wireit/` (`.wireit` is a default excluded directory that almost no tool skips natively). The `test_success_project_lint_mode` test then fails if forwarding regresses. Only do this when every project-capable linter sharing the test folder has forwarding, and only in folders with a `good/` subfolder. See `.claude/rules/testing.md`.

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
