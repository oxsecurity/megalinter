# Fix TEKTON_TEKTON_LINT errors

<!-- generated-descriptor-info-start -->
- Linter: **tekton-lint** (MegaLinter key: `TEKTON_TEKTON_LINT`)
- Descriptor: **TEKTON** (tooling_format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/tekton_tekton_lint/>
- Official documentation: <https://github.com/IBM/tekton-lint>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.tektonlintrc.yaml` (custom path can be defined with `TEKTON_TEKTON_LINT_CONFIG_FILE`)
- Rules index: <https://github.com/IBM/tekton-lint#rules>
- Rules configuration: <https://github.com/IBM/tekton-lint#configuring-tekton-lint>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `TEKTON_TEKTON_LINT` to fully disable this linter
  - `TEKTON_TEKTON_LINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `TEKTON_TEKTON_LINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `TEKTON_TEKTON_LINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `TEKTON_TEKTON_LINT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

tekton-lint validates Tekton resource definitions (Tasks, Pipelines, TriggerTemplates, TriggerBindings) for both hard errors that prevent pipeline execution and best-practice violations. There is no auto-fix: correct the YAML manually per rule category.

- Missing definitions (`no-missing-task-definitions`, `no-missing-pipeline-definitions`, `no-missing-trigger-template-definitions`, `no-missing-referenced-task`): create the referenced Task/Pipeline/TriggerTemplate, fix the name typo, or declare it as an external task in the configuration file (`external-tasks` with `name`, `uri`, `path`).
- Parameter errors (`no-undefined-param`, `no-missing-required-task-params`, `no-missing-required-pipeline-params`, `no-extra-parameters`, `no-duplicate-param`, `no-invalid-param-syntax`, `no-invalid-param-type`): declare every parameter used in `$(params.x)` expressions, pass all required params at call sites, and remove extra or duplicate ones.
- Structural errors (`no-invalid-runAfter`, `no-cycle-detection`, `no-duplicate-resources`, `no-duplicate-env-vars`, `no-missing-task-results`, `no-undefined-workspace-references`, `no-missing-required-workspaces`, `no-missing-volume-definitions`): reference only existing task names in `runAfter`, break dependency cycles, deduplicate resources and env vars, and declare every workspace/volume/result before using it.
- Best practices (`no-latest-image`, `prefer-kebab-case`, `no-v1alpha1-apiVersion`, `no-deprecated-resource`, `no-deprecated-condition`, `no-unused-param`, `no-missing-hashbang`): pin container images to a specific tag instead of `latest`, rename resources to kebab-case, migrate off `v1alpha1` apiVersion and deprecated Condition resources, remove unused parameters, and start script blocks with a hashbang line.

Reproduce locally with `npx @ibm/tekton-lint@latest '<glob-pattern-to-yaml-files>'` (use `--format stylish|json|vscode` and `--quiet` to show errors only).

## Inline disable

tekton-lint has no inline suppression syntax: rules cannot be disabled with YAML comments in the linted files. The closest alternative is setting the rule to `off` or `warning` in the configuration file (see below), or excluding the file from this linter with the MegaLinter filter variable listed above.

## Ignore via configuration

Set per-rule severity (`error`, `warning`, `off`) in the configuration file named above:

```yaml
---
rules:
  no-duplicate-param: error
  no-unused-param: warning
  no-deprecated-resource: off
```

Custom rules loaded from Node modules are disabled with the `module#rule` form, e.g. `my_rules#no-tasks-called-task: off`. There is no dedicated ignore file: to skip files entirely, narrow the glob pattern passed to the CLI or use the MegaLinter exclude regex.

## When disabling is legitimate

- The pipeline calls a Task from an external catalog that tekton-lint cannot resolve locally: prefer declaring it under `external-tasks` before turning off `no-missing-task-definitions`.
- Legacy manifests intentionally still use deprecated resources or `v1alpha1` apiVersion pending a planned migration: downgrade `no-deprecated-resource` / `no-v1alpha1-apiVersion` to `warning` rather than `off`.
- Naming conventions diverge deliberately (e.g. camelCase mandated by an internal platform): switch `prefer-kebab-case` to `prefer-camel-kebab-case` or disable it.
- `latest` image tags kept on purpose in dev-only pipelines: scope the exception to those files instead of disabling `no-latest-image` globally.
- Disabling the whole linter or a rule at MegaLinter level is the last resort; always prefer fixing the manifest or a targeted rule-level configuration.
