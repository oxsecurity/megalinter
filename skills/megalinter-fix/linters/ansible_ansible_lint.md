# Fix ANSIBLE_ANSIBLE_LINT errors

<!-- generated-descriptor-info-start -->
- Linter: **ansible-lint** (MegaLinter key: `ANSIBLE_ANSIBLE_LINT`)
- Descriptor: **ANSIBLE** (tooling_format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/ansible_ansible_lint/>
- Official documentation: <https://ansible-lint.readthedocs.io/>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.ansible-lint` (custom path can be defined with `ANSIBLE_ANSIBLE_LINT_CONFIG_FILE`)
- Rules index: <https://ansible-lint.readthedocs.io/rules/>
- Rules configuration: <https://ansible-lint.readthedocs.io/configuring/#configuration-file>
- How to disable rules inline: <https://ansible-lint.readthedocs.io/usage/#muting-warnings-to-avoid-false-positives>
- Error line format (regex): `: ([0-9]+) failure\(s\), .* warning\(s\) in .* files processed`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `ANSIBLE_ANSIBLE_LINT` to fully disable this linter
  - `ANSIBLE_ANSIBLE_LINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `ANSIBLE_ANSIBLE_LINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `ANSIBLE_ANSIBLE_LINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `ANSIBLE_ANSIBLE_LINT_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `ANSIBLE_ANSIBLE_LINT_ERROR_GALAXY_INSTALL_FAILED`
  - `ANSIBLE_ANSIBLE_LINT_ERROR_SYNTAX_CHECK`
  - `ANSIBLE_ANSIBLE_LINT_ERROR_CONFIG_INVALID`
<!-- generated-descriptor-info-end -->

## Fix instructions

ansible-lint checks Ansible playbooks, roles and collections for syntax errors, deprecated usage, security risks and best-practice violations (60+ default rules). Fix strategy per common rule category:

- `fqcn`: replace short module names with fully qualified collection names (e.g. `git` -> `ansible.builtin.git`).
- `name`: add a descriptive `name:` to every task and play.
- `yaml`: fix YAML formatting (indentation, spacing, truthy values); `no-tabs`: replace tabs with spaces.
- `no-changed-when`: add a `changed_when:` condition to `command`/`shell` tasks so they report change status accurately.
- `risky-file-permissions`: set an explicit `mode:` on file/copy/template tasks.
- `risky-shell-pipe`: add `set -o pipefail` (via `args: executable: /bin/bash`) or avoid pipes; `command-instead-of-shell`: use `command` when shell features are not needed.
- `deprecated-module`: migrate to the replacement module named in the message.
- `jinja`: fix Jinja2 spacing and template errors (e.g. `{{var}}` -> `{{ var }}`); `literal-compare`: use `when: var` instead of `when: var == True`.
- `var-naming` / `loop-var-prefix`: rename variables to match the expected naming pattern.

Although MegaLinter does not apply fixes for this linter, ansible-lint itself can fix many findings locally: run `ansible-lint --fix` (reformats YAML and applies rule transforms; scope transforms with the `write_list` config option — YAML reformatting still runs even with `write_list: ["none"]`). Review the diff, then commit.

## Inline disable

Append a `# noqa: <rule-id>` comment on the line that triggers the rule (task-level rules: on the task's first offending line). Skip several rules with a space-separated list:

```yaml
- name: Clone repo
  become_user: alice # noqa: git-latest partial-become
  ansible.builtin.git: src=/path/to/git/repo dest=checkout

- name: Download config
  ansible.builtin.get_url:
    url: http://example.com/file.conf
    dest: "{{dest_proj_path}}/foo.conf" # noqa: jinja[spacing]
```

## Ignore via configuration

In the configuration file, use `skip_list` (rule never runs), `warn_list` (rule reports but never fails) and `exclude_paths`:

```yaml
skip_list:
  - fqcn[action-core]
warn_list:
  - experimental
exclude_paths:
  - .cache/
  - test/fixtures/
```

For per-file ignores, use a `.ansible-lint-ignore` file (or `.config/ansible-lint-ignore.txt`), one `<path> <rule>` pair per line; append `skip` to silence the residual warning. Generate it from current findings with `ansible-lint --generate-ignore` (overwrites the file):

```text
playbook.yml package-latest
playbook2.yml role-name skip
```

## When disabling is legitimate

- Rules tagged `experimental` or opinionated style rules (e.g. `name[casing]`) that conflict with an established team convention — prefer `warn_list` over `skip_list`.
- Third-party or vendored roles/collections you do not maintain — use `exclude_paths` rather than editing them.
- Intentional patterns a rule cannot verify, e.g. a `shell` pipe whose failure is handled, or a legacy module kept for OS compatibility — use a targeted `# noqa` on that line.
- Baseline adoption on a large legacy codebase — commit a generated `.ansible-lint-ignore` and shrink it over time.

Disabling the linter or its errors at MegaLinter level is the last resort.
