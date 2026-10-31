# Fix DART_DARTANALYZER errors

<!-- generated-descriptor-info-start -->
- Linter: **dartanalyzer** (MegaLinter key: `DART_DARTANALYZER`)
- Descriptor: **DART** (language)
- MegaLinter documentation: <https://megalinter.io/beta/descriptors/dart_dartanalyzer/>
- Official documentation: <https://dart.dev/tools/dart-analyze>
- Auto-fix support: no (errors must be fixed manually)
- Configuration file: `analysis_options.yaml` (custom path can be defined with `DART_DARTANALYZER_CONFIG_FILE`)
- Rules index: <https://dart.dev/tools/linter-rules#rules>
- Rules configuration: <https://dart.dev/tools/analysis>
- How to disable rules inline: <https://dart.dev/tools/analysis#ignoring-rules>
- MegaLinter tuning variables (in `.mega-linter.yml`):
  - `DISABLE_LINTERS`: add `DART_DARTANALYZER` to fully disable this linter
  - `DART_DARTANALYZER_DISABLE_ERRORS: true`: keep the linter active but non-blocking
  - `DART_DARTANALYZER_DISABLE_ERRORS_IF_LESS_THAN: <number>`: block only when the error count reaches the threshold — useful on a first install to accept the existing technical debt while preventing it from growing
  - `DART_DARTANALYZER_FILTER_REGEX_EXCLUDE`: regex of files to exclude from this linter
  - `DART_DARTANALYZER_ARGUMENTS`: additional CLI arguments for the linter
- Known non-lint failure patterns (configuration/environment issues, see resolutions in the MegaLinter documentation page):
  - `DART_DARTANALYZER_ERROR_MISSING_PUBSPEC`
  - `DART_DARTANALYZER_ERROR_PACKAGES_NOT_RESOLVED`
<!-- generated-descriptor-info-end -->

## Fix instructions

`dart analyze` performs static analysis on Dart code, reporting errors, warnings and info-level issues
(compilation errors, type problems, and violations of the lint rules enabled in the configuration file).

- Read each diagnostic's rule name (e.g. `invalid_assignment`, `always_declare_return_types`) and look it up
  in the rules index to understand the intent before changing code.
- Fix type and compilation errors first: they are always blocking and often cascade into further diagnostics.
- For lint-rule violations, apply the rule's documented "good" pattern rather than restructuring the code.
- Many diagnostics have automated fixes: run `dart fix --dry-run` to preview them, then `dart fix --apply`
  to apply. Only diagnostics with an associated fix are handled, and lint rules must be enabled in the
  configuration file for their fixes to run.
- Ensure dependencies are resolved (`dart pub get`) before analyzing: unresolved packages cause spurious
  `uri_does_not_exist` errors (see the known non-lint failure patterns above).
- Reproduce locally with `dart analyze <directory>`; `--fatal-infos` also fails on info-level issues and
  `--no-fatal-warnings` downgrades warnings.

## Inline disable

Suppress a diagnostic on a single line with an `// ignore:` comment on the line above or at the end of the
line; suppress for a whole file with `// ignore_for_file:` at the top. Multiple rule names are comma-separated.

```dart
// ignore: invalid_assignment
int x = '';

int y = ''; // ignore: invalid_assignment, const_initialized_with_non_constant_value

// ignore_for_file: unused_local_variable
// ignore_for_file: type=lint  (suppresses all lint rules in the file)
```

## Ignore via configuration

In the configuration file (placed at the package root next to `pubspec.yaml`), disable a rule inherited from
an included rule set with key-value syntax, exclude files with glob patterns under `analyzer: exclude`, or
change a diagnostic's severity (including `ignore`) under `analyzer: errors`:

```yaml
include: package:lints/recommended.yaml

linter:
  rules:
    avoid_shadowing_type_parameters: false

analyzer:
  exclude:
    - lib/**.g.dart
    - test/_data/**
  errors:
    todo: ignore
    dead_code: info
```

Note: within a single `rules` entry you cannot mix list syntax and key-value syntax. There is no separate
ignore file; exclusions live in this configuration file.

## When disabling is legitimate

- Generated code (`*.g.dart`, `*.freezed.dart`, protobuf output): exclude it under `analyzer: exclude`
  instead of fixing files that will be regenerated.
- A rule from an included rule set (e.g. `package:lints/recommended.yaml`) conflicts with a deliberate
  project convention: disable that single rule in the configuration file rather than dropping the rule set.
- A one-off construct is intentional and correct (e.g. a test asserting a type error): use a targeted
  `// ignore:` on that line, never a file-wide or global suppression.
- `todo`-style informational diagnostics that the team tracks elsewhere can be set to `ignore` under
  `analyzer: errors`.

Disabling the linter at MegaLinter level (`DISABLE_LINTERS`, `DART_DARTANALYZER_DISABLE_ERRORS`) is the
last resort, only when the tool itself misbehaves.
