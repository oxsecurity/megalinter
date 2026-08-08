# Fix KUBERNETES_HELM errors

<!-- generated-descriptor-info-start -->
- Linter: **helm** (MegaLinter key: `KUBERNETES_HELM`)
- Descriptor: **KUBERNETES** (tooling_format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/kubernetes_helm/>
- Official documentation: <https://helm.sh/docs/helm/helm_lint/>
- Auto-fix support: no (errors must be fixed manually)
- Rules configuration: <https://helm.sh/docs/helm/helm_lint/>
- How to disable rules inline: <https://helm.sh/docs/topics/charts/#schema-files>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `KUBERNETES_HELM` to fully disable this linter
  - `KUBERNETES_HELM_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `KUBERNETES_HELM_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `KUBERNETES_HELM_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `KUBERNETES_HELM_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `KUBERNETES_HELM_ERROR_MISSING_DEPENDENCIES`
  - `KUBERNETES_HELM_ERROR_CHART_YAML_MISSING`
<!-- generated-descriptor-info-end -->

## Fix instructions

`helm lint PATH` runs a series of tests to verify that a Helm chart is well-formed. It emits `[ERROR]` messages for issues that would make the chart fail to install, and `[WARNING]` messages for convention or recommendation violations (with `--strict`, warnings also fail the run).

Fix errors by category:

- **Chart metadata errors** (reported against `Chart.yaml`): add or correct the offending field in `Chart.yaml` (e.g. required name/version metadata, recommended icon), then re-run `helm lint`.
- **Template rendering errors** (reported against files under `templates/`): fix the Go template syntax or the missing value at the reported line. Reproduce locally with `helm template PATH` to see the full rendering failure.
- **YAML parse errors**: correct indentation/syntax in the reported manifest or values file.
- **Values schema errors**: `helm lint` validates the final `.Values` object against `values.schema.json` (including subchart schemas). Either fix the value in `values.yaml` so it satisfies the schema, or correct the schema itself if it is wrong.
- **Values required at lint time**: if templates need values that are not in `values.yaml`, pass them to the lint command with `-f <file.yaml>` / `--values`, or `--set KEY=VALUE` (also `--set-string`, `--set-json`, `--set-file`).
- **Kubernetes version–dependent checks**: use `--kube-version <version>` so capability and deprecation checks match your target cluster.
- **Subchart errors**: lint dependent charts too with `--with-subcharts` and fix them at their source.

Helm has no auto-fix mode: every finding must be fixed by editing the chart.

## Inline disable

`helm lint` has no inline suppression syntax: you cannot disable a check from a comment inside `Chart.yaml`, templates or values files. The closest alternatives are command-line flags (add them via the extra-arguments variable of the generated block):

- `--quiet`: print only warnings and errors
- `--skip-schema-validation`: disable `values.schema.json` validation (useful e.g. in air-gapped environments when the schema contains remote references)

## Ignore via configuration

`helm lint` has no rule-configuration or ignore file of its own. Available levers:

- **Relax the schema**: edit `values.schema.json` to loosen a constraint (make a property optional, widen a type) instead of suppressing the validation globally.
- **`.helmignore`**: placed next to `Chart.yaml`, it excludes files from the packaged chart using shell-glob patterns (one per line, `!` negation, no `**` support):

  ```text
  .helmignore
  *.txt
  mydir/
  ```

- **Exclude whole charts from MegaLinter**: use the filter-regex-exclude variable of the generated block for vendored or third-party charts.

## When disabling is legitimate

- Third-party or vendored charts (e.g. mirrored dependencies) that you do not maintain: exclude their path rather than editing them.
- `values.schema.json` with remote `$ref` references in air-gapped CI: `--skip-schema-validation` is the documented escape hatch.
- Charts whose templates require deployment-time values that cannot be provided in CI: prefer passing placeholder values with `--set`/`--values` over disabling the linter.
- Warning-only conventions (e.g. recommended metadata) you deliberately reject: keep the linter blocking on errors instead of enabling `--strict`.

Disabling the linter at MegaLinter level (`DISABLE_LINTERS`) is the last resort.
