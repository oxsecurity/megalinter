# LLM Provider Architecture

This directory contains the modular LLM provider system for MegaLinter's AI-powered fix suggestions.

## Architecture

### Core Components

- **`llm_provider.py`**: Abstract base class defining the provider interface
- **`llm_provider_factory.py`**: Factory pattern for creating and managing providers
- **`llm_provider_*.py`**: Individual provider implementations

### Supported Providers

| Provider     | File                          | LLM Models                      | API Required |
|--------------|-------------------------------|---------------------------------|--------------|
| OpenAI       | `llm_provider_openai.py`      | GPT-3.5, GPT-4, GPT-4o          | Yes          |
| Anthropic    | `llm_provider_anthropic.py`   | Claude 3 (Haiku, Sonnet, Opus)  | Yes          |
| Google       | `llm_provider_google.py`      | Gemini Pro, Gemini Flash        | Yes          |
| Mistral AI   | `llm_provider_mistral.py`     | Mistral Small, Medium, Large    | Yes          |
| DeepSeek     | `llm_provider_deepseek.py`    | DeepSeek Chat, DeepSeek Coder   | Yes          |
| Grok         | `llm_provider_grok.py`        | Grok Beta (xAI)                 | Yes          |
| Hugging Face | `llm_provider_huggingface.py` | Any HF transformer model        | Optional     |
| Ollama       | `llm_provider_ollama.py`      | Llama, CodeLlama, Mistral, etc. | No           |

## Adding a New Provider

1. **Create Provider Class**:

   ```python
   # llm_provider_newprovider.py
   from .llm_provider import LLMProvider

   class NewProvider(LLMProvider):
       def get_default_model(self) -> str:
           return "default-model-name"

       def initialize(self) -> bool:
           # Initialize your LLM here
           # Return True if successful, False otherwise
   ```

2. **Register in Factory**:

   ```python
   # Add to llm_provider_factory.py
   SUPPORTED_PROVIDERS = {
       "newprovider": NewProvider,
       # ... existing providers
   }
   ```

3. **Update Imports**:

   ```python
   # Add to __init__.py
   from .llm_provider_newprovider import NewProvider
   ```

## Provider Interface

Each provider must implement:

- `get_default_model() -> str`: Return the default model name
- `initialize() -> bool`: Initialize the provider (return success status)
- `load_config(request_id) -> Dict[str, Any]`: Load provider-specific configuration

Base class provides:

- `is_available() -> bool`: Check if provider is ready
- `invoke(prompt, system_prompt=None) -> str`: Generate response
- `get_config_value(key, default=None)`: Access configuration with centralized defaults
- `get_default_config_value(key)`: Access centralized default values
- `requires_api_key() -> bool`: Check if API key needed

## Centralized Default Configuration

The base class defines common default values that apply to all providers:

```python
DEFAULT_CONFIG = {
    "temperature": 0.1,
    "max_tokens": 1000,
    "timeout": 30,
    "retry_attempts": 3
}
```

Providers automatically inherit these defaults through the `get_config_value()` method, ensuring consistency across all implementations.

## Configuration

Providers receive configuration through the constructor and use centralized defaults:

```python
config = {
    "model_name": "model-name",
    "temperature": 0.1,  # Uses centralized default if not specified
    "max_tokens": 1000,  # Uses centralized default if not specified
    "api_key": "your-api-key",
    # Provider-specific settings...
}
provider = ProviderClass(config)
```

To use centralized defaults in your `load_config()` method:

```python
def load_config(self, request_id: str = None) -> Dict[str, str | float]:
    return {
        "api_key": config.get(request_id, "PROVIDER_API_KEY", ""),
        "model_name": config.get(request_id, "LLM_MODEL_NAME", ""),
        "temperature": float(config.get(request_id, "LLM_TEMPERATURE", str(self.get_default_config_value("temperature")))),
        "max_tokens": int(config.get(request_id, "LLM_MAX_TOKENS", str(self.get_default_config_value("max_tokens"))))
    }
```

## Error Handling

- Providers should handle initialization errors gracefully
- Failed providers return `False` from `initialize()`
- Runtime errors are logged and re-raised with context

## Testing

Test your provider:

1. Create test configuration
2. Initialize provider
3. Verify `is_available()` returns `True`
4. Test `invoke()` with sample prompt
5. Handle edge cases (missing API keys, network errors)

## Usage

```python
from megalinter.llm_provider.llm_provider_factory import LLMProviderFactory

# Create provider
config = {"api_key": "...", "model_name": "..."}
provider = LLMProviderFactory.create_provider("openai", config)

if provider and provider.is_available():
    response = provider.invoke("Your prompt here", "System prompt")
    print(response)
```
