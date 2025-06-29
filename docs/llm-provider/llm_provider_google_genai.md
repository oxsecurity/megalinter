# Google GenAI Provider

Google's Gemini models offer excellent performance at competitive prices with strong multilingual support.

## Supported Models

| Model               | Context Length | Cost | Best For                  |
|---------------------|----------------|------|---------------------------|
| `gemini-pro`        | 30K tokens     | $    | General code analysis     |
| `gemini-pro-vision` | 30K tokens     | $    | Code with visual elements |

## Setup

1. **Get API Key**:
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
2. **Set Environment Variable**:
   ```bash
   export GOOGLE_API_KEY=AIza-your-api-key
   ```
3. **Configure MegaLinter**:
   ```yaml
   LLM_ADVISOR_ENABLED: true
   LLM_PROVIDER: google
   LLM_MODEL_NAME: gemini-pro
   LLM_MAX_TOKENS: 1000
   LLM_TEMPERATURE: 0.1
   ```

## Configuration Options

### Basic Configuration

```yaml
LLM_PROVIDER: google
LLM_MODEL_NAME: gemini-pro          # or gemini-pro-vision
```

### Advanced Configuration

```yaml
# Custom settings (rarely needed)
GOOGLE_APPLICATION_CREDENTIALS: /path/to/service-account.json
```

## Model Recommendations

- **Standard Use**: `gemini-pro` - Excellent for most code analysis tasks
- **Visual Content**: `gemini-pro-vision` - When dealing with diagrams, screenshots in docs

## Advantages

- **Cost-Effective**: Very competitive pricing
- **Fast Responses**: Quick analysis and suggestions
- **Multilingual**: Excellent support for non-English codebases
- **Google Integration**: Works well with Google Cloud ecosystem

## Cost Considerations

Google offers very competitive pricing:
- Free tier available with rate limits
- Pay-per-use pricing for production
- Monitor usage in [Google Cloud Console](https://console.cloud.google.com/)

## Troubleshooting

### Common Issues

1. **"API key not valid"**
   - Verify API key format: `AIza...`
   - Check that Generative AI API is enabled
   - Ensure you're in a supported region

2. **"Quota exceeded"**
   - Check your quota limits in Google Cloud Console
   - Request quota increases if needed
   - Implement rate limiting

3. **"Model not found"**
   - Verify model name is correct
   - Check regional availability
   - Some models may require special access

### Debug Mode

```yaml
LOG_LEVEL: DEBUG
```

## Best Practices

- Start with the free tier for testing
- Use `gemini-pro` for most code analysis tasks
- Monitor usage to stay within quotas
- Consider regional data residency requirements
- Use appropriate temperature settings (0.1-0.3) for technical tasks
