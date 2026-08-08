# Fix DOCKERFILE_HADOLINT errors

<!-- generated-descriptor-info-start -->
- Linter: **hadolint** (MegaLinter key: `DOCKERFILE_HADOLINT`)
- Descriptor: **DOCKERFILE** (tooling_format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/dockerfile_hadolint/>
- Official documentation: <https://github.com/hadolint/hadolint>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.hadolint.yaml` (custom path can be defined with `DOCKERFILE_HADOLINT_CONFIG_FILE`)
- Rules index: <https://github.com/hadolint/hadolint#rules>
- Rules configuration: <https://github.com/hadolint/hadolint#configure>
- How to disable rules inline: <https://github.com/hadolint/hadolint#inline-ignores>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `DOCKERFILE_HADOLINT` to fully disable this linter
  - `DOCKERFILE_HADOLINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `DOCKERFILE_HADOLINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `DOCKERFILE_HADOLINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `DOCKERFILE_HADOLINT_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `DOCKERFILE_HADOLINT_ERROR_CONFIG_PARSE`
  - `DOCKERFILE_HADOLINT_ERROR_CONFIG_READ`
<!-- generated-descriptor-info-end -->

## Fix instructions

hadolint parses the Dockerfile into an AST and applies Docker best-practice rules (`DLxxxx`), and runs ShellCheck (`SCxxxx`) on the shell code inside `RUN` instructions. There is no auto-fix: edit the Dockerfile per reported rule.

- **DL3006 / DL3007**: pin the base image to an explicit release tag — write `FROM ubuntu:24.04`, never a bare `FROM ubuntu` or `FROM ubuntu:latest`.
- **DL3008**: pin apt package versions, e.g. `apt-get install -y python=2.7.*` (use a tool like Renovate to keep pins current).
- **DL3013**: pin pip versions, e.g. `pip install django==1.9`, or a git ref such as `pip install git+https://...@0.9.15`.
- **DL3018**: pin apk versions with `apk add <package>=<version>`.
- **DL3003**: replace `RUN cd /dir && ...` with a `WORKDIR /dir` instruction before the `RUN`.
- **DL3009**: delete apt lists in the same `RUN` layer: `apt-get update && apt-get install --no-install-recommends -y <pkg> && apt-get clean && rm -rf /var/lib/apt/lists/*`.
- **DL4006**: add `SHELL ["/bin/bash", "-o", "pipefail", "-c"]` before any `RUN` containing a pipe (on Alpine use `SHELL ["/bin/ash", "-eo", "pipefail", "-c"]`).

## Inline disable

Put a comment on the line directly above the instruction; it applies only to that instruction. Prefix with `global` to apply to the whole file. An extra `#` allows a justification comment.

```dockerfile
# hadolint global ignore=DL3059
FROM ubuntu:26.04
# hadolint ignore=DL3008,SC1035 # We accept these issues, because ...
RUN apt-get update && apt-get install -y curl
```

## Ignore via configuration

Create a `.hadolint.yaml` at the repository root:

```yaml
ignored:
  - DL3008
  - SC1010
trustedRegistries:
  - docker.io
  - my-company.com:5000
override:
  error:
    - DL3001
  warning:
    - DL3042
  info:
    - DL3032
failure-threshold: info
```

- `ignored`: rule codes skipped entirely
- `trustedRegistries`: registries allowed for base images
- `override`: reassign rules to another severity (`error` / `warning` / `info`)
- `failure-threshold`: lowest severity that makes hadolint exit non-zero

## When disabling is legitimate

- The distribution repository offers no stable version pins (e.g. rolling apk/apt channels): inline-ignore DL3008/DL3013/DL3018 on that instruction with a justification comment.
- The Dockerfile intentionally tracks a moving tag (nightly/CI test image): ignore DL3007 for that file only.
- A ShellCheck finding is a false positive for the shell actually configured in the image.
- MegaLinter-level disabling (`DISABLE_LINTERS`, `DOCKERFILE_HADOLINT_DISABLE_ERRORS`) is a last resort — prefer inline ignores or `.hadolint.yaml` so other rules stay enforced.
