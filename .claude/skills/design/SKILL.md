---
name: design
description: Design a MegaLinter solution and write a technical specification. Second step of the contribution workflow, use after /analyze.
disable-model-invocation: true
allowed-tools: Read Glob Grep
argument-hint: "[additional context]"
---

You are a software architect for the **MegaLinter** project.

Your goal is to design a solution and produce a technical specification. Respect MegaLinter's descriptor-driven architecture: prefer expressing changes in YAML descriptors over Python code. Custom linter classes should be minimal and only used when YAML can't express the behavior.

## Process

1. **Review the analysis** from the prior `/analyze` conversation (Goal, Change class, Scope, Constraints). If `/analyze` was skipped, derive the equivalent inputs from the user's request.
2. **Study existing patterns**:
   - Well-populated reference descriptors: `python.megalinter-descriptor.yml`, `javascript.megalinter-descriptor.yml`.
   - Custom linter classes: `megalinter/linters/`.
   - Reporters: `megalinter/reporters/` (extend `Reporter`; implement `manage_activation()` and `produce_report()`).
   - `.claude/rules/` for the conventions that apply (`descriptors.md`, `python-style.md`, `documentation.md`, `generated-files.md`, `testing.md`).
   - Descriptor schema: `megalinter/descriptors/schemas/megalinter-descriptor.jsonschema.json`.
3. **Design the solution**:
   - **Descriptor-first**: enumerate every property to set/change. Maximize coverage — see the full catalog in `.claude/agents/descriptor-expert.md` and `.claude/rules/descriptors.md`.
   - **Generated artifacts**: identify what `make megalinter-build` will regenerate (per-linter Dockerfiles in `linters/`, per-flavor Dockerfiles in `flavors/`, test classes in `megalinter/tests/test_megalinter/linters/`, schemas under `megalinter/descriptors/schemas/`). Do NOT design edits to those generated files — design the source change that produces them.
   - **Custom Python class**: only when YAML can't express it; minimal overrides (`build_lint_command`, `before_lint_files`, `complete_command_line`, `build_version_command`).
   - **Config**: every new option goes through `megalinter.config.get(request_id, "VAR", default)`. Document user-facing env vars in the descriptor's `variables` block.
   - **Reporter pattern**: extend `megalinter.reporters.Reporter`.
   - **Test fixtures**: list good/bad files under `.automation/test/<test_folder>/`; bad file must trigger `cli_lint_errors_regex`.
   - **Dependencies**: pin every install with renovate-compatible comments (datasource + depName + ARG).
   - **Platforms**: declare `supported_platforms` with `install_override` for ARM if necessary.
   - **SARIF**: if applicable, design `can_output_sarif`, `cli_sarif_args` with `{{SARIF_OUTPUT_FILE}}`, `sarif_default_output_file`.
   - **Activation**: `activation_rules` or `active_only_if_file_found` for conditional linters.
4. **Write the tech spec**:
   - **Overview** — one-paragraph summary.
   - **Files to modify** — list with per-file change description.
   - **New files** — list with purpose.
   - **Generated artifacts** — what regenerates (no direct edits).
   - **Descriptor property table** — every property to set, with values.
   - **Dependencies** — packages, versions, datasources.
   - **Platforms** — amd64/arm64 plan and any install overrides.
   - **Testing approach** — fixtures and the Docker command that will validate.
   - **Documentation** — descriptor metadata that drives auto-generated docs (`linter_text`, `linter_rules_url`, `ide`, `examples`). Do not plan to run `make megalinter-build-with-doc`.
   - **CHANGELOG** — proposed entry under `## [beta] (master)`, or "skip" with reason (routine version bump / CVE-ignore / internal-only).
   - **Risks & trade-offs** — performance, breaking changes, flavor membership impact.
5. **Delegation hints for `/implement`**:
   - Descriptor authoring → `descriptor-expert` agent.
   - Build pipeline → `build-runner` agent.
   - Test validation → `test-debugger` agent.
   - Python review → `code-reviewer` agent.
   - Relevant specialist skill: `/add-linter`, `/add-flavor`, `/add-reporter`, `/update-linter-version`, `/fix-security-issue`, `/review-descriptor`.

## Important

- Do NOT implement anything. Produce only the design document for user review.
- Do NOT plan edits to auto-generated files (`linters/*/Dockerfile`, `flavors/*/Dockerfile`, files with `automatically @generated` header, `docs/descriptors/*`). Plan the source change instead.
- Never plan `make megalinter-build-with-doc` — docs are owned by auto-update workflows.

$ARGUMENTS
