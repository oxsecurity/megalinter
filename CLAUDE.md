# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MegaLinter is an open-source CI/CD linting tool that analyzes code quality across 69+ languages, 23+ formats, and 21+ tooling formats. It runs as a Docker container or GitHub Action. Written primarily in Python with a Node.js runner component.

## Development Setup

Prerequisites: make, Python 3.12+, uv, Node.js, Docker.

```bash
make bootstrap          # Create venv, install dependencies (uses uv if available)
make bootstrap          # Also runs: python-bootstrap + python-bootstrap-dev + nodejs-bootstrap
```

Always activate the venv before running Python scripts manually:
- Linux/macOS: `source .venv/bin/activate`
- Windows: `source .venv/Scripts/activate`

## Key Commands

```bash
# Build (regenerate Dockerfiles, docs, etc. from descriptors)
make megalinter-build           # Regenerate Dockerfiles from YAML descriptors
# Never run make megalinter-build-with-doc - docs are handled by auto-update workflows (avoids PR conflicts)

# Run MegaLinter locally
npx mega-linter-runner --flavor python --release beta

# Tests - run inside Docker containers (linters not installed locally)
# See "Testing" section below

# Documentation
hatch run docs:serve            # Local docs server at http://127.0.0.1:8000

# Dependencies
uv lock                         # After modifying pyproject.toml
uv pip install -e .             # Install in editable mode
```

## Architecture

### Descriptor-Driven Design

The core pattern: each linter is defined in a YAML descriptor file (`megalinter/descriptors/<lang>.megalinter-descriptor.yml`). The build system (`.automation/build.py`) reads these descriptors and generates:
- Dockerfiles (per-linter in `linters/`, per-flavor in `flavors/`)
- Documentation pages (in `docs/`)
- Test class skeletons
- JSON configuration schemas

**Never edit generated files directly** - modify the descriptor YAML or `.automation/build.py` instead.

### Core Components

- **`megalinter/MegaLinter.py`** - Main orchestrator: loads config, discovers linters, runs them in parallel, manages reporters
- **`megalinter/Linter.py`** - Base class for all linters: file discovery, command execution, result processing
- **`megalinter/linter_factory.py`** - Builds linter instances from YAML descriptors; uses `build_linter()` and `build_descriptor_linters()`
- **`megalinter/flavor_factory.py`** - Manages flavor variants (language-specific Docker images)
- **`megalinter/config.py`** - Hierarchical config: descriptor defaults -> `.mega-linter.yml` -> env vars -> CLI args. Access via `config.get(request_id, "VAR_NAME", default)`
- **`megalinter/linters/`** - Custom linter subclasses when default `Linter.py` behavior isn't sufficient
- **`megalinter/reporters/`** - Output formatters (GitHub comments, GitLab, SARIF, etc.)
- **`megalinter/llm_advisor.py`** - AI-powered fix suggestions via LangChain (multi-provider)

### Entrypoint

`megalinter/run.py` creates a `Megalinter` instance and calls `.run()`. In Docker, `entrypoint.sh` invokes this.

### Server Mode

`server/` contains a FastAPI-based server (`server.py`) with Redis-backed worker (`server_worker.py`) for running MegaLinter as a service.

### Node.js Runner

`mega-linter-runner/` is an npm package that wraps Docker execution for local use (`npx mega-linter-runner`).

## Testing

Tests live in `megalinter/tests/test_megalinter/`. Each linter has a test file in `linters/` (e.g., `python_ruff_test.py`).

Linter tests extend `LinterTestRoot` which provides standard `test_success`, `test_failure`, `test_get_linter_version`, and `test_get_linter_help` methods. Test fixtures are in `.automation/test/`.

**Linter tests must run inside Docker containers** since linters aren't installed locally:

```bash
# Build and test a specific linter
LINTER="python_ruff"
docker buildx build --platform linux/amd64 --file linters/$LINTER/Dockerfile --tag $LINTER .
docker run --rm \
  --env TEST_CASE_RUN=true \
  --env OUTPUT_DETAIL=detailed \
  --env TEST_KEYWORDS="${LINTER}_test" \
  --env MEGALINTER_VOLUME_ROOT="." \
  --volume "$(pwd):/tmp/lint" \
  $LINTER
```

In CI, filter tests via commit message body: `TEST_KEYWORDS=python_ruff_test`. Use `quick build` in commit message body to only copy Python files (faster, ~15min vs ~45min).

## Adding a New Linter

1. Add/update the YAML descriptor in `megalinter/descriptors/<lang>.megalinter-descriptor.yml`
2. If custom logic needed, create a class in `megalinter/linters/` extending `Linter`
3. Add test fixtures in `.automation/test/` (one success file, one failure file)
4. Run `make megalinter-build` to regenerate Dockerfiles, tests, docs
5. Update `CHANGELOG.md`

## Coding Conventions

- Python: PEP 8, use type hints, do NOT use docstrings for classes/methods
- Do not test if imports work - assume they are always available
- Place imports at the top of files
- Use `megalinter.config.get(request_id, "VAR", default)` for config access, never `os.environ` directly
- Use `logging` module for output, never `print()`
- Documentation files must be mkdocs-material compliant: always have a blank line after headers and before bulleted lists
- Auto-generated docs come from descriptors - update descriptor metadata to improve docs

## Claude Code Agents

Custom agents in `.claude/agents/` for delegating specialized tasks:

- **descriptor-expert** - Creates, edits, and validates YAML descriptor files
- **test-debugger** - Diagnoses and fixes failing linter tests
- **build-runner** - Runs and troubleshoots the build system
- **code-reviewer** - Reviews Python code for MegaLinter conventions

## Claude Code Skills

Skills in `.claude/skills/` invocable by name (e.g. `/add-linter`):

- `/add-linter [name]` - Guided workflow for adding a new linter
- `/update-linter-version [linter] [version]` - Update a linter's pinned version
- `/review-descriptor [name]` - Audit a descriptor YAML for completeness
- `/fix-linter-test [name]` - Debug a failing linter test
- `/add-reporter [name]` - Add a new output reporter
- `/add-flavor [name]` - Add a new Docker flavor
- `/build` - Run the build system
- `/diagnose-config` - Debug `.mega-linter.yml` configuration issues
- `/fix-security-issue [CVE or description]` - Handle CVE/vulnerability reports from trivy, osv-scanner, etc.

## Rules

Context-aware rules in `.claude/rules/` are automatically loaded based on which files are being edited:

- `python-style.md` - Python conventions (no docstrings, config access patterns, linter subclass guidelines)
- `descriptors.md` - YAML descriptor schema, naming, version pinning, test fixtures
- `generated-files.md` - Prevents editing auto-generated Dockerfiles, docs, test classes
- `documentation.md` - mkdocs-material markdown formatting rules
- `testing.md` - Test structure, fixtures, Docker-based test execution
