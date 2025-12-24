<div align="center">
  <img src="https://huggingface.co/datasets/huggingface/brand-assets/resolve/main/hf-logo.png" alt="Hugging Face Logo" style="max-width: 100px; margin-bottom: 1em;" />
</div>

# Hugging Face Provider

Hugging Face provides access to thousands of open-source models that can run locally or via their inference API.

## Setup

### Prerequisites

Hugging Face models require additional dependencies:

```bash
# Install as PRE_COMMAND in .mega-linter.yml
pip install langchain-huggingface transformers torch
```

### Configuration

1. **Optional: Get API Token** (for private models or hosted inference):

   - Go to [Hugging Face Settings](https://huggingface.co/settings/tokens)
   - Create a new token

2. **Set Environment Variable** (optional):

Set **HUGGINGFACE_API_TOKEN=hf_your-token** in your CI/CD secret variables.

> Make sure the secret variable is sent to MegaLinter from your CI/CD workflow. Example in GitHub Action: `HUGGINGFACE_API_TOKEN: ${{ secrets.HUGGINGFACE_API_TOKEN }}`

1. **Configure MegaLinter**:

```yaml
LLM_ADVISOR_ENABLED: true
LLM_PROVIDER: huggingface
LLM_MODEL_NAME: microsoft/DialoGPT-medium
LLM_MAX_TOKENS: 1000
LLM_TEMPERATURE: 0.1
```

## Official Model List

For the most up-to-date list of Hugging Face models and their capabilities, see the official Hugging Face model hub:

- [Hugging Face Model Hub](https://huggingface.co/models?pipeline_tag=text-generation)

## Configuration Options

### Basic Configuration

```yaml
LLM_PROVIDER: huggingface
LLM_MODEL_NAME: microsoft/DialoGPT-medium
```

### Advanced Configuration

```yaml
# Model task type
HUGGINGFACE_TASK: text-generation

# Device settings
HUGGINGFACE_DEVICE: -1              # -1 for CPU, 0+ for GPU

# For hosted inference API
HUGGINGFACE_USE_API: true
```

## Troubleshooting

### Common Issues

1. **"Model not found"**

   - Verify model name and repository exists
   - Check if model requires authentication
   - Ensure model supports the specified task

2. **"Out of memory"**

   - Use smaller models
   - Enable CPU-only mode: `HUGGINGFACE_DEVICE: -1`
   - Close other applications

3. **"Import errors"**

   - Install required dependencies:
     ```bash
     pip install langchain-huggingface transformers torch
     ```

4. **"Slow inference"**

   - Use GPU if available: `HUGGINGFACE_DEVICE: 0`
   - Consider smaller models
   - Use hosted API for large models

### Debug Mode

```yaml
LOG_LEVEL: DEBUG
HUGGINGFACE_VERBOSE: true
```
