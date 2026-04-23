---
name: update-linter-version
description: Update a linter's pinned version in its descriptor YAML. Use when upgrading a linter tool to a new release.
allowed-tools: Read Grep Glob Edit Bash
argument-hint: [linter-name] [new-version]
arguments: [linter, version]
---

Update the version of linter `$linter` to `$version`.

Steps:

1. Search `megalinter/descriptors/*.megalinter-descriptor.yml` for the linter by name
2. Find the version ARG in the `install.dockerfile` section (e.g., `ARG PIP_TOOL_VERSION=X.Y.Z`) or version pin in pip/npm arrays
3. Update the version, preserving the renovate comment format:
   ```yaml
   # renovate: datasource=pypi depName=tool-name
   ARG PIP_TOOL_VERSION=<new_version>
   ```
4. If no version was specified, check the tool's package registry for the latest
5. Run `make megalinter-build` to regenerate Dockerfiles with the new version
6. Update `CHANGELOG.md` in the **repository root** (not the one in /docs)
7. To test the updated version in CI, write `TEST_KEYWORDS=<linter>_test` in the commit message body
