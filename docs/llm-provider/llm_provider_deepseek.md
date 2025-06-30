# DeepSeek Provider

DeepSeek offers specialized code-focused models at competitive prices, optimized for programming tasks.

## Supported Models

| Model            | Context Length | Cost | Best For            |
|------------------|----------------|------|---------------------|
| `deepseek-chat`  | 32K tokens     | $    | General purpose     |
| `deepseek-coder` | 16K tokens     | $    | Code-specific tasks |

## Setup

1. **Get API Key**: Sign up at [DeepSeek Platform](https://platform.deepseek.com/)
2. **Set Environment Variable**:
   ```bash
   export DEEPSEEK_API_KEY=your-deepseek-api-key
   ```
3. **Configure MegaLinter**:
   ```yaml
   LLM_ADVISOR_ENABLED: true
   LLM_PROVIDER: deepseek
   LLM_MODEL_NAME: deepseek-chat
   LLM_MAX_TOKENS: 1000
   LLM_TEMPERATURE: 0.1
   ```

## Configuration Options

### Basic Configuration

```yaml
LLM_PROVIDER: deepseek
LLM_MODEL_NAME: deepseek-chat       # or deepseek-coder
```

### Advanced Configuration

```yaml
# Custom API endpoint (if needed)
DEEPSEEK_BASE_URL: https://api.deepseek.com/v1
```

## Model Recommendations

- **General Use**: `deepseek-chat` - Good for all types of code analysis
- **Code-Specific**: `deepseek-coder` - Optimized for programming tasks

## Advantages

- **Code-Focused**: Models trained specifically for programming
- **Cost-Effective**: Competitive pricing for quality
- **Good Performance**: Strong code understanding capabilities
- **Fast Responses**: Quick analysis and suggestions

## Cost Considerations

DeepSeek offers competitive pricing:
- Pay-per-token model
- Generally more affordable than major providers
- Monitor usage on your dashboard

## Troubleshooting

### Common Issues

1. **"Invalid API key"**
   - Verify your API key is correct
   - Check account status and credits
   - Ensure API access is enabled

2. **"Rate limit exceeded"**
   - Check your plan's rate limits
   - Implement rate limiting in your requests
   - Consider upgrading your plan

3. **"Model not available"**
   - Verify model name is correct
   - Check if model is available in your region
   - Some models may require special access

## Best Practices

- Use `deepseek-chat` for general code analysis
- Use `deepseek-coder` for specialized programming tasks
- Monitor token usage to control costs
- Set appropriate temperature (0.1-0.3) for consistent technical advice
