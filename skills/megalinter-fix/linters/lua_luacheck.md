# Fix LUA_LUACHECK errors

<!-- generated-descriptor-info-start -->
- Linter: **luacheck** (MegaLinter key: `LUA_LUACHECK`)
- Descriptor: **LUA** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/lua_luacheck/>
- Official documentation: <https://luacheck.readthedocs.io>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.luacheckrc` (custom path can be defined with `LUA_LUACHECK_CONFIG_FILE`)
- Rules index: <https://luacheck.readthedocs.io/en/stable/warnings.html>
- Rules configuration: <https://luacheck.readthedocs.io/en/stable/config.html>
- How to disable rules inline: <https://luacheck.readthedocs.io/en/stable/inline.html>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `LUA_LUACHECK` to fully disable this linter
  - `LUA_LUACHECK_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `LUA_LUACHECK_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `LUA_LUACHECK_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `LUA_LUACHECK_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `LUA_LUACHECK_ERROR_CONFIG_INVALID`
<!-- generated-descriptor-info-end -->

## Fix instructions

luacheck is a static analyzer for Lua that reports syntax errors and warnings identified by three-digit codes grouped by category. There is no auto-fix: correct the code manually according to the warning category.

- `011` (syntax error): fix the Lua syntax at the reported position first — other warnings on the file may be side effects.
- `1xx` (globals — e.g. `111` setting, `113` accessing an undefined global): declare the variable `local`, or if the global is legitimate (API of a host application, test framework), declare it via `globals` / `read_globals` in the configuration or pick the right `std` set instead of touching the code.
- `2xx` (unused variables — `211` unused local, `212` unused argument, `213` unused loop variable): remove the variable, or rename it `_` when the value must be received but is intentionally unused.
- `3xx` (unused values, `321` accessing an uninitialized variable): drop the dead assignment or initialize the variable before use.
- `4xx` (shadowing — `411`/`421`/`431` redefining or shadowing a local, argument or upvalue): rename the inner variable to a distinct name.
- `5xx` (control flow — `511` unreachable code, `512` loop executed at most once, `541`/`542` empty blocks, `561` cyclomatic complexity): delete dead code, simplify the condition, or split the function.
- `6xx` (formatting — `611`-`614` whitespace, `621` inconsistent indentation, `631` line too long): trim trailing whitespace, normalize indentation, wrap long lines (default limit 120).

## Inline disable

Use a comment starting with `luacheck:` followed by comma-separated options. With code on the same line only that line is affected; on its own line it applies until the end of the current closure (whole file when at top level).

```lua
local foo = g1(g2) -- luacheck: globals g1 g2
-- luacheck: ignore 212
-- luacheck: no unused args
```

Use `push` / `pop` to limit the scope of a suppression:

```lua
-- luacheck: push ignore foo
foo() -- no warning
-- luacheck: pop
```

`ignore` without arguments silences all warnings in scope; `ignore <name-or-code>` targets a variable name or a warning code.

## Ignore via configuration

The configuration file is plain Lua setting option variables. Disable warning codes with `ignore`, allow globals with `globals` / `read_globals` (or a `std` set), and exclude paths with `exclude_files`:

```lua
std = "min"
ignore = {"212"}                       -- warning codes or patterns
read_globals = {"ngx", "jit"}          -- accessible but not modifiable
exclude_files = {"vendor/", "*.min.lua"}
max_line_length = 100                  -- or false to disable 631
```

Per-path overrides use the `files` table:

```lua
files["**/spec/**/*_spec.lua"].std = "+busted"
files["src/legacy/**"] = {ignore = {"211", "631"}}
```

There is no separate ignore file: use `exclude_files` in the configuration.

## When disabling is legitimate

- Globals injected by a host environment (OpenResty `ngx`, LuaJIT `jit`, game engines) or a test framework: declare them via `read_globals` or a `std` set (e.g. `+busted`) rather than ignoring `11x` warnings.
- Callback signatures imposed by an API force unused arguments (`212`): prefer renaming to `_`; ignore the code only when renaming is not possible.
- Vendored or generated Lua (minified bundles, generated bindings): exclude the paths with `exclude_files`.
- Codebase with an intentional different line-length or formatting convention: adjust `max_line_length` or ignore `6xx` codes in the configuration.

Disabling at MegaLinter level (`DISABLE_LINTERS`, `LUA_LUACHECK_DISABLE_ERRORS`, filter regexes) is the last resort — prefer fixing the code, then inline or configuration-level suppression.
