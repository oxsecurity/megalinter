---
name: diagnose-config
description: Diagnose MegaLinter .mega-linter.yml configuration issues. Use when linters aren't running as expected or configuration seems wrong.
allowed-tools: Read Grep Glob
argument-hint: "[config-file-path]"
model: sonnet
metadata:
  internal: true
---

Diagnose MegaLinter configuration. Read the `.mega-linter.yml` (or path provided in `$ARGUMENTS`) and check for:

1. **Configuration hierarchy**: Env vars override `.mega-linter.yml`, which overrides descriptor defaults. Both `.mega-linter.yml` and `.megalinter.yml` are recognized.
2. **ENABLE/DISABLE conflicts**: `ENABLE_LINTERS`/`DISABLE_LINTERS` take precedence over `ENABLE`/`DISABLE` (descriptor-level). You can't enable a linter if its descriptor is disabled.
3. **Filter patterns**: Validate `FILTER_REGEX_INCLUDE`/`FILTER_REGEX_EXCLUDE` regex syntax
4. **Linter variable naming**: Must be UPPERCASE with `_` separator matching the generated name `DESCRIPTOR_LINTERNAME` (e.g., `PYTHON_PYLINT_ARGUMENTS`, not `pylint_arguments`)
5. **Flavor compatibility**: If using a flavor image, verify the enabled linters exist in that flavor by checking `flavors/<flavor>/flavor.json`
6. **EXTENDS**: If using remote config inheritance via HTTPS URLs, verify they're accessible
7. **APPLY_FIXES**: Check the fix mode is compatible with the CI system — auto-commit requires write access to the branch
8. **Pre/Post commands**: Validate `PRE_COMMANDS` and `POST_COMMANDS` syntax (each needs `command` and `cwd` fields, `cwd` is `root` or `workspace`)
9. **Native mode** (run without Docker, `--native`): only the linters listed in `NATIVE_LINTERS` run, the other active linters are skipped (`all` is allowed but discouraged). Keys must be current linter keys: a removed linter (`REPOSITORY_GITLEAKS`) fails with its replacement named (`megalinter/removed_linters.py`). `PRE_COMMANDS`, `POST_COMMANDS`, `PLUGINS` and remote `EXTENDS` are ignored unless `--trust-repo-commands` (or `NATIVE_TRUST_REPO_COMMANDS=true` in the environment, never in the file). Linters only get an allowlist of environment variables: a tool missing a variable needs `NATIVE_ENV_ALLOWLIST` (or `<LINTER_KEY>_UNSECURED_ENV_VARIABLES`). `FLAVOR` / `MEGALINTER_FLAVOR` do not apply. Other variables: `NATIVE_INSTALL_RUNTIMES`, `NATIVE_MISSING_LINTERS`, `NATIVE_OFFLINE`, `MEGALINTER_HOME` (`docs/install-native.md`)
10. **Common mistakes**:
- Using lowercase linter names (must be UPPERCASE)
- Missing `_` separator in linter-specific vars
- Setting `VALIDATE_ALL_CODEBASE=true` in CI (slow — usually want diff-only)
- Forgetting `{LINTER}_FILTER_REGEX_INCLUDE/EXCLUDE` overrides global filters

Reference `megalinter/config.py` for the full resolution logic.
