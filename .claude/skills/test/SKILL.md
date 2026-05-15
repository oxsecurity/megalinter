---
name: test
description: Build the MegaLinter Docker image and run the targeted linter tests to verify the implementation. Fourth step of the contribution workflow, use after /implement.
disable-model-invocation: true
allowed-tools: Read Glob Grep Write Edit Bash
argument-hint: "[linter or test focus]"
---

You are a QA engineer for the **MegaLinter** project.

Verify the implementation by regenerating from descriptors, building the linter image, and running targeted tests inside Docker. **Linters are not installed locally** — tests must run in containers.

## Process

1. **Regenerate from descriptors** (after any descriptor or build-logic change):

   ```bash
   make megalinter-build
   ```

   **Never run `make megalinter-build-with-doc`** — docs are owned by auto-update workflows.

   If `make megalinter-build` fails, delegate to the `build-runner` agent.

2. **Identify the test target**:
   - Single linter: `LINTER="<descriptor_id_lowercase>_<linter_name>"` (e.g. `python_ruff`).
   - Multiple linters in the same descriptor: build each image separately.
   - The test file is `megalinter/tests/test_megalinter/linters/${LINTER}_test.py` (auto-generated — don't edit).

3. **Build and run the linter image**:

   ```bash
   LINTER="python_ruff"
   docker buildx build --platform linux/amd64 --file linters/$LINTER/Dockerfile --tag $LINTER .
   docker run --rm \
     --env TEST_CASE_RUN=true \
     --env OUTPUT_DETAIL=detailed \
     --env TEST_KEYWORDS="${LINTER}_test" \
     --env MEGALINTER_VOLUME_ROOT="." \
     --volume "$(pwd):/tmp/lint" \
     $LINTER
   ```

   Faster iteration on a single method:

   ```bash
   --env TEST_KEYWORDS="${LINTER}_test and test_failure"
   ```

   For ARM coverage: `--platform linux/arm64`.

4. **Python-only checks** (for core changes in `megalinter/`):
   - Activate the venv (`source .venv/bin/activate` or `source .venv/Scripts/activate` on Windows).
   - Run targeted pytest only if the test doesn't require a linter binary: `pytest megalinter/tests/test_megalinter/<test>.py`.
   - Most linter tests need Docker — don't try to run them on the host.

5. **Fix issues** (or delegate to `test-debugger` for deeper triage):
   - Fixture file extension doesn't match descriptor `file_extensions` / `file_names_regex` → fix fixture filename.
   - `cli_lint_errors_regex` doesn't match real linter output → adjust regex in descriptor, re-run `make megalinter-build`.
   - Version pin broken → check upstream registry, bump the `ARG ..._VERSION=...` in the descriptor.
   - ARM fails but amd64 passes → add `install_override` under `supported_platforms`.
   - Test class out of date → re-run `make megalinter-build`; never edit the generated test file.
   - Custom class bug → check `megalinter/linters/<class>.py`; keep overrides minimal.
   - `config.get()` missing `request_id` → fix (required for server mode).
   - `os.environ` direct access → switch to `megalinter.config.get(...)`.
   - `print()` calls → switch to `logging`.

6. **Markdown checks** (for any docs touched): mkdocs-material requires blank lines after headings and around lists. Visual check with `hatch run docs:serve` (`http://127.0.0.1:8000`).

7. **Report**:
   - Tests run, pass/fail counts, platforms covered.
   - Build success and regenerated files.
   - Remaining issues with next steps.

## Common Issues

- Linter behavior differs between host and Alpine container → trust the container; adjust descriptor.
- `cli_lint_mode` mismatch (`file` vs `list_of_files` vs `project`) → align with how the tool actually runs.
- Missing config file referenced by `config_file_name` → add to `.automation/test/<test_folder>/`.
- Dockerfile install fails on ARM → use `install_override` per platform.

## CI Notes

- `quick build` in commit message body skips a full Docker rebuild (~15 min vs ~45 min) — fine for iterations.
- `TEST_KEYWORDS=<linter>_test` in commit body filters CI to one linter's tests.
- Maintainers can comment `/build` on a PR to trigger the build workflow.
- The last commit before PR merge must be a full build.

Continue fixing and re-running until all checks pass. Do not stop to ask mid-loop.

$ARGUMENTS
