# Fix SPELL_LYCHEE errors

<!-- generated-descriptor-info-start -->
- Linter: **lychee** (MegaLinter key: `SPELL_LYCHEE`)
- Descriptor: **SPELL** (other)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/spell_lychee/>
- Official documentation: <https://lychee.cli.rs>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `lychee.toml` (custom path can be defined with `SPELL_LYCHEE_CONFIG_FILE`)
- Ignore file: `.lycheeignore`
- Rules index: <https://lychee.cli.rs/guides/cli/>
- Rules configuration: <https://lychee.cli.rs/guides/config/>
- How to ignore files and directories: <https://lychee.cli.rs/recipes/excluding-links/>
- Error line format (regex): `Errors\.+([0-9]+)`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `SPELL_LYCHEE` to fully disable this linter
  - `SPELL_LYCHEE_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `SPELL_LYCHEE_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `SPELL_LYCHEE_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `SPELL_LYCHEE_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

lychee is a fast, asynchronous link checker: it detects broken URLs and mail addresses in Markdown, HTML and other files. There is no auto-fix; repair each reported link manually.

- `404 Not Found` or similar 4xx: the target page is gone. Find the new location of the content and update the URL, or remove the link if the resource no longer exists.
- Redirect chains or moved pages: replace the old URL with its final destination.
- `429 Too Many Requests`: the site rate-limits the checker, the link is usually fine. Accept the status code (`accept = ["200", "429"]` in the config, or `--accept '200..=204, 429'`), or slow lychee down with `--host-concurrency` / `--host-request-interval`.
- Timeouts on slow sites: raise `timeout` (default 20s) or `max_retries` / `retry_wait_time` in the config, or pass `--accept-timeouts` to treat timeouts as valid.
- Private, local or loopback addresses (e.g. `http://localhost:8080`): keep them if intentional and run with `--exclude-all-private` (via the linter arguments variable).
- Broken relative links to local files: fix the path or restore the missing file.
- Broken fragments/anchors (when `--include-fragments` is enabled): fix the heading or anchor name the fragment points to.

Re-run on changed files only to iterate quickly; `--offline` restricts checks to local files, and `--cache` reuses results from `.lycheecache` between runs.

## Inline disable

lychee has no inline suppression comment inside checked files. The closest alternative is excluding the URL pattern via `.lycheeignore` or the `exclude` list in the configuration file (see below).

## Ignore via configuration

Add one URL or regex per line to `.lycheeignore` at the repository root (patterns match the full URL, scheme included):

```text
https://www.example.com/private-page
# Comments are supported, and so is regex
https?:\/\/(www\.)?linkedin\.com
^mailto:
```

Or use the `exclude` list in the configuration file — values are treated as regular expressions, and includes take precedence over excludes:

```toml
exclude = [
    '^https://example\.com/home$',
    '^https://(www\.)?linkedin\.com'
]
accept = ["200", "429"]
timeout = 20
max_retries = 2
```

## When disabling is legitimate

- Sites that block bots or rate-limit automated requests (LinkedIn, some CDNs): the link works in a browser but returns 403/429 to lychee — exclude the domain or accept the status code.
- Intentionally unreachable URLs: example/placeholder domains in documentation, or internal/private URLs only resolvable inside a VPN.
- Auto-generated files containing templated or not-yet-published URLs (e.g. links that will exist only after release).
- Flaky remote hosts causing intermittent timeouts despite retries — prefer `accept_timeouts` or a domain exclusion over ignoring the file.

Disabling the linter at MegaLinter level (`DISABLE_LINTERS` or `SPELL_LYCHEE_DISABLE_ERRORS`) is the last resort.
