---
name: review-descriptor
description: Audit a linter descriptor YAML for completeness, correctness, and best practices. Checks all properties against the full schema.
allowed-tools: Read Grep Glob Bash WebSearch WebFetch
argument-hint: [descriptor-file-or-linter-name]
---

Review the descriptor for `$ARGUMENTS`. If a linter name is given, find its descriptor in `megalinter/descriptors/`.

For each linter entry, audit against the **full property list** below. Report a checklist with status for each category.

## 1. Identity (required)
- [ ] `linter_name` — present, lowercase, matches CLI executable
- [ ] `linter_url` — valid URL to tool docs/website
- [ ] `examples` — at least 2: one plain, one with config file

## 2. Documentation Quality
- [ ] `linter_text` — rich description with features, what it checks, use cases
- [ ] `linter_repo` — GitHub/source repository URL
- [ ] `linter_rules_url` — URL listing all rules/checks
- [ ] `linter_rules_configuration_url` — how to configure
- [ ] `linter_rules_inline_disable_url` — how to suppress inline
- [ ] `linter_rules_ignore_config_url` — how to use ignore files
- [ ] `linter_spdx_license` — valid SPDX ID (e.g., MIT, Apache-2.0)
- [ ] `linter_speed` — rated 1-5 (check if realistic)
- [ ] `linter_image_url` or `linter_icon_png_url` or `linter_banner_image_url` — at least one image

## 3. CLI Configuration
- [ ] `cli_lint_mode` — set to `file`, `list_of_files`, or `project`
- [ ] `config_file_name` — set if linter uses a config file
- [ ] `cli_config_arg_name` — set if config file is used
- [ ] `cli_lint_fix_arg_name` — set if linter supports auto-fix
- [ ] `cli_lint_fix_remove_args` — set if fix mode requires removing args (e.g., `--check`)
- [ ] `ignore_file_name` + `cli_lint_ignore_arg_name` — set if linter has ignore files
- [ ] `cli_version_arg_name` — set if not `--version`
- [ ] `cli_help_arg_name` — set if not `--help`

## 4. Error Parsing
- [ ] `cli_lint_errors_count` — set (`regex_count`, `regex_number`, `regex_sum`, `total_lines`, or `sarif`)
- [ ] `cli_lint_errors_regex` — set and matches actual linter output format

## 5. SARIF Support
- [ ] If linter supports SARIF: `can_output_sarif: true`, `cli_sarif_args` with `{{SARIF_OUTPUT_FILE}}`
- [ ] If not: confirmed that tool doesn't support SARIF output (**search the internet** to verify)

## 6. Install & Platforms
- [ ] `install` section with proper renovate-compatible `# renovate: datasource=...` comments
- [ ] Version explicitly pinned (no `@latest` in production)
- [ ] `supported_platforms` lists linux/amd64 (and linux/arm64 if applicable)
- [ ] `install_override` for ARM if install differs by platform

## 7. IDE Integration
- [ ] `ide.vscode` — VS Code extension listed (if one exists; **search** if unsure)
- [ ] `ide.idea` — JetBrains/IntelliJ extension listed (if available)
- [ ] Other IDEs checked: `eclipse`, `sublime`, `emacs`, `atom`, `visual_studio`

## 8. Test Fixtures
- [ ] `.automation/test/<test_folder>/` exists
- [ ] Contains at least one good (clean) file
- [ ] Contains at least one bad (has errors) file
- [ ] Bad file errors match `cli_lint_errors_regex` pattern

## 9. Behavior Flags
- [ ] `is_formatter` — set to `true` if it's a formatter
- [ ] `activation_rules` — set if depends on env vars (e.g., style choice)
- [ ] `active_only_if_file_found` — set if should only run when config exists
- [ ] `deprecated`/`disabled` — correct if applicable

## 10. Flavor Assignment
- [ ] `descriptor_flavors` is appropriate for the language
- [ ] Cross-check against existing flavors in `flavors/`
- [ ] `descriptor_flavors_exclude` set if needed

## Summary

After the checklist, provide:
- **Missing properties** that should be added (with suggested values when possible)
- **Incorrect values** that should be fixed
- **Internet search** results for any missing documentation URLs, IDE extensions, or SARIF support
