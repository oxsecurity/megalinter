# Fix RST_RSTCHECK errors

<!-- generated-descriptor-info-start -->
- Linter: **rstcheck** (MegaLinter key: `RST_RSTCHECK`)
- Descriptor: **RST** (format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/rst_rstcheck/>
- Official documentation: <https://github.com/myint/rstcheck>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.rstcheck.cfg` (custom path can be defined with `RST_RSTCHECK_CONFIG_FILE`)
- Rules configuration: <https://github.com/myint/rstcheck#configuration-file>
- How to disable rules inline: <https://github.com/myint/rstcheck#ignore-specific-errors>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `RST_RSTCHECK` to fully disable this linter
  - `RST_RSTCHECK_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `RST_RSTCHECK_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `RST_RSTCHECK_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `RST_RSTCHECK_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

rstcheck validates reStructuredText syntax (docutils messages such as `(ERROR/3)` and `(SEVERE/4)`) and additionally checks the syntax of code inside `code-block` directives (Bash, C, C++, JSON, XML, Python, RST, doctest). There is no auto-fix: correct each reported location manually.

- `Title overline & underline mismatch` / `Title underline too short` (SEVERE/ERROR): make the `===`/`---` adornment line at least as long as the title text, and identical for overline and underline.
- Syntax errors reported inside a `code-block`: fix the embedded snippet itself (e.g. the Python `SyntaxError` or unbalanced C braces), not the surrounding RST.
- `Unknown directive type` / `Unknown interpreted text role`: fix the typo, or if it is a legitimate Sphinx/custom directive or role that plain docutils does not know, add it to `ignore_directives` / `ignore_roles` in the configuration (see below).
- `Undefined substitution referenced`: define the missing `.. |name| replace::` substitution, or add it to `ignore_substitutions` if it is provided externally.
- `Duplicate implicit target name` / `Hyperlink target ... is not referenced`: rename duplicated section titles or remove/reference the unused target.

## Inline disable

Use rstcheck flow-control comments (RST comments starting with `rstcheck:`). `ignore-next-code-block` skips syntax checking of the code block that follows; `<key>=<value>` comments (e.g. `ignore-languages`, `ignore-directives`, `ignore-roles`) apply to the whole file regardless of placement and regardless of other configuration:

```rst
.. rstcheck: ignore-next-code-block
.. code-block:: python

    print("Hello World"  # deliberately incomplete example

.. rstcheck: ignore-languages=cpp
.. rstcheck: ignore-directives=my-custom-directive
```

There is no per-line suppression of docutils messages; for a single message pattern use `ignore_messages` in the configuration file instead.

## Ignore via configuration

In the configuration file (INI format, `[rstcheck]` section), use the `ignore_*` options. `ignore_messages` takes a regular expression matched against docutils messages; the other options take comma-separated lists:

```ini
[rstcheck]
report_level = WARNING
ignore_directives = automodule, my-directive
ignore_roles = src, RFC
ignore_substitutions = image_link
ignore_languages = cpp
ignore_messages = (Duplicate implicit target.*|Hyperlink target ".*" is not referenced\.$)
```

The same options are available in `pyproject.toml` under `[tool.rstcheck]` (TOML lists instead of comma-separated strings). rstcheck has no dedicated ignore-file mechanism for excluding paths: exclude files with the MegaLinter filter variable listed in the block above.

## When disabling is legitimate

- Sphinx-only or project-specific directives and roles (`automodule`, `toctree`, custom extensions) that plain docutils flags as unknown: add them to `ignore_directives` / `ignore_roles` rather than rewriting valid docs.
- Intentionally incomplete or pseudo-code snippets shown for illustration: mark them with `.. rstcheck: ignore-next-code-block` or use a language rstcheck does not check.
- `Hyperlink target is not referenced` on anchors kept for external deep links, or `Duplicate implicit target name` in generated/concatenated documents: filter them with a precise `ignore_messages` regex.
- Generated RST (e.g. API docs produced by tooling) should be excluded from linting rather than hand-patched.

Disabling the linter or the rule at MegaLinter level (`DISABLE_LINTERS`, `RST_RSTCHECK_DISABLE_ERRORS`) is the last resort, once targeted fixes and rstcheck-level configuration are exhausted.
