# Fix SNAKEMAKE_LINT errors

<!-- generated-descriptor-info-start -->
- Linter: **snakemake** (MegaLinter key: `SNAKEMAKE_LINT`)
- Descriptor: **SNAKEMAKE** (tooling_format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/snakemake_snakemake/>
- Official documentation: <https://snakemake.github.io/>
- Auto-fix support: no (errors must be fixed manually)
- Rules configuration: <https://snakemake.readthedocs.io/en/stable/snakefiles/configuration.html>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `SNAKEMAKE_LINT` to fully disable this linter
  - `SNAKEMAKE_LINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `SNAKEMAKE_LINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `SNAKEMAKE_LINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `SNAKEMAKE_LINT_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `SNAKEMAKE_LINT_ERROR_WORKFLOW_PARSE`
<!-- generated-descriptor-info-end -->

## Fix instructions

This linter runs `snakemake --lint`, which checks Snakefiles against Snakemake's official best
practices for reproducibility and portability. There is no auto-fix; address each reported lint:

- **Absolute path in Snakefile**: replace hardcoded absolute paths (e.g. `/home/user/data`) with
  paths relative to the working directory, or make them configurable via the config file.
- **No log directive defined**: add a `log:` directive to the rule so its output is captured in a
  file instead of being interleaved on the terminal (e.g. `log: "logs/myrule.log"` plus
  `2> {log}` in the shell command).
- **Specify a conda environment or container for each rule**: add a `conda:` (environment YAML)
  or `container:` directive so software dependencies are reproducible.
- **Deprecated `singularity:` directive**: replace it with the runtime-agnostic `container:`.
- **Shell command uses a variable from outside the rule**: pass the value through `params:`,
  `input:` or `output:` instead of referencing a global Python variable directly.
- **Do not access input/output files by index** (`{input[0]}`): name the files
  (`input: fq="reads.fastq"`) and reference them as `{input.fq}`.
- **Param is a prefix of an input/output file but hardcoded**: derive the prefix from the file
  with an input function or params lambda instead of duplicating the path.
- **Migrate long `run:` directives into scripts or notebooks**: move the code to
  `workflow/scripts/` and call it with `script:` (or `notebook:`).
- **Mixed rules and functions / path concatenation with `+`**: move complex helper functions to
  `workflow/rules/common.smk`; build paths with f-strings or `pathlib`.
- **`os.environ` usage without `envvars:`**: declare required environment variables with the
  `envvars:` directive.

Fixture parse errors (`SNAKEMAKE_LINT_ERROR_WORKFLOW_PARSE`) mean the Snakefile itself is
invalid (often mixed tabs and spaces): fix the syntax before re-running the lint.

## Inline disable

`snakemake --lint` has no inline suppression mechanism: there is no `# noqa`-style comment to
silence a specific lint in a Snakefile. When a finding cannot be fixed, exclude the file from
this linter through MegaLinter configuration (see below).

## Ignore via configuration

The linter itself has no configuration file to disable individual lint rules and no ignore-file
mechanism; the `workflow/config` files documented in the "Rules configuration" link configure
the workflow, not the linter. To skip specific Snakefiles, use the MegaLinter exclusion
variable from the block above, for example:

```yaml
# .mega-linter.yml
SNAKEMAKE_LINT_FILTER_REGEX_EXCLUDE: "(legacy/.*Snakefile|third_party/)"
```

## When disabling is legitimate

- Known false positives, such as shell commands whose fragments are misdetected as absolute
  paths (see snakemake issue #1305).
- Third-party or vendored workflows kept in sync with an upstream repository, where local
  divergence from best practices is not yours to fix.
- Rules intentionally running without `conda:`/`container:` because software is provided by the
  execution environment (e.g. cluster modules or a pre-built image).
- Quick prototype pipelines where portability lints (log directives, standard layout) are
  deliberately deferred.

Disabling at MegaLinter level (excluding files or the whole linter) is always the last resort:
prefer fixing the Snakefile.
