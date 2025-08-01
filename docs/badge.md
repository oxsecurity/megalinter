---
title: MegaLinter Badges
description: Show that your repositories are cleaned and secured with MegaLinter with a badge
---
<!-- markdownlint-disable MD013 -->
<!-- Generated by .automation/build.py, please do not update manually -->
<!-- badge-section-start -->

# Badge

You can show MegaLinter status with a badge in your repository README

[![MegaLinter](https://github.com/oxsecurity/megalinter/workflows/MegaLinter/badge.svg?branch=main)](https://github.com/oxsecurity/megalinter/actions?query=workflow%3AMegaLinter+branch%3Amain)

_If your main branch is **master** , replace **main** by **master** in URLs_

## Markdown

- Format

```markdown
[![MegaLinter](https://github.com/<OWNER>/<REPOSITORY>/workflows/MegaLinter/badge.svg?branch=main)](https://github.com/<OWNER>/<REPOSITORY>/actions?query=workflow%3AMegaLinter+branch%3Amain)
```

- Example

```markdown
[![MegaLinter](https://github.com/nvuillam/npm-groovy-lint/workflows/MegaLinter/badge.svg?branch=main)](https://github.com/nvuillam/npm-groovy-lint/actions?query=workflow%3AMegaLinter+branch%3Amain)
```

## reStructuredText

- Format

```markdown
.. |MegaLinter yes| image:: https://github.com/<OWNER>/<REPOSITORY>/workflows/MegaLinter/badge.svg?branch=main
   :target: https://github.com/<OWNER>/<REPOSITORY>/actions?query=workflow%3AMegaLinter+branch%3Amain
```

- Example

```markdown
.. |MegaLinter yes| image:: https://github.com/nvuillam/npm-groovy-lint/workflows/MegaLinter/badge.svg?branch=main
   :target: https://github.com/nvuillam/npm-groovy-lint/actions?query=workflow%3AMegaLinter+branch%3Amain
```

_Note:_ IF you did not use `MegaLinter` as GitHub Action name, please read [GitHub Actions Badges documentation](https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/monitoring-workflows/adding-a-workflow-status-badge){target=_blank}

<!-- badge-section-end -->
