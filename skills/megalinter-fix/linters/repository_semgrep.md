# Fix REPOSITORY_SEMGREP errors

<!-- generated-descriptor-info-start -->
- Linter: **semgrep** (MegaLinter key: `REPOSITORY_SEMGREP`)
- Descriptor: **REPOSITORY** (other)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/repository_semgrep/>
- Official documentation: <https://semgrep.dev/>
- Auto-fix support: no (errors must be fixed manually)
- Ignore file: `.semgrepignore`
- Rules index: <https://semgrep.dev/r>
- Rules configuration: <https://semgrep.dev/docs/running-rules/>
- How to disable rules inline: <https://semgrep.dev/docs/ignoring-findings/#inline-comments>
- How to ignore files and directories: <https://semgrep.dev/docs/ignoring-files-folders-code/#defining-files-and-folders-in-semgrepignore>
- Error line format (regex): `files: ([0-9]+) finding`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `REPOSITORY_SEMGREP` to fully disable this linter
  - `REPOSITORY_SEMGREP_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `REPOSITORY_SEMGREP_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `REPOSITORY_SEMGREP_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `REPOSITORY_SEMGREP_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

Semgrep is a multi-language static analysis engine that matches code against rules (security vulnerabilities, bug patterns, anti-patterns) selected via `--config` (registry rulesets such as `p/default` or `p/python`, local rule YAML files, or `--config=auto`).

- Read the reported rule id and message: each finding points to the exact matched code and the rule that fired.
- For security findings, remediate the root cause: replace dangerous function calls with safe equivalents, parameterize queries instead of concatenating input, move hardcoded secrets to environment variables or a secret store (and rotate any committed secret), and use vetted crypto APIs instead of weak ones.
- Look up the rule in the rules index (see generated block above) to understand its rationale and the recommended safe pattern before rewriting code.
- Some rules ship a `fix:` suggestion; apply them locally with `semgrep scan --config=<ruleset> --autofix` (warning from the CLI docs: data loss can occur, run only on version-controlled files).
- To reproduce a single finding locally, run an ephemeral pattern: `semgrep scan -e '$X == $X' --lang=py PATH/TO/PROJECT`.

## Inline disable

Add a `nosemgrep` comment on the matched line or on the line immediately preceding it. Append `: RULE_ID` (comma-delimited list allowed, with the rule's namespace) to target specific rules; a bare `nosemgrep` suppresses all rules on that line.

```python
bad_func1()  # nosemgrep: rule-id-1

# nosemgrep: rule-id-1, rule-id-2
bad_func2()
```

```javascript
bad_func2(); // nosemgrep: configs.rule-id-3
```

## Ignore via configuration

Create a `.semgrepignore` file at the repository root with gitignore-style patterns (character ranges are unsupported; a `:include .gitignore` directive can pull in your `.gitignore`). Without one, Semgrep applies a default template that already excludes paths like `vendor/`, `node_modules/`, `dist/`, `test/` and `tests/`, plus your `.gitignore`.

```text
:include .gitignore
build/
generated/*.py
```

Other levers:

- Skip a rule everywhere: pass `--exclude-rule=RULE_ID` (repeatable) through the linter's extra CLI arguments.
- Skip paths for one scan: `--exclude=PATTERN`.
- In custom rule YAML files, restrict a rule with its `paths` key.

## When disabling is legitimate

- False positive: the pattern matches but the flagged value is not attacker-controlled or is already sanitized upstream — suppress inline with the rule id and a short justification comment.
- Test fixtures or intentionally vulnerable sample code (e.g. security training material) — exclude the folder in `.semgrepignore`.
- Generated or vendored code you do not maintain — exclude the path rather than editing files that will be regenerated.
- A registry rule that does not fit the project's threat model — drop it with `--exclude-rule` instead of scattering inline comments.
- Disabling the whole linter at MegaLinter level is the last resort; prefer per-rule or per-path ignores.
