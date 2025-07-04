# MegaLinter GitHub Copilot Instructions

## Project Overview

MegaLinter is an open-source linting tool that analyzes code quality across multiple programming languages, formats, and tooling formats. It's written primarily in Python and designed to run in CI/CD pipelines as a Docker container or GitHub Action.

## Project Structure

```
megalinter/
├── .automation/            # Build automation and scripts
│   └── build.py           # Main build script for generating files
├── megalinter/            # Core Python package
│   ├── MegaLinter.py      # Main orchestrator class
│   ├── Linter.py          # Base linter class
│   ├── linter_factory.py  # Factory for creating linter instances
│   ├── flavor_factory.py  # Factory for MegaLinter flavors
│   ├── descriptors/       # YAML descriptor files for each linter
│   ├── linters/           # Custom linter implementations
│   └── reporters/         # Report generators
├── flavors/               # Different MegaLinter variants (language-specific)
├── docs/                  # Documentation
├── mega-linter-runner/    # NPM package for local execution
├── linters/               # Generated individual linter dockerfiles
└── TEMPLATES/             # Configuration templates
```

## Core Architecture

### 1. Descriptor-Driven Design

- Each linter is defined by a YAML descriptor file in `megalinter/descriptors/`
- Descriptors contain metadata: supported file types, install instructions, CLI options
- Example: `jsx.megalinter-descriptor.yml` defines ESLint for JSX files

### 2. Main Components

**MegaLinter.py**: Main orchestrator

- Initializes configuration
- Discovers and loads linters
- Orchestrates file scanning and linting
- Manages reporters and output

**Linter.py**: Base class for all linters

- Handles common linter functionality
- File discovery and filtering
- Command execution
- Results processing

**Build System (.automation/build.py)**:

- Generates Dockerfiles from descriptors
- Creates documentation from linter metadata
- Updates flavor configurations
- Validates descriptor schemas

### 3. Linter Categories

- **Languages**: Programming languages (Python, Java, JavaScript, etc.)
- **Formats**: Data formats (JSON, YAML, XML, etc.)
- **Tooling formats**: Infrastructure files (Terraform, Docker, etc.)
- **Other**: Repository-level tools (security, copy-paste detection, etc.)

## Development Guidelines

### Adding a New Linter

1. **Create/Update Descriptor**: Add linter configuration to appropriate `.megalinter-descriptor.yml`
2. **Custom Class (if needed)**: Create custom linter class in `megalinter/linters/` if special logic required
3. **Regenerate**: Run `make megalinter-build` to update Dockerfiles, or `make megalinter-build-with-doc` to update Dockerfiles
4. **Test**: Add test cases in `megalinter/tests/test_megalinter/linters/`

### Descriptor File Structure

```yaml
descriptor_id: LANGUAGE_NAME
descriptor_type: language|format|tooling_format|other
descriptor_flavors: [list of flavors that include this linter]
file_extensions: [".ext1", ".ext2"]
linters:
  - linter_name: tool-name
    linter_url: https://tool-website.com
    cli_lint_mode: list_of_files|file|project
    install:
      npm: [packages]
      pip: [packages]
      dockerfile: [custom commands]
```

### Custom Linter Classes

When default behavior isn't sufficient, create a custom class:

```python
from megalinter import Linter

class CustomLinter(Linter):
    def build_lint_command(self, file):
        # Custom command building logic
        pass
    
    def complete_command_line(self, command, files):
        # Modify final command
        pass
```

### Build and Generation Process

The build process is automated via `.automation/build.py`:

1. **Dockerfile Generation**: Creates Docker images with required linter tools
2. **Documentation Generation**: Auto-generates linter documentation
3. **Flavor Management**: Updates flavor-specific configurations
4. **Schema Validation**: Validates all descriptor files

### Configuration System

MegaLinter uses hierarchical configuration:

1. Default values in descriptors
2. `.mega-linter.yml` file in repository
3. Environment variables
4. Command-line arguments

### Key Configuration Variables

- `ENABLE`/`DISABLE`: Control which linters run
- `APPLY_FIXES`: Enable automatic fixing
- `FILTER_REGEX_INCLUDE/EXCLUDE`: File filtering
- `{LINTER}_ARGUMENTS`: Custom CLI arguments per linter

## Testing Guidelines

### Test Structure

```
megalinter/tests/test_megalinter/
├── linters/                    # Individual linter tests
├── test_megalinter.py          # Main integration tests
└── helpers/                    # Test utilities
```

### Writing Tests

1. **Linter Tests**: Test each linter with sample files
2. **Integration Tests**: Test complete MegaLinter workflows
3. **Descriptor Validation**: Ensure YAML descriptors are valid

## Coding Standards

### Python Code Style

- Follow PEP 8
- Use type hints where possible
- Add docstrings for public methods
- Handle errors gracefully with appropriate logging

### Descriptor Guidelines

- Keep descriptors minimal and focused
- Use clear, descriptive names
- Include comprehensive install instructions
- Specify accurate file patterns

### Documentation

- Auto-generated from descriptors - don't edit generated files directly
- Update descriptor metadata to improve documentation
- Include examples and configuration tips

## Common Operations

### Adding Language Support

1. Create new descriptor file: `megalinter/descriptors/newlang.megalinter-descriptor.yml`
2. Define linters with install instructions
3. Run build process to generate files
4. Add test cases and sample files

### Updating Linter Versions

1. Update version in descriptor's install section
2. Run build to regenerate Dockerfiles
3. Test updated version compatibility

### Adding New Flavor

1. Update `megalinter/descriptors/all_flavors.json`
2. Create flavor directory in `flavors/`
3. Run build to generate flavor-specific files

## Performance Considerations

- **Parallel Processing**: Linters run in parallel when possible
- **File Filtering**: Efficient regex patterns for file discovery
- **Docker Layers**: Optimize Dockerfile for build caching
- **Flavor Selection**: Use specific flavors to reduce image size

## Integration Points

### CI/CD Systems

- GitHub Actions
- GitLab CI
- Azure Pipelines
- Jenkins
- Docker containers

### IDE Integration

- Configuration hints via JSON schemas
- Integration plugins for popular IDEs
- Local development via mega-linter-runner

## Common Patterns

### Error Handling

```python
try:
    result = self.execute_command(command)
except Exception as e:
    logging.error(f"Linter {self.name} failed: {str(e)}")
    return []
```

### File Processing

```python
def collect_files(self):
    files = []
    for ext in self.file_extensions:
        pattern = f"**/*{ext}"
        files.extend(glob.glob(pattern, recursive=True))
    return self.filter_files(files)
```

### Configuration Access

```python
from megalinter import config

# Get configuration value with default
value = config.get(self.request_id, "VARIABLE_NAME", "default_value")
```

This architecture provides a flexible, extensible framework for code quality analysis across diverse programming ecosystems.
