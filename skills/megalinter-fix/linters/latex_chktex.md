# Fix LATEX_CHKTEX errors

<!-- generated-descriptor-info-start -->
- Linter: **chktex** (MegaLinter key: `LATEX_CHKTEX`)
- Descriptor: **LATEX** (format)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/latex_chktex/>
- Official documentation: <https://www.nongnu.org/chktex>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `.chktexrc` (custom path can be defined with `LATEX_CHKTEX_CONFIG_FILE`)
- Rules index: <https://www.nongnu.org/chktex/>
- Rules configuration: <https://github.com/amaloz/dotfiles/blob/master/chktexrc>
- How to disable rules inline: <https://www.nongnu.org/chktex/>
- Error line format (regex): `[0-9]+ in .* line [0-9]+:`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `LATEX_CHKTEX` to fully disable this linter
  - `LATEX_CHKTEX_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `LATEX_CHKTEX_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `LATEX_CHKTEX_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `LATEX_CHKTEX_ARGUMENTS`: additional CLI arguments for the linter
<!-- generated-descriptor-info-end -->

## Fix instructions

chktex finds typographic errors in LaTeX sources: spacing, dashes, quotes, math-mode
punctuation, and use of TeX primitives where LaTeX equivalents exist. There is no
auto-fix; edit the source manually. Each warning has a number — fix the most common ones as follows:

- Warning 1 (command terminated with space): end the command with `{}` or `\` (e.g. `\LaTeX{} is` instead of `\LaTeX is`)
- Warning 3 (enclose previous parenthesis with `{}`): wrap the construct in braces
- Warning 8 (wrong length of dash): use `-` for hyphenation, `--` for ranges, `---` for punctuation dashes
- Warnings 9/17 (mismatched `]`/`)` counts): balance delimiters, or suppress inline when intentional (e.g. half-open intervals like `$[0,\infty)$`)
- Warning 12 (interword spacing): write `\` after abbreviations (e.g. `e.g.\ like`)
- Warning 13 (intersentence spacing): write `\@` before a period ending a sentence after an uppercase letter; the warning is suppressed if `\frenchspacing` is used
- Warning 18 (double quotes): use `` `` `` and `''` instead of `"`
- Warning 24 (space before page-reference punctuation): delete the space, use `~\ref{...}`
- Warning 38 (punctuation in front of/after quotes): move the punctuation inside/outside the quotes as reported

Rerun `chktex file.tex` (or MegaLinter) after each batch of fixes to confirm.

## Inline disable

Add a case-insensitive comment at the end of the offending line, of the form `% chktex ##`
where `##` is the warning number. To suppress two different warnings on the same line,
repeat `chktex` inside one comment. To suppress a warning for the remainder of the file,
use `% chktex-file ##`.

```latex
% chktex-file 18
$[0,\infty)$          % chktex 9
Jordan--H\"older on $[0,\infty)$  % chktex 8 chktex 9
```

Negative numbers (`% chktex -4`) target named user-regex warnings without silencing
system warning 44. The `-L` / `--nolinesupp` CLI flag disables all these suppressions,
which is useful for a final strict pass.

## Ignore via configuration

The configuration file is a list of variable assignments. Useful entries:

- `CmdLine { -n8 -n24 }`: default CLI options, `-n##` mutes a warning globally (`-w##` / `-e##` re-enable as warning/error)
- `WipeArg { \label:{} \cite:[]{} }`: ignore the arguments of given commands
- `VerbEnvir { verbatim listing tikzpicture }`: ignore the whole contents of given environments
- `DashExcpt { Birch--Swinnerton-Dyer }`: accept listed words regardless of dash rules (warning 8)

chktex has no ignore-file mechanism to exclude whole files; use the MegaLinter
exclusion variable listed in the block above instead.

## When disabling is legitimate

- Half-open intervals such as `$[0,\infty)$` legitimately trigger the delimiter-match warnings 9/17: suppress inline
- Warning 18 is a false positive in files where `"` is an active character (e.g. with the `babel` package): use `% chktex-file 18`
- Ranges of names with real double dashes (e.g. `Jordan--H\"older` as a two-person theorem name) are correct despite warning 8: add them to `DashExcpt`
- Verbatim-like environments from packages chktex does not know (code listings, TikZ) produce noise: declare them in `VerbEnvir`

Disabling the whole linter or a rule at MegaLinter level is the last resort: prefer a
line suppression, then a `.chktexrc` entry scoped to the project.
