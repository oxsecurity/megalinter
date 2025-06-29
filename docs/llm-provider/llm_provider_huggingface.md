# Hugging Face Provider

Hugging Face provides access to thousands of open-source models that can run locally or via their inference API.

## Supported Models

Popular models for code analysis:

| Model                       | Size | Type    | Best For                |
|-----------------------------|------|---------|-------------------------|
| `microsoft/DialoGPT-medium` | 345M | General | Conversational analysis |
| `Salesforce/codet5-base`    | 220M | Code    | Code understanding      |
| `microsoft/codebert-base`   | 125M | Code    | Code representation     |
| `bigcode/starcoder`         | 15B  | Code    | Advanced code tasks     |

## Setup

### Prerequisites

Hugging Face models require additional dependencies:

```bash
# Install as PRE_COMMAND in .mega-linter.yml
pip install langchain-huggingface transformers torch
```

Or use the optional dependency group:
```bash
pip install megalinter[huggingface]
```

### Configuration

1. **Optional: Get API Token** (for private models or hosted inference):
   - Go to [Hugging Face Settings](https://huggingface.co/settings/tokens)
   - Create a new token
2. **Set Environment Variable** (optional):
   ```bash
   export HUGGINGFACE_API_TOKEN=hf_your-token
   ```
3. **Configure MegaLinter**:
   ```yaml
   LLM_ADVISOR_ENABLED: true
   LLM_PROVIDER: huggingface
   LLM_MODEL_NAME: microsoft/DialoGPT-medium
   LLM_MAX_TOKENS: 1000
   LLM_TEMPERATURE: 0.1
   ```

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

## Model Recommendations

### For Local Execution

- **Small/Fast**: `microsoft/DialoGPT-medium` (345M parameters)
- **Code-Focused**: `Salesforce/codet5-base` (220M parameters)
- **Balanced**: `microsoft/codebert-base` (125M parameters)

### For API Execution

- **Advanced**: `bigcode/starcoder` (15B parameters)
- **Efficient**: `codeparrot/codeparrot-small` (110M parameters)

## Advantages

- **Open Source**: Access to thousands of free models
- **Local Execution**: Complete privacy and control
- **Customizable**: Fine-tune models for specific needs
- **No API Costs**: Free for local models
- **Variety**: Specialized models for different tasks

## Hardware Requirements

| Model Size | RAM Required | GPU Memory | Speed     |
|------------|--------------|------------|-----------|
| < 500M     | 4GB+         | Optional   | Fast      |
| 500M-2B    | 8GB+         | 4GB+       | Medium    |
| 2B-7B      | 16GB+        | 8GB+       | Slow      |
| 7B+        | 32GB+        | 16GB+      | Very Slow |

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

## Model Selection Guide

### By Use Case

- **General Chat**: `microsoft/DialoGPT-*`
- **Code Generation**: `bigcode/starcoder`, `Salesforce/codet5-*`
- **Code Understanding**: `microsoft/codebert-*`
- **Fast Inference**: Models under 500M parameters

### By Hardware

- **CPU Only**: Models under 1B parameters
- **4GB GPU**: Models up to 2B parameters
- **8GB+ GPU**: Models up to 7B parameters

## Best Practices

- Start with smaller models for testing
- Use GPU acceleration when available
- Cache models locally to avoid re-downloading
- Monitor system resources during inference
- Consider using the Hugging Face Inference API for large models
- Fine-tune models on your specific codebase for better results

## Local vs API Execution

### Local Execution

- **Pros**: Privacy, no costs, offline capability
- **Cons**: Hardware requirements, setup complexity

### API Execution

- **Pros**: No hardware requirements, access to large models
- **Cons**: API costs, internet dependency, data privacy concerns
