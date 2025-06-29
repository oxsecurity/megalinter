# All LLM Providers

This page provides a comprehensive comparison of all supported LLM providers for MegaLinter's AI-powered fix suggestions.

## Provider Comparison

| Provider | API Cost | Local/Cloud | Setup Complexity | Best For |
|----------|----------|-------------|------------------|----------|
| [OpenAI](llm-provider/llm_provider_openai.md) | $$ | Cloud | Easy | General use, high quality |
| [Anthropic](llm-provider/llm_provider_anthropic.md) | $$ | Cloud | Easy | Code analysis, safety |
| [Google GenAI](llm-provider/llm_provider_google_genai.md) | $ | Cloud | Easy | Cost-effective, multilingual |
| [Mistral AI](llm-provider/llm_provider_mistralai.md) | $ | Cloud | Easy | European alternative |
| [DeepSeek](llm-provider/llm_provider_deepseek.md) | $ | Cloud | Easy | Code-focused models |
| [Grok](llm-provider/llm_provider_grok.md) | $$ | Cloud | Easy | xAI's conversational model |
| [Ollama](llm-provider/llm_provider_ollama.md) | Free | Local | Medium | Privacy, offline use |
| [Hugging Face](llm-provider/llm_provider_huggingface.md) | Free* | Local/Cloud | Hard | Open models, customization |

*Free for local models, paid for hosted inference

## Common Configuration Options

All providers support these common configuration options:

```yaml
LLM_ADVISOR_ENABLED: true          # Enable/disable AI advisor
LLM_PROVIDER: provider_name        # Choose your provider
LLM_MODEL_NAME: model_name         # Provider-specific model
LLM_MAX_TOKENS: 1000               # Maximum response tokens
LLM_TEMPERATURE: 0.1               # Creativity (0.0-1.0)
```

## Security Recommendations

- **Environment Variables**: Always set API keys as environment variables, never in configuration files
- **Private Code**: Use local providers (Ollama, Hugging Face local) for sensitive codebases
- **Rate Limiting**: Monitor API usage to avoid unexpected costs
- **Review Suggestions**: Always review AI suggestions before applying changes

## Provider Selection Guide

### For Production Use

- **OpenAI**: Best overall quality and reliability
- **Anthropic**: Excellent for code analysis with safety focus
- **Google GenAI**: Good balance of cost and performance

### For Privacy-Sensitive Projects

- **Ollama**: Complete local processing
- **Hugging Face (local)**: Open models with local inference

### For Cost-Conscious Teams

- **Google GenAI**: Competitive pricing
- **DeepSeek**: Affordable code-focused models
- **Ollama**: Free local processing

### For Specific Use Cases

- **DeepSeek**: Code generation and analysis
- **Mistral AI**: European data residency requirements
- **Grok**: Conversational analysis with recent training data
- **Hugging Face**: Custom model fine-tuning

## Next Steps

1. **Choose a provider** based on your requirements
2. **Follow the setup guide** for your chosen provider
3. **Test with a small project** before deploying widely
4. **Monitor costs and usage** for cloud providers

Each provider page includes detailed setup instructions, model recommendations, and troubleshooting tips.
