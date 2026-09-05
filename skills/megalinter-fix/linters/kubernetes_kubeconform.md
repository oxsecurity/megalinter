# Fix KUBERNETES_KUBECONFORM errors

<!-- generated-descriptor-info-start -->
- Linter: **kubeconform** (MegaLinter key: `KUBERNETES_KUBECONFORM`)
- Descriptor: **KUBERNETES** (tooling_format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/kubernetes_kubeconform/>
- Official documentation: <https://github.com/yannh/kubeconform>
- Auto-fix support: no (errors must be fixed manually)
- Rules configuration: <https://github.com/yannh/kubeconform#usage>
- How to disable rules inline: <https://github.com/yannh/kubeconform#disabling-validation-for-specific-resources>
- Error line format (regex): `(?:Invalid|Errors): ([0-9]+)`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `KUBERNETES_KUBECONFORM` to fully disable this linter
  - `KUBERNETES_KUBECONFORM_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `KUBERNETES_KUBECONFORM_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `KUBERNETES_KUBECONFORM_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `KUBERNETES_KUBECONFORM_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `KUBERNETES_KUBECONFORM_ERROR_SCHEMA_NOT_FOUND`
  - `KUBERNETES_KUBECONFORM_ERROR_SCHEMA_DOWNLOAD_FAILED`
<!-- generated-descriptor-info-end -->

## Fix instructions

kubeconform validates Kubernetes manifests against JSON schemas derived from the Kubernetes
OpenAPI specifications, and supports custom resources via extra schema locations.

Fix errors by category:

- **Type violations** (e.g. `Invalid type. Expected: [integer,null], given: string`): edit the
  manifest so the property value matches the schema type — unquote numbers, quote strings,
  fix booleans.
- **Schema mismatches** (unknown or misplaced properties, wrong nesting): compare the manifest
  with the Kubernetes API reference for the resource `apiVersion`/`kind` and correct the field
  path; with `-strict`, also remove undefined properties and duplicated keys.
- **Missing schemas** for CRDs: add a schema source with
  `-schema-location default -schema-location '<url-or-path>/{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json'`,
  or generate JSON schemas from the CRD with kubeconform's `openapi2jsonschema` tool and point
  `-schema-location` at them (e.g. `'schemas/{{ .ResourceKind }}{{ .KindSuffix }}.json'`).
- **Version drift**: pass `-kubernetes-version <x.y.z>` so manifests are validated against the
  cluster's actual Kubernetes version.

kubeconform has no auto-fix command: every error must be corrected in the manifest itself.

## Inline disable

kubeconform has no inline (annotation or comment) suppression syntax in manifests. The closest
alternative is skipping at the CLI level with the `-skip` flag, which takes a comma-separated
list of kinds or GVKs:

```bash
# Skip a kind in all versions
kubeconform -skip ReplicationController manifest.yaml
# Skip only a specific group/version/kind
kubeconform -skip v1/ReplicationController manifest.yaml
```

## Ignore via configuration

kubeconform has no configuration file: all tuning is done through CLI flags, passed in
MegaLinter via the arguments tuning variable listed above.

- Skip resource kinds: `-skip Kind1,Kind2` (or GVK form `v1/Kind`)
- Ignore resources whose schema cannot be found: `-ignore-missing-schemas`
- Exclude files by name: `-ignore-filename-pattern '<regex>'` (repeatable)

```yaml
# .mega-linter.yml
KUBERNETES_KUBECONFORM_ARGUMENTS: "-skip CustomResourceDefinition -ignore-missing-schemas"
```

## When disabling is legitimate

- CRDs and operator-managed kinds with no published JSON schema: prefer adding a
  `-schema-location` for them; use `-ignore-missing-schemas` or `-skip` only when no schema
  can be generated.
- Templated or partially rendered manifests (Helm/Kustomize sources) that are not valid
  Kubernetes YAML until rendered: exclude them by file pattern.
- Manifests intentionally targeting a different Kubernetes version than the default schemas:
  set `-kubernetes-version` instead of skipping the resource.
- Disabling the linter at MegaLinter level is the last resort — prefer fixing the manifest or
  narrowing the skip to a specific kind or file.
