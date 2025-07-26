---
title: Generate your own Megalinter custom flavors
description: Optimize your Megalinter performances with custom flavors !
---
<!-- markdownlint-disable MD013 -->

# Custom MegaLinter Flavors

You can easily generate your own MegaLinter custom flavor using the `mega-linter-runner` generator.

## Prerequisites

- Create a new GitHub public repository whose name starts with `megalinter-custom-flavor` (e.g., `megalinter-custom-flavor-python-light`), with default README.
- Make sure you have [Node.js](https://nodejs.org/) installed.

### Clone your new repository locally

Clone your new repository to your local machine.
You can work directly on **main** branch, or create a sub-branch if you prefer.

### Run the custom flavor setup command

Run the following command in your repository folder:

```bash
npx mega-linter-runner --custom-flavor-setup
```

You can also send the list of linters as parameters

```bash
npx mega-linter-runner --custom-flavor-setup --custom-flavor-linters "PYTHON_BANDIT,PYTHON_BLACK,PYTHON_RUFF,REPOSITORY_TRIVY"
```

### Follow the interactive prompts

Select your custom flavor label and the linters you want to include.

### Generated files

The generator will create all necessary configuration files, GitHub Actions workflow, and documentation in your repository.

### Commit and push your changes

Commit and push your changes to GitHub.

### Build and publish your custom flavor

Create a GitHub release or push to any branch to trigger the GitHub action workflow that builds and publish your custom MegaLinter Docker image.

## Notes

- The generated workflow will build and publish your custom flavor to GitHub Container Registry (ghcr.io) and optionally Docker Hub if you define variables and secrets:
  - `DOCKERHUB_REPO` (variable)
  - `DOCKERHUB_USERNAME` (secret)
  - `DOCKERHUB_PASSWORD` (secret)
- You can customize the generated files as needed before publishing.

