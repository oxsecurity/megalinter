# Fix PYTHON_BANDIT errors

<!-- generated-descriptor-info-start -->
- Linter: **bandit** (MegaLinter key: `PYTHON_BANDIT`)
- Descriptor: **PYTHON** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/python_bandit/>
- Official documentation: <https://bandit.readthedocs.io/en/latest/>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.bandit.yml` (custom path can be defined with `PYTHON_BANDIT_CONFIG_FILE`)
- Rules index: <https://bandit.readthedocs.io/en/latest/plugins/index.html#complete-test-plugin-listing>
- Rules configuration: <https://bandit.readthedocs.io/en/latest/config.html#>
- How to disable rules inline: <https://bandit.readthedocs.io/en/latest/config.html#suppressing-individual-lines>
- Error line format (regex): `>> Issue: \[`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `PYTHON_BANDIT` to fully disable this linter
  - `PYTHON_BANDIT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `PYTHON_BANDIT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `PYTHON_BANDIT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `PYTHON_BANDIT_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `PYTHON_BANDIT_ERROR_CONFIG_NOT_FOUND`
  - `PYTHON_BANDIT_ERROR_CONFIG_INVALID`
  - `PYTHON_BANDIT_ERROR_PROFILE_NOT_FOUND`
<!-- generated-descriptor-info-end -->

## Fix instructions

bandit is a security scanner: it builds an AST of each Python file and runs test plugins that flag
common security issues (test IDs `B1xx`-`B7xx`). There is no auto-fix; remediate the vulnerability itself:

- Read the reported test ID (e.g. `B602`) on the rule index page to understand the risk before touching code.
- `B101` (`assert_used`): replace `assert` used for runtime validation with an explicit check raising an exception, since asserts are stripped from optimized bytecode.
- `B105`-`B107` (hardcoded passwords): move secrets to environment variables or a secret store, and rotate any credential that was committed.
- `B602` and other `subprocess` findings: drop `shell=True`, pass the command as a list of arguments, and never interpolate user input into a shell string.
- `B608` (`hardcoded_sql_expressions`): replace string-built SQL with parameterized queries provided by the database driver or ORM.
- Blacklisted calls/imports (`B3xx`/`B4xx`, e.g. `pickle`, weak hashes): switch to the safer alternative named in the rule documentation, or justify and suppress narrowly.
- Prioritize by the reported severity and confidence levels; fix HIGH severity findings first.

## Inline disable

Append a `# nosec` comment to the offending line; scope it to specific test IDs (or test names) rather
than suppressing everything:

```python
self.process = subprocess.Popen('/bin/ls *', shell=True)  # nosec B602, B607
assert yaml.load("{}") == []  # nosec assert_used
```

A bare `# nosec` suppresses every result on the line — always prefer the ID-scoped form.

## Ignore via configuration

The YAML configuration file supports `skips` (test IDs to disable), `tests` (only run these) and
`exclude_dirs` (paths to skip):

```yaml
exclude_dirs: ['tests', 'path/to/file']
tests: ['B201', 'B301']
skips: ['B101', 'B601']
```

If both `tests` and `skips` are given, bandit runs only the tests listed in `tests` minus those in
`skips`. bandit has no dedicated ignore file, but the same options can also live in a `.bandit` INI
file (using `exclude =` instead of `exclude_dirs`) or a `[tool.bandit]` section of `pyproject.toml`,
passed with `-c` or `--ini`. CLI flags `-s`/`-t` concatenate with the config file values.

## When disabling is legitimate

- `B101` in test suites: `assert` is the normal pytest idiom, so skip `B101` for test directories via `exclude_dirs` or a scoped `skips`.
- False positives on non-secrets: `B105` often flags constants like `token_type = "Bearer"` that are not credentials — suppress with `# nosec B105`.
- Subprocess calls with fully static, trusted arguments where `shell=True` is genuinely required — document why in the `# nosec` line's surrounding code.
- Generated or vendored code you do not maintain: exclude the path with `exclude_dirs` instead of editing it.

Disabling at MegaLinter level (`DISABLE_LINTERS`, `PYTHON_BANDIT_DISABLE_ERRORS`) is the last resort:
prefer a targeted `# nosec` or a configuration-level skip.
