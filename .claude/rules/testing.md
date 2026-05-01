---
description: Testing conventions for MegaLinter
globs: ["megalinter/tests/**/*.py", ".automation/test/**"]
---

# Testing Rules

## Test Structure
- Linter tests extend `LinterTestRoot` and `TestCase`
- Standard tests (`test_success`, `test_failure`, `test_get_linter_version`, `test_get_linter_help`) are inherited from `LinterTestRoot`
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
