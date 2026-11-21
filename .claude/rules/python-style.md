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
- In a linter module, module-level helper functions (ex: a converter of the output of the linter to SARIF) are declared **after** the class, never before it. Constants and imports stay at the top
- Linters whose findings are one line of text each need no Python code: declare `can_output_sarif: true` and `sarif_text_regex` (named groups `path`, `line`, `column`, `end_column`, `rule`, `severity`, `message`, `cell`) in the descriptor, with `sarif_text_levels` to map a `severity` group to `error`, `warning` or `note`, and `sarif_whole_output: true`. Formatters that check formatting by printing a unified diff declare `sarif_unified_diff: true` instead (one result per file, at its first hunk), with `sarif_text_default_level: note` and `sarif_text_default_message`. Force a stable output format in `cli_sarif_args` (no colors, one finding per line). Test the regex as shipped, with `sarif_text_converters_test.py`
- Linters that can not output SARIF otherwise build it by overriding `convert_output_to_sarif()` with the helpers of `megalinter/sarif_builder.py`: the conversion works in Docker and in native mode (never depend on a binary that exists only in the Docker image)

## Error Handling
- Use `logging` module for all output, never `print()`
- Do not add defensive error handling for internal code paths — trust internal APIs
