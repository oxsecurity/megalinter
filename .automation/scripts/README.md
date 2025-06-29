# Automation Scripts

This directory contains various automation and testing scripts for MegaLinter development.

## Directories

### `llm/`
Testing scripts for LLM (Large Language Model) integrations:
- **OpenAI Connector Tests** - Scripts to test OpenAI integration for the LLM Advisor feature
- See `llm/README_OPENAI_TEST.md` for detailed instructions

## Usage

Scripts should be run from the MegaLinter root directory to ensure proper import paths and configuration loading.

Example:
```bash
# From the root directory
python .automation/scripts/llm/test_openai_simple.py
```
