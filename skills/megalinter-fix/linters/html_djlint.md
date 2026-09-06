# Fix HTML_DJLINT errors

<!-- generated-descriptor-info-start -->
- Linter: **djlint** (MegaLinter key: `HTML_DJLINT`)
- Descriptor: **HTML** (format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/html_djlint/>
- Official documentation: <https://djlint.com/>
- Auto-fix support: no (errors must be fixed manually)
- Rules index: <https://djlint.com/docs/linter/>
- Rules configuration: <https://djlint.com/docs/configuration/>
- How to disable rules inline: <https://djlint.com/docs/ignoring-code/>
- Error line format (regex): `[A-Z][0-9]{3} `
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `HTML_DJLINT` to fully disable this linter
  - `HTML_DJLINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `HTML_DJLINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `HTML_DJLINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `HTML_DJLINT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

djlint lints HTML templates (Django, Jinja, Nunjucks, Handlebars, Liquid, Go...) for HTML validity, accessibility and template syntax. Rule codes are prefixed by scope: `H` HTML rules, `T` template syntax, `D` Django-specific, `J` Jinja-specific, `M` Handlebars, `N` Nunjucks.

Fix strategy per common category:

- `H005`/`H007`/`H016` (document structure): add the missing `lang` attribute on `<html>`, the `<!DOCTYPE html>` declaration, or the `<title>` tag.
- `H008`-`H012` (attribute formatting): quote attribute values with double quotes, lowercase tag and attribute names, fix spacing around `=`.
- `H013`/`H030`/`H042` (accessibility and SEO): add `alt` text on images, a meta description, and matching `for`/`id` between `<label>` and its input.
- `T001`/`T027`/`T038` (template syntax): add whitespace inside `{{ }}` variables, close unclosed strings in template tags, and pair every block tag with its matching end tag.
- `D004`/`D018` and `J004`/`J018` (framework URLs): replace hard-coded static and internal URLs with `{% static %}`/`{% url %}` (Django) or `url_for()` (Flask/Jinja).

djlint also ships a formatter (`djlint <path> --reformat`) that fixes indentation and formatting issues, but the lint rules reported here (H/T/D/J codes) generally require manual edits as shown above. Make sure the correct `profile` (template language) is configured, otherwise framework-specific rules can misfire.

## Inline disable

Wrap the offending block between `djlint:off` and `djlint:on` comments, optionally restricted to specific rule codes appended after `off` (comma-separated):

```html
<!-- djlint:off H025,H026 -->
<p>
<!-- djlint:on -->
```

Template-comment variants work too, e.g. `{# djlint:off #}` ... `{# djlint:on #}` (Django/Jinja) or `{{!-- djlint:off --}}` (Handlebars).

## Ignore via configuration

Configure djlint in `pyproject.toml` under `[tool.djlint]`, or in `.djlintrc` (JSON) / `djlint.toml`:

```toml
[tool.djlint]
profile = "django"
ignore = "H014,H015"
extend_exclude = "vendor,generated"

[tool.djlint.per-file-ignores]
"templates/legacy.html" = "H026,H025"
```

- `ignore` disables rule codes globally; `include` re-enables optional ones.
- `exclude` replaces the default excluded paths, `extend_exclude` adds to them.
- `per-file-ignores` disables rules for a single file only.

There is no separate ignore file; use `exclude`/`extend_exclude` (or `HTML_DJLINT_FILTER_REGEX_EXCLUDE`) for path-based exclusion.

## When disabling is legitimate

- The `profile` does not match the template language and framework-specific rules (D/J/M/N) fire on constructs that are valid in your engine.
- Third-party, vendored or generated templates you do not control (exclude the paths rather than editing them).
- Intentional non-standard markup, e.g. partial templates without `<!DOCTYPE>`/`<title>` (H007/H016) because they are included into a full page.
- Rules conflicting with another formatter or house style (e.g. attribute quoting) already enforced elsewhere.

Prefer a targeted inline `djlint:off CODE` or a `per-file-ignores` entry over global `ignore`; disabling at MegaLinter level (`DISABLE_LINTERS` / `HTML_DJLINT_DISABLE_ERRORS`) is the last resort.
