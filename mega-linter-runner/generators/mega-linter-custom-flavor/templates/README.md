# MegaLinter Custom Flavor: <%= CUSTOM_FLAVOR_LABEL %>

This custom MegaLinter aims to have an optimized Docker image size.

It is built from official MegaLinter images, but maintained on <%= CUSTOM_FLAVOR_REPO %> by <%= CUSTOM_FLAVOR_AUTHOR %>

## Embedded linters

<%= CUSTOM_FLAVOR_LINTERS_WITH_LINKS %>

## How to generate the flavor

Create a GitHub release on your repo, it will generate and publish your custom flavor using the MegaLinter custom Flavor Builder matching the tag name of your release (example: `9.0.0`)

You can also generate a custom flavor using MegaLinter Custom Flavor by pushing on any branch or manually run the workflow `megalinter-custom-flavor-builder.yml`.

See [full Custom Flavors documentation](https://megalinter.io/beta/custom-flavors/).

## How to use the custom flavor

Follow [MegaLinter installation guide](https://megalinter.io/latest/install-assisted/), and replace related elements in the workflow.

- GitHub Action: On MegaLinter step in .github/workflows/mega-linter.yml, define `uses: <%= CUSTOM_FLAVOR_GITHUB_ACTION %>@main`
- Docker image: Replace official MegaLinter image by `<%= DOCKER_IMAGE_VERSION %>`

[![MegaLinter is graciously provided by OX Security](https://raw.githubusercontent.com/oxsecurity/megalinter/main/docs/assets/images/ox-banner.png)](https://www.ox.security/?ref=megalinter)
