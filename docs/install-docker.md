---
title: Run MegaLinter as a Docker image
description: Manual instructions to run MegaLinter as a docker image
---
<!-- markdownlint-disable MD013 -->
<!-- @generated by .automation/build.py, please don't update manually -->
<!-- install-docker-section-start -->

# Docker container

You can also run megalinter with its Docker container, just execute this command:

`docker run --rm -v /var/run/docker.sock:/var/run/docker.sock:rw -v $(pwd):/tmp/lint:rw oxsecurity/megalinter:v8`

**No extra arguments are needed,** however, megalinter will lint all of the files inside the `/tmp/lint` folder, so it may be needed to configure your tool of choice to use the `/tmp/lint` folder as workspace.
This can also be changed:

_Example:_

`docker run --rm -v /var/run/docker.sock:/var/run/docker.sock:rw -v $(pwd):/example/folder:rw oxsecurity/megalinter:v8`


<!-- install-docker-section-end -->
