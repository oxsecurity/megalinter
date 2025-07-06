# Ollama Provider

Ollama enables running large language models locally, providing complete privacy and no API costs.

## Setup

### 1. Install Ollama

**macOS/Linux:**

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**

Download installer from [ollama.ai](https://ollama.ai/)

### 2. Pull a Model

```bash
ollama pull codellama:7b
```

### 3. Configure MegaLinter

```yaml
LLM_ADVISOR_ENABLED: true
LLM_PROVIDER: ollama
LLM_MODEL_NAME: codellama:7b
LLM_MAX_TOKENS: 1000
LLM_TEMPERATURE: 0.1
```

## Official Model List

For the most up-to-date list of models available for Ollama, see the official Ollama model library:

- [Ollama Model Library](https://ollama.com/library)

## Configuration Options

### Basic Configuration

```yaml
LLM_PROVIDER: ollama
LLM_MODEL_NAME: codellama:7b        # Any installed Ollama model
```

### Advanced Configuration

```yaml
# Custom Ollama server
OLLAMA_BASE_URL: http://localhost:11434

# For remote Ollama servers
OLLAMA_BASE_URL: http://your-server:11434
```

## Troubleshooting

### Common Issues

1. **"Connection refused"**
   - Ensure Ollama is running: `ollama serve`
   - Check the correct port (default: 11434)
   - Verify firewall settings

2. **"Model not found"**
   - Pull the model first: `ollama pull model-name`
   - List available models: `ollama list`
   - Use exact model name with tag

3. **"Out of memory"**
   - Use smaller models (7B instead of 13B)
   - Close other applications
   - Consider using quantized models

4. **Slow responses**
   - Use smaller models for faster inference
   - Ensure sufficient RAM
   - Consider GPU acceleration if available
