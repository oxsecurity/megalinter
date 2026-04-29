---
name: add-flavor
description: Add a new MegaLinter flavor (language-specific Docker image). Use when creating a new specialized Docker image variant.
allowed-tools: Read Grep Glob Bash Edit Write
argument-hint: [flavor-name]
---

Guide through adding a new flavor named `$ARGUMENTS`.

Steps:

1. **Update the schema enum** in `megalinter/descriptors/schemas/megalinter-descriptor.jsonschema.json` — add the new flavor name to `enum_flavors`
2. **Create the flavor directory** `flavors/$ARGUMENTS/`
3. **Update descriptors**: Add the flavor name to `descriptor_flavors` arrays in the relevant `megalinter/descriptors/*.megalinter-descriptor.yml` files for each language/tool this flavor should include
4. **Run `make megalinter-build`** to auto-generate:
   - `flavors/$ARGUMENTS/Dockerfile`
   - `flavors/$ARGUMENTS/action.yml`
   - `flavors/$ARGUMENTS/flavor.json`
5. **Verify** the generated Dockerfile includes exactly the intended linters (check `flavor.json` for the linter list)
6. **Update documentation** and `CHANGELOG.md` in the repository root (not docs/)
7. **Branch naming**: use `user/add-<flavor-name>-flavor`
