---
name: add-reporter
description: Add a new output reporter to MegaLinter. Use when adding support for a new CI system or output format.
allowed-tools: Read Grep Glob Edit Write
argument-hint: [reporter-name]
---

Guide through adding a new reporter named `$ARGUMENTS` to MegaLinter.

Steps:

1. **Create the class** in `megalinter/reporters/<Name>Reporter.py` extending `megalinter.Reporter`
2. **Implement required methods**:
   - `manage_activation()` — check env var like `<NAME>_REPORTER=true` to enable/disable
   - `produce_report()` — generate the report output
   - Optionally: `initialize()`, `add_report_item()`
3. **Register the reporter** — check how existing reporters are discovered and loaded in `megalinter/MegaLinter.py`
4. **Reference patterns** from existing reporters:
   - Simple output: `ConsoleReporter.py`, `TapReporter.py`
   - CI integration: `GithubCommentReporter.py`, `GitlabCommentReporter.py`
   - File output: `JsonReporter.py`, `SarifReporter.py`
   - External service: `ApiReporter.py`, `EmailReporter.py`
5. **Update documentation** — add a docs page describing configuration
6. **Update `CHANGELOG.md`** in the repository root (not docs/)
7. **Branch naming**: use `user/add-<reporter-name>-reporter`
