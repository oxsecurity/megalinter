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
- **CLI config**: `cli_lint_mode`, `cli_executable`, `config_file_name`, `cli_config_arg_name`, `cli_lint_extra_args`, `cli_lint_fix_arg_name`, `cli_lint_fix_remove_args`, `ignore_file_name`, `cli_lint_ignore_arg_name`
- **Error parsing**: `cli_lint_errors_count`, `cli_lint_errors_regex`
- **SARIF**: `can_output_sarif`, `cli_sarif_args`, `sarif_default_output_file`
- **Behavior**: `is_formatter`, `activation_rules`, `active_only_if_file_found`
- **IDE**: `ide` with entries for `vscode`, `idea`, `eclipse`, `sublime`, `emacs` etc.
- **Platforms**: `supported_platforms` with `install_override` for ARM when needed
- **Install**: with renovate-compatible version pinning

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
