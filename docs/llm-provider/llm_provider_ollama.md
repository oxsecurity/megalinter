# Ollama Provider

Ollama enables running large language models locally, providing complete privacy and no API costs.

## Supported Models

Popular models available through Ollama:

| Model | Size | Best For |
|-------|------|----------|
| `llama2` | 7B-70B | General purpose |
| `codellama` | 7B-34B | Code-specific tasks |
| `mistral` | 7B | Fast, efficient |
| `dolphin-mixtral` | 8x7B | Code and reasoning |
| `deepseek-coder` | 6.7B-33B | Code generation |

See [Ollama Model Library](https://ollama.ai/library) for complete list.

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

## Model Recommendations

- **Code Analysis**: `codellama:7b` or `deepseek-coder:6.7b`
- **General Use**: `llama2:7b` or `mistral:7b`
- **Better Quality**: `codellama:13b` or `mixtral:8x7b` (if you have enough RAM)
- **Fast Responses**: `codellama:7b` or `mistral:7b`

## Advantages

- **Complete Privacy**: Code never leaves your machine
- **No API Costs**: Free to use once installed
- **Offline**: Works without internet connection
- **Customizable**: Can fine-tune models for specific needs
- **No Rate Limits**: Limited only by your hardware

## Hardware Requirements

| Model Size | RAM Required | Speed |
|------------|-------------|-------|
| 7B models | 8GB+ | Fast |
| 13B models | 16GB+ | Medium |
| 33B+ models | 32GB+ | Slow |

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

### Debug Commands

```bash
# Check Ollama status
ollama list

# Test model directly
ollama run codellama:7b "Explain this error: undefined variable"

# View logs
ollama logs
```

## Best Practices

- Start with `codellama:7b` for code analysis
- Ensure you have enough RAM for your chosen model
- Use SSD storage for better model loading times
- Consider running Ollama as a service for persistent availability
- Monitor system resources during use
- Pull models ahead of time for offline use

## Model Management

```bash
# List installed models
ollama list

# Pull a new model
ollama pull mistral:7b

# Remove a model
ollama rm model-name

# Update a model
ollama pull model-name
```
