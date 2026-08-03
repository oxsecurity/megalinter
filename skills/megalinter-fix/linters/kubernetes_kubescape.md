# Fix KUBERNETES_KUBESCAPE errors

<!-- generated-descriptor-info-start -->
- Linter: **kubescape** (MegaLinter key: `KUBERNETES_KUBESCAPE`)
- Descriptor: **KUBERNETES** (tooling_format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/kubernetes_kubescape/>
- Official documentation: <https://github.com/kubescape/kubescape>
- Auto-fix support: no (errors must be fixed manually)
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `KUBERNETES_KUBESCAPE` to fully disable this linter
  - `KUBERNETES_KUBESCAPE_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `KUBERNETES_KUBESCAPE_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `KUBERNETES_KUBESCAPE_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `KUBERNETES_KUBESCAPE_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

kubescape is a Kubernetes security scanner: it checks manifests, Helm charts and Kustomize
directories for misconfigurations against frameworks such as NSA-CISA, MITRE ATT&CK and the
CIS Kubernetes Benchmark. It is a security scanner, not a formatter: remediate by hardening
the resource, not by reformatting.

- Each finding references a control ID (e.g. `C-0057`). Look it up in the control library
  (<https://kubescape.io/docs/controls/>) to understand the risk and the expected setting.
- Edit the flagged manifest to apply the control's remediation (typical examples: set a
  `securityContext`, drop privileged/host access, add resource limits, tighten RBAC).
- kubescape can auto-remediate many misconfigurations from a saved scan:

  ```bash
  kubescape scan /path/to/manifests --format json --output results.json
  kubescape fix results.json --dry-run   # preview
  kubescape fix results.json             # apply in-place
  ```

  Always review the diff: `kubescape fix` modifies files in place.
- Re-check a single control locally with `kubescape scan control C-0057 .` before re-running
  the full scan. Note that MegaLinter invokes kubescape with `--severity-threshold high`, so
  only high/critical findings break the build.

## Inline disable

kubescape has no inline suppression mechanism: there is no comment or resource annotation
that skips a control inside a manifest. The supported alternative is an exceptions file
(see below) that targets specific resources by name, kind, namespace or labels.

## Ignore via configuration

kubescape has no lint configuration file, but it supports an exceptions JSON file passed
with `--exceptions` (add the flag through the linter arguments variable listed above,
e.g. `--exceptions .kubescape/exceptions.json`). Excluded objects are reported as
"excluded" instead of failing:

```json
[
  {
    "name": "exclude-c0060-on-legacy-app",
    "policyType": "postureExceptionPolicy",
    "actions": ["alertOnly"],
    "resources": [
      {
        "designatorType": "Attributes",
        "attributes": { "kind": "Deployment", "name": "legacy-app" }
      }
    ],
    "posturePolicies": [{ "controlID": "C-0060" }]
  }
]
```

`resources` and `posturePolicies` each require at least one entry; attribute values
support regex (use `"kind": ".*"` to match all resources). See
<https://kubescape.io/docs/accepting-risk/> for the full syntax.

## When disabling is legitimate

- The control does not apply to the workload's threat model (e.g. host access required by a
  node-level agent or CNI/CSI component) — accept the risk with a narrowly scoped exception.
- Third-party Helm charts or generated manifests you do not own and cannot patch upstream.
- Controls enforced elsewhere in the platform (admission controller, policy engine), where a
  manifest-level finding is redundant.
- Prefer a resource-scoped exception in the exceptions file over widening the severity
  threshold; disabling the linter at MegaLinter level is the last resort.
