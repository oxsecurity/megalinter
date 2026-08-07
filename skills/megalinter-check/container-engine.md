# Container engine setup (podman / docker)

Load this guide only when a local MegaLinter run is needed and no container engine is available. **Always ask the user before installing or starting anything.** Prefer **podman** when installing from scratch: it is free of charge including in enterprise contexts, while Docker Desktop requires a paid subscription in larger companies.

## Detect what is available

Always bound the probes: with a stopped backend (e.g. Docker Desktop's Windows service `com.docker.service`), the CLI can hang indefinitely instead of failing fast.

```bash
timeout 10 podman info --format '{{.Version.Version}}'   # podman installed AND responding?
timeout 10 docker info --format '{{.ServerVersion}}'     # docker installed AND responding?
```

- Command not found → the engine is not installed.
- Command found but the call fails → the engine is installed but its daemon/VM is not started.
- Command times out (exit 124) → installed but the backend is stopped or wedged - treat as not running, and never retry it without a bound.
- If **either** engine responds, use it — pass `--container-engine podman` to `mega-linter-runner` when using podman.

## Start an already-installed engine

| OS      | podman                                                             | docker                                                                                                                                                                 |
|:--------|:-------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Windows | `podman machine start` (create it once with `podman machine init`) | Start Docker Desktop: `Start-Process 'C:\Program Files\Docker\Docker\Docker Desktop.exe'`, then poll `timeout 10 docker info` until it responds (give up after ~2 min) |
| macOS   | `podman machine start` (create it once with `podman machine init`) | `open -a Docker`, then poll `timeout 10 docker info` until it responds (give up after ~2 min)                                                                          |
| Linux   | Nothing to start (daemonless) — rootless works out of the box      | `sudo systemctl start docker` (enable at boot: `sudo systemctl enable docker`)                                                                                         |

## Install an engine (ask the user first, prefer podman)

### podman

| OS            | Install                                                                           |
|:--------------|:----------------------------------------------------------------------------------|
| Windows       | `winget install RedHat.Podman` then `podman machine init && podman machine start` |
| macOS         | `brew install podman` then `podman machine init && podman machine start`          |
| Debian/Ubuntu | `sudo apt-get install -y podman`                                                  |
| Fedora/RHEL   | `sudo dnf install -y podman`                                                      |
| Other         | See <https://podman.io/docs/installation>                                         |

### docker (if the user prefers it)

| OS      | Install                                                                                                                               |
|:--------|:--------------------------------------------------------------------------------------------------------------------------------------|
| Windows | `winget install Docker.DockerDesktop`, start Docker Desktop, accept its terms                                                         |
| macOS   | `brew install --cask docker`, then `open -a Docker`                                                                                   |
| Linux   | `curl -fsSL https://get.docker.com \| sudo sh`, then `sudo systemctl start docker` (add the user to the `docker` group to avoid sudo) |

## After setup

Verify with the detection commands above, then re-run the MegaLinter command, adding `--container-engine podman` if podman was chosen. If installation is refused or fails, fall back to CI watch mode (`megalinter-check` watch mode) instead of local runs.
