# Fix PERL_PERLCRITIC errors

<!-- generated-descriptor-info-start -->
- Linter: **perlcritic** (MegaLinter key: `PERL_PERLCRITIC`)
- Descriptor: **PERL** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/perl_perlcritic/>
- Official documentation: <https://metacpan.org/pod/Perl::Critic>
- Auto-fix support: no (errors must be fixed manually)
- Rules index: <https://metacpan.org/pod/Perl::Critic#THE-POLICIES>
- Rules configuration: <https://metacpan.org/pod/Perl::Critic#CONFIGURATION>
- How to disable rules inline: <https://metacpan.org/pod/Perl::Critic#BENDING-THE-RULES>
- Error line format (regex): `\(Severity: [0-9]+\)`
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `PERL_PERLCRITIC` to fully disable this linter
  - `PERL_PERLCRITIC_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `PERL_PERLCRITIC_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `PERL_PERLCRITIC_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `PERL_PERLCRITIC_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `PERL_PERLCRITIC_ERROR_CONFIG_INVALID`
  - `PERL_PERLCRITIC_ERROR_POLICY_NOT_FOUND`
<!-- generated-descriptor-info-end -->

## Fix instructions

perlcritic applies coding-standard policies (mostly derived from Damian Conway's *Perl Best Practices*) to Perl source code. Each violation reports a policy name and a severity from 5 (`gentle`, most severe) down to 1 (`brutal`, most pedantic). There is no auto-fix: rewrite the code manually so it satisfies the reported policy.

- Read the policy name in the violation message and look it up in the rules index to understand the expected idiom before changing code.
- Fix the highest-severity violations first (severity 5 and 4 cover the `bugs` and `security` themes: missing `use strict`/`use warnings`, two-argument `open`, unchecked system calls, string `eval`, ...).
- For `maintenance`/`complexity` policies (e.g. `ProhibitExcessComplexity`, `ProhibitDeepNests`), refactor long subroutines into smaller ones instead of suppressing.
- For `cosmetic` policies (quoting, interpolation, postfix controls), apply the exact replacement suggested by the policy documentation (e.g. use `q{}` instead of `""` for `ProhibitEmptyQuotes`).
- Reproduce a finding locally with `perlcritic --severity <n> <file>` and add `--verbose 11` to print the full policy explanation and PBP page reference.

## Inline disable

Use `## no critic` annotations (two hashes, on or before the offending line) and restore checking with `## use critic`. Always name the policies being disabled rather than using a bare `## no critic`.

```perl
## no critic (EmptyQuotes, PostfixControls)
$foo = "";               # Exempt from ProhibitEmptyQuotes
$barf = bar() if $foo;   # Exempt from ProhibitPostfixControls
## use critic
```

For block-level policies (e.g. complexity checks), put the annotation on the line that starts the block:

```perl
sub complicated_function {  ## no critic (ProhibitExcessComplexity)
```

## Ignore via configuration

In `.perlcriticrc`, global options come first, then one section per policy to tune it; prefix a section name with `-` to disable that policy entirely:

```ini
severity = 3
exclude = Variables::ProhibitPunctuationVars

[ControlStructures::ProhibitPostfixControls]
allow = if unless

[-CodeLayout::RequireTidyCode]
```

`exclude` takes a space-delimited list of patterns matched against policy names. perlcritic has no ignore-file mechanism for excluding source files: use `PERL_PERLCRITIC_FILTER_REGEX_EXCLUDE`, or place a file-wide `## no critic (PolicyName)` annotation at the top of the file.

## When disabling is legitimate

- The policy contradicts a deliberate project convention (Perl::Critic ships intentionally contradictory policies; pick one side in `.perlcriticrc` rather than fighting both).
- The idiom is required by context: postfix controls in one-liner-style scripts, punctuation variables in code intentionally close to the interpreter, XS or generated Perl code.
- A low-severity `cosmetic` policy fires on legacy code where mass rewriting would create churn without behavior benefit — raise the global `severity` threshold instead of suppressing many policies one by one.
- Disabling the whole linter at MegaLinter level (`DISABLE_LINTERS`) is the last resort; prefer inline annotations or `.perlcriticrc` tuning.
