---
description: Documentation conventions for mkdocs-material
globs: ["docs/**/*.md", "*.md"]
---

# Documentation Rules

## mkdocs-material Compliance
All markdown files must be mkdocs-material compliant:
- Always leave a blank line after a heading (`##`, `###`, etc.)
- Always leave a blank line before a bulleted list or numbered list
- Always leave a blank line after a bulleted list or numbered list

## Auto-Generated Documentation
Documentation pages under `docs/descriptors/` are generated from YAML descriptors. To update them, modify the descriptor's metadata fields (`linter_text`, `linter_url`, `linter_rules_url`, `ide` section, `examples`). Documentation regeneration is handled automatically by auto-update workflows — **never run `make megalinter-build-with-doc` in PRs** as it causes merge conflicts.

## CHANGELOG
Update `CHANGELOG.md` in the repository root (not `docs/`) when making user-facing changes.
