# Fix BICEP_BICEP_LINTER errors

<!-- generated-descriptor-info-start -->
- Linter: **bicep_linter** (MegaLinter key: `BICEP_BICEP_LINTER`)
- Descriptor: **BICEP** (tooling_format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/bicep_bicep_linter/>
- Official documentation: <https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter>
- Auto-fix support: no (errors must be fixed manually)
- Rules index: <https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter#default-rules>
- Rules configuration: <https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/bicep-config>
- How to disable rules inline: <https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter#silencing-false-positives>
- Error line format (regex): ` : Error `
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `BICEP_BICEP_LINTER` to fully disable this linter
  - `BICEP_BICEP_LINTER_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `BICEP_BICEP_LINTER_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `BICEP_BICEP_LINTER_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `BICEP_BICEP_LINTER_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

The Bicep linter is built into the Bicep CLI (`bicep build` / `bicep lint`) and checks `.bicep` files for syntax errors and best-practice violations derived from arm-ttk test cases. There is no CLI auto-fix: fix each violation manually (quick fixes exist only in the VS Code Bicep extension).

Fix the most common rule categories as follows:

- **Unused declarations** (`no-unused-params`, `no-unused-vars`, `no-unused-imports`, `no-unused-existing-resources`): delete the unused parameter, variable, import or `existing` resource, or wire it into the template.
- **Hardcoded values** (`no-hardcoded-env-urls`): replace literal Azure endpoint hosts (e.g. `core.windows.net`, `management.azure.com`) with the `environment()` function.
- **Secrets** (`outputs-should-not-contain-secrets`, `secure-parameter-default`, `adminusername-should-not-be-literal`, `protect-commandtoexecute-secrets`): never output secret values, add `@secure()` to secret parameters and remove their defaults, pass admin usernames as parameters instead of literals, and move `commandToExecute` secrets into `protectedSettings`.
- **String expressions** (`prefer-interpolation`, `simplify-interpolation`): use `'${a}${b}'` interpolation instead of `concat()`, and drop interpolation wrapping a lone string variable.
- **Resource references** (`use-parent-property`, `use-resource-symbol-reference`, `no-unnecessary-dependson`): declare child resources with the `parent` property, reference resources by symbolic name instead of `reference()`/`resourceId()`, and remove `dependsOn` entries Bicep infers automatically.
- **Limits** (`max-parameters`, `max-outputs`, `max-variables`, `max-resources`): these are errors mirroring ARM template limits; split the template into modules.

Rule violations at `Error` level fail the build; `Warning` level is reported without failing. Each message includes the rule name — look it up in the rules index of the generated block above.

## Inline disable

Use the `#disable-next-line` directive immediately above the offending line, followed by one or more space-separated rule names or compiler diagnostic codes (case sensitive). `#disable-diagnostics` disables rules for the rest of the file and `#restore-diagnostics` re-enables them.

```bicep
#disable-next-line no-hardcoded-env-urls // link to a specific blob, environment() not applicable
var blobUrl = 'https://myaccount.blob.core.windows.net/data'
```

Add a comment explaining why the suppression is legitimate.

## Ignore via configuration

Create a `bicepconfig.json` in the same directory as (or a parent directory of) the Bicep files; the nearest one wins and is merged with the default configuration. Set a rule's `level` to `off` to disable it, or downgrade it to `warning`/`info`:

```json
{
  "analyzers": {
    "core": {
      "enabled": true,
      "rules": {
        "no-hardcoded-env-urls": { "level": "off" },
        "max-params": { "level": "warning" }
      }
    }
  }
}
```

Setting `"enabled": false` under `analyzers.core` turns the whole linter off. There is no ignore-file mechanism for excluding paths in `bicepconfig.json`; to skip files, place a directory-local `bicepconfig.json` with relaxed rules next to them, or use the MegaLinter file-exclusion variable from the generated block.

## When disabling is legitimate

- `no-hardcoded-env-urls` false positives when a URL intentionally points to a specific storage blob or external host where `environment()` does not apply.
- Files produced by `bicep decompile` from ARM JSON that trip `decompiler-cleanup` and naming rules pending a later refactor.
- Sovereign or Azure Stack clouds where `use-recent-api-versions` flags API versions not yet available in that environment.
- Templates deliberately kept as a single file where `max-resources`/`max-params` limits would force an unwanted module split.

Prefer inline `#disable-next-line` with a justification comment, then a rule-level `off` in `bicepconfig.json`; disabling at MegaLinter level is the last resort.
