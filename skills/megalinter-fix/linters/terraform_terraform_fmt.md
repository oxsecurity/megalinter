# Fix TERRAFORM_TERRAFORM_FMT errors

<!-- generated-descriptor-info-start -->
- Linter: **terraform-fmt** (MegaLinter key: `TERRAFORM_TERRAFORM_FMT`)
- Descriptor: **TERRAFORM** (tooling_format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/terraform_terraform_fmt/>
- Official documentation: <https://developer.hashicorp.com/terraform/cli/commands/fmt>
- Auto-fix support: **yes** — add `TERRAFORM_TERRAFORM_FMT` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter TERRAFORM_TERRAFORM_FMT --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `TERRAFORM_TERRAFORM_FMT` to fully disable this linter
  - `TERRAFORM_TERRAFORM_FMT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `TERRAFORM_TERRAFORM_FMT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `TERRAFORM_TERRAFORM_FMT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `TERRAFORM_TERRAFORM_FMT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

`terraform fmt` is a pure formatter: it rewrites Terraform configuration files to the canonical HCL style (two-space indentation per nesting level, aligned `=` signs for consecutive single-line arguments, arguments grouped above nested blocks with a blank line between them). It reports no rules — a failure only means a file is not in canonical format.

The fix is never manual reformatting — run the formatter:

- Preferred: enable MegaLinter auto-fix as described in the block above.
- Locally: run `terraform fmt -recursive` at the repository root to rewrite all `.tf` files in subdirectories (by default only the current directory is processed).
- To preview what would change without writing, run `terraform fmt -check -diff` (exit code is non-zero when files need reformatting — this check mode is what makes CI fail).
- To format a single file: `terraform fmt path/to/file.tf`.

Formatting is intentionally opinionated with no customization options, so there is no style decision to make: apply the tool output as-is.

## Inline disable

`terraform fmt` has no inline suppression mechanism — no comment or directive can exempt a block or line from formatting, since the tool has no configurable rules. The closest alternative is excluding the whole file from the linter via the MegaLinter exclusion regex variable listed in the block above:

```yaml
# .mega-linter.yml
TERRAFORM_TERRAFORM_FMT_FILTER_REGEX_EXCLUDE: '(vendored|generated)/'
```

## Ignore via configuration

`terraform fmt` has no configuration file and no ignore file: it accepts no rule toggles and reads no settings from the project. File-level exclusion is therefore only possible at MegaLinter level, using the exclusion regex shown above, or by narrowing the CLI target through the extra-arguments variable (for example passing a specific directory instead of the default).

## When disabling is legitimate

- Vendored or third-party Terraform modules copied into the repository that must stay byte-identical to upstream for diffability.
- Machine-generated `.tf` files (e.g. produced by code generators or `cdktf`) that are regenerated on every build and never hand-edited.
- Almost never otherwise: the format is deterministic, safe, and semantic-neutral, so running the auto-fix is always cheaper than suppressing the check.

Disabling the linter at MegaLinter level (`DISABLE_LINTERS` / `DISABLE_ERRORS`) is the last resort — prefer auto-fix, then targeted file exclusion.
