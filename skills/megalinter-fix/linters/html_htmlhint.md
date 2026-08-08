# Fix HTML_HTMLHINT errors

<!-- generated-descriptor-info-start -->
- Linter: **htmlhint** (MegaLinter key: `HTML_HTMLHINT`)
- Descriptor: **HTML** (format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/html_htmlhint/>
- Official documentation: <https://htmlhint.com/>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.htmlhintrc` (custom path can be defined with `HTML_HTMLHINT_CONFIG_FILE`)
- Rules index: <https://htmlhint.com/docs/user-guide/list-rules>
- Rules configuration: <https://htmlhint.com/configuration/>
- How to disable rules inline: <https://htmlhint.com/configuration/>
- Error line format (regex): `found ([0-9]+) errors in`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `HTML_HTMLHINT` to fully disable this linter
  - `HTML_HTMLHINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `HTML_HTMLHINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `HTML_HTMLHINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `HTML_HTMLHINT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

HTMLHint is a static analyzer for HTML that checks document structure, attribute hygiene, and accessibility basics. It has no auto-fix: edit the markup manually for each reported rule.

Fix strategy per common rule category:

- **Doctype and head** (`doctype-first`, `doctype-html5`, `title-require`, `html-lang-require`, `meta-charset-require`, `meta-viewport-require`): put `<!DOCTYPE html>` as the very first non-comment content, add a non-empty `<title>`, a valid `lang` attribute on `<html>`, and the required `<meta>` tags in `<head>`.
- **Tags** (`tag-pair`, `tagname-lowercase`, `tag-no-obsolete`): close every unclosed tag, lowercase tag names, replace obsolete tags with modern equivalents.
- **Attributes** (`attr-lowercase`, `attr-value-double-quotes`, `attr-no-duplication`, `src-not-empty`): lowercase attribute names, wrap values in double quotes, remove duplicated attributes, give `src` a real value.
- **IDs** (`id-unique`): rename duplicated `id` values so each is unique in the document; use classes for shared styling.
- **Escaping** (`spec-char-escape`): replace literal `<` and `>` in text content with `&lt;` and `&gt;`.
- **Accessibility** (`alt-require`, `input-requires-label`, `button-type-require`, `h1-require`, `frame-title-require`): add `alt` to images (or `aria-hidden="true"` for decorative ones), associate a `<label>` with every input, set an explicit `type` on buttons, keep one non-empty `<h1>`, and title frames/iframes.

Reproduce locally with `htmlhint path/to/file.html` (or a glob like `htmlhint "src/**/*.html"`).

## Inline disable

Use HTML comment directives, optionally followed by one or more rule names:

```html
<!-- htmlhint-disable-next-line attr-lowercase -->
<div DATA-Custom="x"></div>

<!-- htmlhint-disable tag-pair spec-char-escape -->
<p>legacy block left as-is
<!-- htmlhint-enable -->
```

`<!-- htmlhint-disable -->` without rule names disables all rules until `<!-- htmlhint-enable -->`; prefer the rule-scoped forms.

## Ignore via configuration

Disable a rule for the whole project by setting it to `false` in the configuration file (JSON):

```json
{
  "tagname-lowercase": true,
  "attr-value-double-quotes": false
}
```

There is no dedicated ignore file; exclude paths with the CLI ignore option, e.g. `--ignore="**/vendor/**,**/dist/**"` (pass it through `HTML_HTMLHINT_ARGUMENTS`), or use the MegaLinter filter variable from the block above.

## When disabling is legitimate

- Template fragments (partials, includes, email templates) that are intentionally not full documents: head-related rules like `doctype-first`, `title-require` or `h1-require` do not apply.
- Server-side or JS template syntax (Jinja, Handlebars, Angular...) that HTMLHint misparses, typically triggering `spec-char-escape` or `attr-value-double-quotes` false positives.
- Generated or vendored HTML (build output, third-party widgets) that should be excluded by path rather than fixed.
- Disabling the whole linter at MegaLinter level is the last resort; prefer a rule-scoped inline comment or a configuration entry.
