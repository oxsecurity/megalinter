---
name: build
description: Run the MegaLinter build system to regenerate Dockerfiles, test classes, docs, and schemas from YAML descriptors.
allowed-tools: Bash Read
model: haiku
metadata:
  internal: true
---

Run the MegaLinter build system. Ask what to build if unclear.

## Make Targets

- `make megalinter-build` — regenerate Dockerfiles and test classes from descriptors
- `make megalinter-build-with-doc` — also regenerate documentation pages
- `make megalinter-build-custom` — build custom flavor

## Prerequisites

Requires an activated Python venv. If it fails:
1. Run `make bootstrap` to set up the environment (creates venv, installs deps with uv)
2. If running `build.sh` manually instead of `make`, activate venv first:
   - Linux/macOS: `source .venv/bin/activate`
   - Windows: `source .venv/Scripts/activate`

## Underlying build.py Flags

`.automation/build.py` supports: `--doc`, `--stats`, `--dependents`, `--changelog`, `--release <version>`, `--version <version>`, `--latest`, `--custom-flavor`, `--delete-dockerfiles`, `--delete-test-classes`.

## What Gets Generated

From YAML descriptors, the build creates:
- `linters/*/Dockerfile` — per-linter Docker images
- `flavors/*/Dockerfile`, `action.yml`, `flavor.json` — flavor Docker images
- `megalinter/tests/test_megalinter/linters/*_test.py` — test classes
- `docs/descriptors/*` — documentation pages
- `.automation/generated/` — cached linter versions, helps, licenses

## Updating Dockerfile Base Image

If updating the base image in `/Dockerfile`, run `make megalinter-build` and it will propagate to all other Dockerfiles automatically.

## CI Build Commands

Maintainers with write access can comment `/build` on a PR to trigger the build workflow. Use `/help` to see all available PR commands.
