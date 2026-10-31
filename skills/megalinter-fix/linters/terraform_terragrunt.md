# Fix TERRAFORM_TERRAGRUNT errors

<!-- generated-descriptor-info-start -->
- Linter: **terragrunt** (MegaLinter key: `TERRAFORM_TERRAGRUNT`)
- Descriptor: **TERRAFORM** (tooling_format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/terraform_terragrunt/>
- Official documentation: <https://docs.terragrunt.com/reference/cli/commands/hcl/fmt/>
- Auto-fix support: **yes** — add `TERRAFORM_TERRAGRUNT` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter TERRAFORM_TERRAGRUNT --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Configuration file: `terragrunt.hcl` (custom path can be defined with `TERRAFORM_TERRAGRUNT_CONFIG_FILE`)
- Rules configuration: <https://terragrunt.gruntwork.io/docs/getting-started/quick-start/#add-terragrunthcl-to-your-project>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `TERRAFORM_TERRAGRUNT` to fully disable this linter
  - `TERRAFORM_TERRAGRUNT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `TERRAFORM_TERRAGRUNT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `TERRAFORM_TERRAGRUNT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `TERRAFORM_TERRAGRUNT_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `TERRAFORM_TERRAGRUNT_ERROR_CONFIG_PARSE`
<!-- generated-descriptor-info-end -->

## Fix instructions

Here terragrunt acts as a pure formatter: MegaLinter runs `terragrunt hcl fmt --check --file <file>` on each `.hcl` file and fails when the file is not written in canonical HCL format. There are no configurable style rules — any error simply means the file must be reformatted.

- Preferred fix: enable the MegaLinter auto-fix (see the generated block above); it drops `--check` so terragrunt rewrites the files in place.
- Locally, run `terragrunt hcl fmt` from the repository root to recursively reformat every HCL file, or target one file with `terragrunt hcl fmt --file=path/to/terragrunt.hcl`.
- To preview changes before applying them, run `terragrunt hcl fmt --check --diff`.
- If the failure matches `TERRAFORM_TERRAGRUNT_ERROR_CONFIG_PARSE`, formatting is not the problem: the HCL itself is invalid. Fix syntax errors (unclosed blocks, bad interpolation) and make sure paths used in `include` and `dependency` blocks resolve from the working directory.

## Inline disable

terragrunt `hcl fmt` has no inline suppression comment: it formats whole files and cannot skip a region of code. To keep a file out of the check, exclude it instead — either through terragrunt's own directory exclusion (below) or through the MegaLinter file-exclusion regex listed in the generated block.

```hcl
# There is no "terragrunt:disable"-style comment; this block will always be formatted.
inputs = {
  env = "prod"
}
```

## Ignore via configuration

`terragrunt.hcl` itself has no setting to turn off formatting checks and there is no dedicated ignore file. Exclusion is done on the command line or at MegaLinter level:

- When running terragrunt directly, skip directories with `--exclude-dir` (repeatable), e.g. `terragrunt hcl fmt --check --exclude-dir=vendor --exclude-dir=.terragrunt-cache`, or use path filters such as `--filter '!./test/**'`.
- In MegaLinter (which invokes terragrunt once per file), exclude files with the regex variable from the generated block:

```yaml
# .mega-linter.yml
TERRAFORM_TERRAGRUNT_FILTER_REGEX_EXCLUDE: '(vendor/|\.terragrunt-cache/)'
```

## When disabling is legitimate

- Vendored or third-party HCL copied into the repository that you do not maintain and want to keep byte-identical to upstream.
- Generated `.hcl` files (scaffolding or codegen output) that are overwritten on each regeneration.
- Accidentally scanned working artifacts such as `.terragrunt-cache` directories — exclude them rather than reformatting cache content.
- For hand-written configuration, prefer fixing: formatting is deterministic, safe and automated. Disabling the linter at MegaLinter level is the last resort.
