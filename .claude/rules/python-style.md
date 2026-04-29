---
description: Python coding conventions specific to MegaLinter
globs: ["megalinter/**/*.py", ".automation/**/*.py", "server/**/*.py"]
---

# Python Style Rules for MegaLinter

## Imports
- Place all imports at the top of the file, never inline or conditional
- Do not test if imports work (no try/except ImportError) — assume all packages are always available
- Use `from megalinter import config` then `config.get(self.request_id, "VAR", default)` for configuration access

## Docstrings and Comments
- Do NOT add docstrings to classes or methods
- Only add comments where the logic is non-obvious

## Configuration Access
- Always use `megalinter.config.get(request_id, "VARIABLE_NAME", "default_value")` — never access env vars directly with `os.environ`
- The `request_id` parameter is required for multi-tenant support (server mode)

## Linter Subclasses
- Custom linter classes go in `megalinter/linters/` and must extend `megalinter.Linter`
- Override only the methods you need: `build_lint_command()`, `before_lint_files()`, `complete_command_line()`, `build_version_command()`
- Keep custom classes minimal — most config belongs in the YAML descriptor, not Python code

## Error Handling
- Use `logging` module for all output, never `print()`
- Do not add defensive error handling for internal code paths — trust internal APIs
