---
title: Generate your own Megalinter custom flavors
description: Optimize your Megalinter performances with custom flavors !
---
<!-- markdownlint-disable MD013 -->

# Custom MegaLinter Flavors

You can easily generate your own MegaLinter custom flavor using the `mega-linter-runner` generator.

## Create a custom flavor

### Pre-requisites

- Make sure you have [Node.js](https://nodejs.org/) installed.

### Create a new repository

- Create a new GitHub public repository whose name starts with `megalinter-custom-flavor` (example: `megalinter-custom-flavor-npm-groovy-lint`), with default README checked.

![](assets/images/custom-flavor-new-repo.png)

### Clone your new repository locally

Clone your new repository to your local machine.
You can work directly on **main** branch, or create a sub-branch if you prefer.

### Run the custom flavor setup command

Run the following command in your repository folder:

```bash
npx mega-linter-runner@beta --custom-flavor-setup
```

You can also send the list of linters as parameters, available from the logs of any official MegaLinter flavor (if you don't see it, make sure `FLAVOR_SUGGESTIONS: true` is defined in your `.mega-linter.yml` config file).

![](assets/images/custom-flavor-command.png)

```bash
npx mega-linter-runner@beta --custom-flavor-setup --custom-flavor-linters "PYTHON_BANDIT,PYTHON_BLACK,PYTHON_RUFF,REPOSITORY_TRIVY"
```

### Follow the interactive prompts

Select your custom flavor label and the linters you want to include.

![](assets/images/custom-flavor-linter-select.png)

### Generated files

The generator will create all necessary configuration files, GitHub Actions workflow, and documentation in your repository.

![](assets/images/custom-flavor-generated-files.png)

### Commit and push your changes

Commit and push the generated files to GitHub.

![](assets/images/custom-flavor-commit-push.png)

### Build and publish your custom flavor

Create a GitHub release or push to any branch to trigger the GitHub action workflow that builds and publish your custom MegaLinter Docker image.

The generated workflow will build and publish your custom flavor to GitHub Container Registry (ghcr.io) and optionally Docker Hub if you define variables and secrets:
  - `DOCKERHUB_REPO` (variable)
  - `DOCKERHUB_USERNAME` (secret)
  - `DOCKERHUB_PASSWORD` (secret)

![](assets/images/custom-flavor-release-1.png)

![](assets/images/custom-flavor-release-2.png)

![](assets/images/custom-flavor-build-job.png)

## Use a Custom Flavor

Follow [MegaLinter installation guide](https://megalinter.io/latest/install-assisted/), and replace related elements in the workflow.

![](assets/images/custom-flavor-run.png)

### GitHub Action

On MegaLinter step in `.github/workflows/mega-linter.yml`, replace the official GitHub Action with your custom flavor repo action.

Example:

```yaml
      # Mega-Linter
      - name: Mega-Linter
        id: ml
        uses: nvuillam/megalinter-custom-flavor-npm-groovy-lint@main
        env:
          # All available variables are described in documentation
          # https://megalinter.io/#configuration
          VALIDATE_ALL_CODEBASE: true # ${{ github.event_name == 'push' && github.ref == 'refs/heads/master' }} # Validates all source when push on master, else just the git diff with master. Override with true if you always want to lint all sources
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          # ADD YOUR CUSTOM ENV VARIABLES HERE OR DEFINE THEM IN A FILE .mega-linter.yml AT THE ROOT OF YOUR REPOSITORY
          # DISABLE: COPYPASTE,SPELL # Uncomment to disable copy-paste and spell checks
```

### Docker image

Replace official MegaLinter image wih your custom flavor docker image

Example with gitlab-ci.yml:

```yaml
mega-linter:
  stage: test

  # You can override MegaLinter flavor used to have faster performances
  # More info at https://megalinter.io/latest/flavors/
  image: ghcr.io/nvuillam/megalinter-custom-flavor-npm-groovy-lint/megalinter-custom-flavor:latest
```

## Update your custom flavor

If you add/remove linters in your `mega-linter-flavor.yml`:

- Run `npx mega-linter-runner@beta --custom-flavor-setup` to apply upgrades to other files
- Delete your release and associated tag, then recreate the release with the same tag name.

## Upgrade your custom flavor

When a new MegaLinter official release is published, you can create a new version of your custom flavor.

Just create a GitHub Release with the same version (tag) than the MegaLinter release you want to use to generate your upgraded flavor.








