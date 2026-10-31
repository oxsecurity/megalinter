# Fix LUA_STYLUA errors

<!-- generated-descriptor-info-start -->
- Linter: **stylua** (MegaLinter key: `LUA_STYLUA`)
- Descriptor: **LUA** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/lua_stylua/>
- Official documentation: <https://github.com/JohnnyMorganz/StyLua>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `stylua.toml` (custom path can be defined with `LUA_STYLUA_CONFIG_FILE`)
- Rules index: <https://roblox.github.io/lua-style-guide/>
- Rules configuration: <https://github.com/JohnnyMorganz/StyLua?tab=readme-ov-file#configuration>
- How to disable rules inline: <https://github.com/JohnnyMorganz/StyLua?tab=readme-ov-file#ignoring-parts-of-a-file>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `LUA_STYLUA` to fully disable this linter
  - `LUA_STYLUA_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `LUA_STYLUA_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `LUA_STYLUA_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `LUA_STYLUA_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

StyLua is a deterministic code formatter for Lua (5.1-5.4, LuaJIT, Luau, CfxLua): it parses the code and
prints it back enforcing a consistent style (indentation, quotes, line width, call parentheses...).
It reports no individual rules — a failure only means files are not formatted as StyLua would write them.

- Do not hand-edit whitespace to satisfy the checker: run the formatter itself on the reported files:

  ```bash
  stylua src/ foo.lua bar.lua
  ```

- Verify locally without modifying files with `stylua --check <path>` (this check mode is what fails in CI).
- If the formatted output looks wrong for the project, adjust style options in the configuration file
  (see below) instead of fighting the formatter, then re-run it so all files match the new settings.

## Inline disable

Use `-- stylua: ignore` comments. For a single statement:

```lua
-- stylua: ignore
local matrix = { { 0, 0, 0 }, { 0, 0, 0 }, { 0, 0, 0 } }
```

For a whole block, wrap it with start/end markers:

```lua
-- stylua: ignore start
local   aligned    =   1
local   manually   =   2
-- stylua: ignore end
```

## Ignore via configuration

The configuration file selects formatting options rather than rules to disable, e.g.:

```toml
column_width = 100
indent_type = "Spaces"
indent_width = 2
quote_style = "AutoPreferSingle"
```

To exclude files, add a `.styluaignore` file at the workspace root (gitignore-like syntax):

```text
vendor/
*.spec.lua
```

Negated glob filters on the command line also work: `stylua -g '*.lua' -g '!*.spec.lua' -- .`

## When disabling is legitimate

- Hand-aligned data tables (matrices, lookup tables, ASCII art) whose manual layout is more readable
  than the formatted output — use `-- stylua: ignore` around them.
- Generated or vendored Lua code that should keep its upstream formatting — exclude it via
  `.styluaignore` rather than reformatting it.
- Code that must stay byte-identical to an external source (embedded snippets, patch targets).
- A team-wide divergence from a default (tabs vs spaces, line width) belongs in the configuration
  file, not in disables. Disabling at MegaLinter level is the last resort.
