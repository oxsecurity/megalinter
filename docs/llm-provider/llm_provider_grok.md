# Grok Provider

Grok is xAI's conversational AI model, designed for real-time information and engaging interactions. It uses the OpenAI-compatible API format.

## Supported Models

| Model       | Context Length | Cost | Best For                     |
|-------------|----------------|------|------------------------------|
| `grok-beta` | 128K tokens    | $$   | Conversational code analysis |

## Setup

1. **Get API Key**: Sign up at [xAI Console](https://console.x.ai/)
2. **Set Environment Variable**:
   ```bash
   export GROK_API_KEY=your-grok-api-key
   ```
3. **Configure MegaLinter**:
   ```yaml
   LLM_ADVISOR_ENABLED: true
   LLM_PROVIDER: grok
   LLM_MODEL_NAME: grok-beta
   LLM_MAX_TOKENS: 1000
   LLM_TEMPERATURE: 0.1
   ```

## Configuration Options

### Basic Configuration

```yaml
LLM_PROVIDER: grok
LLM_MODEL_NAME: grok-beta
```

### Advanced Configuration

```yaml
# Custom API endpoint (if needed)
GROK_BASE_URL: https://api.x.ai/v1
```

## Model Recommendations

- **General Use**: `grok-beta` - Currently the main available model

## Advantages

- **Conversational**: Designed for engaging, helpful interactions
- **Real-time Training**: Trained on more recent data
- **Large Context**: 128K token context window
- **OpenAI Compatible**: Uses familiar API format

## Cost Considerations

Grok pricing is competitive with other premium providers:
- Pay-per-token model
- Large context window for comprehensive analysis
- Monitor usage in xAI console

## Troubleshooting

### Common Issues

1. **"Invalid API key"**
   - Verify API key is correct
   - Check account status and access
   - Ensure Grok API access is enabled

2. **"Rate limit exceeded"**
   - Check your plan's rate limits
   - Implement exponential backoff
   - Contact xAI support for higher limits

3. **"Model not available"**
   - Verify model name: `grok-beta`
   - Check regional availability
   - Ensure you have access to the model

### Debug Mode

```yaml
LOG_LEVEL: DEBUG
```

## Best Practices

- Use `grok-beta` for conversational code analysis
- Leverage the large context window for comprehensive file analysis
- Set temperature between 0.1-0.3 for technical tasks
- Monitor usage to manage costs
- Take advantage of the conversational nature for detailed explanations

## Notes

- Grok is a newer provider, so features and pricing may evolve
- Uses OpenAI-compatible API under the hood
- Currently in beta phase with potential for updates
- Good for teams wanting an alternative to established providers
