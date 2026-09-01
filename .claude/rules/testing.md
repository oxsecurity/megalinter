---
description: Testing conventions for MegaLinter
globs: ["megalinter/tests/**/*.py", ".automation/test/**"]
---

# Testing Rules

## Test Structure
- Linter tests extend `LinterTestRoot` and `TestCase`
- Standard tests are inherited from `LinterTestRoot`: `test_get_linter_version`, `test_get_linter_help`, `test_report_sarif`, plus one success and one failure test **per CLI lint mode**
- TAP reporter golden-file tests are NOT per-linter: they live in `tap_reporter_test.py` on a curated sample of linters (bash, css, protobuf, cloudformation) — do not add `expected-*.tap` files for other linters — `test_success_file_lint_mode`, `test_success_list_of_files_lint_mode`, `test_success_project_lint_mode`, and the matching `test_failure_*_lint_mode`
- Each per-mode test is automatically skipped when that mode is not listed in the descriptor's `supported_cli_lint_modes`. So a linter's success/failure fixtures are now exercised in **every** mode it declares support for, not only the default `cli_lint_mode` — fixtures must pass/fail correctly in all declared modes
- **CI optimization**: when a linter supports both `file` and `list_of_files`, the `file`-mode tests are skipped (`list_of_files` exercises the same code path more cheaply). This skip lives in `LinterTestRoot.run_lint_mode_test`
- The old `test_success` / `test_failure` methods no longer exist (renamed to the per-mode variants above). A pytest `-k` filter of `test_failure` still matches all three `test_failure_*_lint_mode` tests via substring matching
- Test files in `megalinter/tests/test_megalinter/linters/` are auto-generated — don't edit ones with the `@generated` header

## Test Fixtures
- Place test fixtures in `.automation/test/<language_or_test_folder>/`
- Include both good (passing) and bad (failing) example files
- Bad files must trigger at least one lint error from the target linter

## Poison Fixtures (excluded directories forwarding guard)
- Linters that forward `EXCLUDED_DIRECTORIES` in project lint mode (descriptor `cli_lint_mode_project_exclude_*` properties or a `manage_excluded_directories_config()` override) have a **poison fixture**: a deliberately failing file inside `.automation/test/<test_folder>/good/.wireit/`
- `.wireit` is a default excluded directory that almost no tool skips natively, so `test_success_project_lint_mode` passes only if the forwarding actually excludes it — the fixture is a regression test for the forwarding, not for the linter rules
- Excluded directories are matched by basename **at any nesting level**, so a linter that forwards them also gets a nested poison in `.automation/test/<test_folder>/good/infrastructure/.wireit/`, guarding the nested forwarding fixed in issue #8806. Present for `REPOSITORY_BETTERLEAKS`, and for every linter whose value template is `{{DIR_PATH}}` — `PYTHON_BANDIT`, `YAML_V8R`, `CSHARP_DOTNET_FORMAT`, `VBDOTNET_DOTNET_FORMAT`, `REPOSITORY_LS_LINT` — whose root-anchored patterns are the code path that nesting actually exercises
- When adding forwarding to a linter, add its poison fixture; when a project success test fails on a file under `.wireit/`, the forwarding is broken, not the fixture
- Constraints: only in folders with a `good/` subfolder, and only when every project-capable linter sharing the test folder has forwarding (otherwise the poison legitimately fails the non-forwarding tenant)
- No poison fixture for a linter that can not receive exclusions at all (coffeelint, sqlfluff): its `good/` folder must stay clean, and the limitation is documented in the descriptor `linter_text` instead
- Poisons may be vacuous for tools that natively skip the directory (dot-folder-skipping globs, verified-only secret scanners): they never false-fail, so that is acceptable

## Running Tests
- Linter tests require Docker because the actual linter tools are not installed locally
- Use the `TEST_KEYWORDS` environment variable to filter tests (e.g., `TEST_KEYWORDS=python_ruff_test`)
- pytest is used with `pytest-xdist` for parallel execution, `pytest-timeout` (300s), and `pytest-rerunfailures`

## Test Utilities
- Use `megalinter.utilstest` helpers: `linter_test_setup()`, `test_linter_success()`, `test_linter_failure()`
- Initialize tests with `linter_test_setup({"request_id": str(uuid.uuid1())})`
