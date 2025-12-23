<div align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/8/8a/Google_Gemini_logo.svg" alt="Google Gemini Logo" style="max-width: 100px; margin-bottom: 1em;" />
</div>

# Google GenAI Provider

Google's Gemini models offer excellent performance at competitive prices with strong multilingual support.

## Setup

1. **Get API Key**:

   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key

2. **Set Environment Variable**:

Set **GOOGLE_API_KEY=AIza-your-api-key** in your CI/CD secret variables.

> Make sure the secret variable is sent to MegaLinter from your CI/CD workflow. Example in GitHub Action: `GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}`

1. **Configure MegaLinter**:

```yaml
LLM_ADVISOR_ENABLED: true
LLM_PROVIDER: google
LLM_MODEL_NAME: gemini-2.5-flash
LLM_MAX_TOKENS: 1000
LLM_TEMPERATURE: 0.1
```

## Official Model List

For the most up-to-date list of Gemini models and their capabilities, see the official Google documentation:

- [Google Gemini Model List](https://ai.google.dev/models/gemini)

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
