---
description: Testing conventions for MegaLinter
globs: ["megalinter/tests/**/*.py", ".automation/test/**"]
---

# Testing Rules

## Test Structure
- Linter tests extend `LinterTestRoot` and `TestCase`
- Standard tests are inherited from `LinterTestRoot`: `test_get_linter_version`, `test_get_linter_help`, `test_report_tap`, `test_report_sarif`, plus one success and one failure test **per CLI lint mode** — `test_success_file_lint_mode`, `test_success_list_of_files_lint_mode`, `test_success_project_lint_mode`, and the matching `test_failure_*_lint_mode`
- Each per-mode test is automatically skipped when that mode is not listed in the descriptor's `supported_cli_lint_modes`. So a linter's success/failure fixtures are now exercised in **every** mode it declares support for, not only the default `cli_lint_mode` — fixtures must pass/fail correctly in all declared modes
- **CI optimization**: when a linter supports both `file` and `list_of_files`, the `file`-mode tests are skipped (`list_of_files` exercises the same code path more cheaply). This skip lives in `LinterTestRoot.run_lint_mode_test`
- The old `test_success` / `test_failure` methods no longer exist (renamed to the per-mode variants above). A pytest `-k` filter of `test_failure` still matches all three `test_failure_*_lint_mode` tests via substring matching
- Test files in `megalinter/tests/test_megalinter/linters/` are auto-generated — don't edit ones with the `@generated` header

## Test Fixtures
- Place test fixtures in `.automation/test/<language_or_test_folder>/`
- Include both good (passing) and bad (failing) example files
- Bad files must trigger at least one lint error from the target linter

## Running Tests
- Linter tests require Docker because the actual linter tools are not installed locally
- Use the `TEST_KEYWORDS` environment variable to filter tests (e.g., `TEST_KEYWORDS=python_ruff_test`)
- pytest is used with `pytest-xdist` for parallel execution, `pytest-timeout` (300s), and `pytest-rerunfailures`

## Test Utilities
- Use `megalinter.utilstest` helpers: `linter_test_setup()`, `test_linter_success()`, `test_linter_failure()`
- Initialize tests with `linter_test_setup({"request_id": str(uuid.uuid1())})`
