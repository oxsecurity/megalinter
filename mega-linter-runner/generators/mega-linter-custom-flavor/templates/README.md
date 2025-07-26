# MegaLinter Custom Flavor

<%= CUSTOM_FLAVOR_LABEL %>

## Embedded linters

<%= CUSTOM_FLAVOR_LINTERS %>

## Generated docker image

<%= DOCKER_IMAGE_VERSION %>

## How to generate the flavor

Create a GitHub release on your repo, it will generate and publish your custom flavor using the MegaLinter custom Flavor Builder matching the tag name of your release (example: `9.0.0`)

You can also generate a custom flavor using MegaLinter Custom Flavor by pushing on any branch or manually run the workflow `megalinter-custom-flavor-builder.yml`.