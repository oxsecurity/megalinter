# Fix XML_XMLLINT errors

<!-- generated-descriptor-info-start -->
- Linter: **xmllint** (MegaLinter key: `XML_XMLLINT`)
- Descriptor: **XML** (format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/xml_xmllint/>
- Official documentation: <https://gitlab.gnome.org/GNOME/libxml2/-/wikis/home>
- Auto-fix support: **yes** — add `XML_XMLLINT` (or `all`) to the `APPLY_FIXES` variable, or run locally `npx mega-linter-runner --linter XML_XMLLINT --fix` (runner and image versions follow `MEGALINTER_VERSION` of `.mega-linter.yml`: use `npx mega-linter-runner@beta` only when that property is `beta`)
- Rules configuration: <https://gnome.pages.gitlab.gnome.org/libxml2/xmllint.html>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `XML_XMLLINT` to fully disable this linter
  - `XML_XMLLINT_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `XML_XMLLINT_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `XML_XMLLINT_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `XML_XMLLINT_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

xmllint (from libxml2) checks that XML files are well-formed and can optionally validate them against a DTD, W3C XML Schema, or RelaxNG. Errors fall into a few categories, identifiable by exit code: not well-formed / unreadable document (exit 4), DTD errors (exit 2), and validation errors (exit 3).

- Well-formedness errors (the most common in MegaLinter runs): fix the XML syntax at the reported line — close every open tag, quote all attribute values, escape literal `&` as `&amp;` and `<` as `&lt;`, keep a single root element, and match start/end tag names exactly (XML is case-sensitive).
- Encoding/parse errors: ensure the file content matches the encoding declared in the `<?xml ... encoding="..."?>` prolog and remove invalid control characters.
- Namespace problems: declare every used prefix with an `xmlns:prefix="uri"` attribute before use.
- Validation errors (only if `--valid`, `--dtdvalid`, `--schema` or `--relaxng` was added via extra arguments): make the document conform to the schema — add missing required elements/attributes, remove undeclared ones, fix element ordering.
- Unresolvable DTD or schema references: point the `XML_CATALOG_FILES` environment variable to an XML catalog that redirects remote URLs to local copies.

Formatting: xmllint can rewrite files with `xmllint --format file.xml --output file.xml`. In MegaLinter this is the auto-fix mode; enable it with `XML_XMLLINT_AUTOFORMAT: true` together with `XML_XMLLINT_CLI_LINT_MODE: file`, and tune indentation with `XML_XMLLINT_INDENT` (default two spaces). Auto-fix only reformats — it cannot repair a document that is not well-formed, so fix syntax errors manually first.

## Inline disable

xmllint has no inline suppression mechanism: there is no comment syntax that disables a well-formedness or validation error for a line or block. The closest alternatives are excluding the file from the linter (see below) or relaxing the CLI behavior globally, e.g. adding `--nowarning` to the extra arguments to silence parser/validator warnings (errors still fail).

## Ignore via configuration

xmllint has no configuration file or ignore file of its own — all behavior is driven by CLI flags and environment variables. To skip files, use the MegaLinter file-exclusion regex named in the block above, in `.mega-linter.yml`:

```yaml
XML_XMLLINT_FILTER_REGEX_EXCLUDE: "(third_party/|\\.generated\\.xml$)"
```

To change validation behavior, append flags through the extra-arguments variable (for example `--nowarning`, or `--schema mySchema.xsd` to add schema validation). Use `XML_CATALOG_FILES` to resolve DTD/schema URLs from a local catalog instead of the network.

## When disabling is legitimate

- Generated or vendored XML (build outputs, third-party fixtures) that is not hand-maintained: exclude it via the filter regex rather than reformatting it.
- Test fixtures that are intentionally malformed XML (e.g. bad files used to test other tools): exclude those paths.
- Files with an XML-like extension that are not actually strict XML (templated XML with placeholders that only becomes valid after rendering).
- Documents referencing remote DTDs unreachable from CI: prefer an XML catalog via `XML_CATALOG_FILES` before excluding the file.

Disabling the linter entirely at MegaLinter level (`DISABLE_LINTERS`) is the last resort — prefer fixing the file, then a targeted exclusion.
