# AI-Powered Fix Suggestions (LLM Advisor)

MegaLinter includes an AI-powered advisor that provides intelligent fix suggestions for linter errors using various Large Language Models (LLMs) through LangChain.

![Advisor](assets/images/megalinter-llm-advisor.gif)

## Features

- **Multi-Provider Support**: Works with OpenAI, Anthropic, Google Gemini, Hugging Face, Mistral AI, DeepSeek, Grok, and local Ollama models
- **Context-Aware Suggestions**: Analyzes code context around errors for better recommendations
- **Integrated Reporting**: AI suggestions appear directly in MegaLinter reports
- **Configurable**: Control which models to use and how many errors to analyze

## Supported LLM Providers

| Provider                                                  | API Key Required | Local/Cloud | Documentation                                            |
|-----------------------------------------------------------|------------------|-------------|----------------------------------------------------------|
| [OpenAI](llm-provider/llm_provider_openai.md)             | Yes              | Cloud       | [Setup Guide](llm-provider/llm_provider_openai.md)       |
| [Anthropic](llm-provider/llm_provider_anthropic.md)       | Yes              | Cloud       | [Setup Guide](llm-provider/llm_provider_anthropic.md)    |
| [Google GenAI](llm-provider/llm_provider_google_genai.md) | Yes              | Cloud       | [Setup Guide](llm-provider/llm_provider_google_genai.md) |
| [Mistral AI](llm-provider/llm_provider_mistralai.md)      | Yes              | Cloud       | [Setup Guide](llm-provider/llm_provider_mistralai.md)    |
| [DeepSeek](llm-provider/llm_provider_deepseek.md)         | Yes              | Cloud       | [Setup Guide](llm-provider/llm_provider_deepseek.md)     |
| [Grok](llm-provider/llm_provider_grok.md)                 | Yes              | Cloud       | [Setup Guide](llm-provider/llm_provider_grok.md)         |
| [Ollama](llm-provider/llm_provider_ollama.md)             | No               | Local       | [Setup Guide](llm-provider/llm_provider_ollama.md)       |
| [Hugging Face](llm-provider/llm_provider_huggingface.md)  | Optional         | Local/Cloud | [Setup Guide](llm-provider/llm_provider_huggingface.md)  |

See [All LLM Providers](llm-providers.md) for a complete comparison and setup instructions.

## Quick Start

1. **Choose your provider** from the [supported providers](llm-providers.md)
2. **Set your API key** as an environment variable
3. **Configure MegaLinter** in your `.mega-linter.yml`:

```yaml
# Enable AI-powered fix suggestions
LLM_ADVISOR_ENABLED: true

# Choose your provider and model
LLM_PROVIDER: openai  # openai, anthropic, google, huggingface, mistral, deepseek, grok, ollama
LLM_MODEL_NAME: gpt-4.1-mini
LLM_MAX_TOKENS: 1000
LLM_TEMPERATURE: 0.1
```

1. **Run MegaLinter** - AI suggestions will appear in your reports

## Basic Configuration

```yaml
LLM_ADVISOR_ENABLED: true                  # Enable/disable AI advisor
LLM_ADVISOR_LEVEL: ERROR                   # When to trigger: ERROR (default) or WARNING
LLM_ADVISOR_ENABLE_LINTERS: []             # Only analyze these linters (linter names)
LLM_ADVISOR_DISABLE_LINTERS: []            # Never analyze these linters (linter names)
LLM_PROVIDER: openai                       # Provider: see supported providers above
LLM_MODEL_NAME: gpt-4.1-mini               # Model name (provider-specific)
LLM_MAX_TOKENS: 1000                       # Maximum tokens for response
LLM_TEMPERATURE: 0.1                       # Temperature for generation (0.0-1.0)
LLM_ADVISOR_POSITION: after_linter_output  # Display Advisor suggestions before or after linter output
```

## Advisor Level Configuration

The `LLM_ADVISOR_LEVEL` setting controls when AI suggestions are triggered:

### ERROR (Default)

```yaml
LLM_ADVISOR_LEVEL: ERROR
```

- AI advisor analyzes **only linters that are blocking** (return code != 0)
- Most cost-effective approach
- Focuses on critical issues that break builds
- Includes linters with errors that cause build failures

### WARNING

```yaml
LLM_ADVISOR_LEVEL: WARNING  
```

- AI advisor analyzes **both blocking and non-blocking linters**
- Includes linters with errors/warnings that don't fail the build (return code == 0)
- More comprehensive analysis covering ignored errors and warnings
- Higher API costs due to increased usage
- Helps improve code quality beyond just fixing build-breaking errors

Choose `ERROR` for cost-sensitive environments or `WARNING` for comprehensive code quality improvements.

## Position Configuration

The `LLM_ADVISOR_POSITION` setting controls where AI suggestions appear in the linter output:

### after_linter_output (Default)

```yaml
LLM_ADVISOR_POSITION: after_linter_output
```

- AI suggestions appear **after** the original linter error messages
- Maintains traditional linter output format at the top
- Better for users who want to see standard linter output first
- Recommended for most use cases

### before_linter_output

```yaml
LLM_ADVISOR_POSITION: before_linter_output
```

- AI suggestions appear **before** the original linter error messages
- Prioritizes AI guidance over raw linter output
- Useful when AI suggestions are the primary focus
- May help users understand errors before seeing technical details

## Linter-Specific Configuration

You can control which specific linters the AI advisor should analyze using these settings:

### LLM_ADVISOR_ENABLE_LINTERS

```yaml
LLM_ADVISOR_ENABLE_LINTERS:
  - PYTHON_PYLINT
  - JAVASCRIPT_ESLINT
  - TYPESCRIPT_ESLINT
```

- Only the specified linters will be analyzed by the AI advisor
- Takes precedence over `LLM_ADVISOR_DISABLE_LINTERS` if both are set
- Useful for focusing on critical linters to reduce API costs

### LLM_ADVISOR_DISABLE_LINTERS

```yaml
LLM_ADVISOR_DISABLE_LINTERS:
  - PYTHON_BANDIT
  - DOCKERFILE_HADOLINT
```

- These linters will never be analyzed by the AI advisor
- Ignored if `LLM_ADVISOR_ENABLE_LINTERS` is also set
- Useful for excluding noisy or less critical linters

### Priority Order

1. **Enable List**: If `LLM_ADVISOR_ENABLE_LINTERS` is set, only those linters are analyzed
2. **Disable List**: If only `LLM_ADVISOR_DISABLE_LINTERS` is set, all linters except those are analyzed
3. **Level Filter**: `LLM_ADVISOR_LEVEL` (ERROR/WARNING) is then applied to the filtered linters

## Security Considerations

⚠️ **Important**: Set API credentials as environment variables in your CI/CD system, not in `.mega-linter.yml` files.

```bash
# Examples (choose your provider)
OPENAI_API_KEY=sk-your-api-key
ANTHROPIC_API_KEY=sk-ant-your-api-key
GOOGLE_API_KEY=AIza-your-api-key
```

For detailed provider setup instructions, see the individual provider documentation pages linked above.

## Bot Detection & Cost Control

To prevent unnecessary API costs and avoid analyzing automated dependency updates, MegaLinter automatically disables LLM Advisor for bot-generated pull requests in CI/CD environments (requires an up to date CI/CD workflow)

### Automatic Bot Detection

MegaLinter includes built-in logic to detect common bots and automated PRs:

- **GitHub Actions**: Detects Dependabot, Renovate, and GitHub Actions bot PRs
- **GitLab CI**: Identifies bot merge requests using author and title patterns
- **Azure Pipelines**: Checks branch names and requestor information for bot patterns
- **Bitbucket**: Analyzes branch names and PR titles for automation patterns
- **Jenkins**: Examines branch names and change authors for bot signatures
- **Drone CI**: Filters based on PR titles and commit authors
- **Concourse CI**: Uses pipeline and job names for bot detection

### Detection Patterns

The following patterns automatically disable LLM Advisor:

**Bot Accounts:**

- `dependabot[bot]`, `renovate[bot]`, `github-actions[bot]`
- User names starting with `dependabot` or `renovate`

**PR/MR Titles:**

- Commits starting with `chore:`, `fix:`, `deps:`, `bump:`
- Dependency update patterns like `Bump package from x.x.x to y.y.y`

### Manual Override

You can manually control LLM Advisor activation:

```yaml
# Force enable even for detected bots (not recommended due to costs)
LLM_ADVISOR_ENABLED: true

# Force disable for specific branches or conditions
LLM_ADVISOR_ENABLED: false
```

⚠️ **Cost Warning**: Enabling LLM Advisor for bot PRs can lead to significant API costs since dependency update PRs are frequent and often contain many changes.

## How It Works

1. **Error Collection**: MegaLinter collects errors from active linters
2. **Context Analysis**: The AI advisor analyzes code context around each error
3. **AI Processing**: Errors are sent to the configured LLM with structured prompts
4. **Suggestion Generation**: The LLM provides explanations and fix recommendations
5. **Report Integration**: Suggestions are added to the markdown summary report

## Example Output

When AI advisor is enabled, you'll see a new section in your MegaLinter reports:

```markdown
## 🤖 AI-Powered Fix Suggestions (openai - gpt-4.1-mini)

Analyzed 3 out of 5 errors:

### 1. src/example.py

**Line 15** - flake8 (F401)

**Error:** 'os' imported but unused

**AI Suggestion:**
This error occurs because you've imported the `os` module but haven't used it anywhere in your code. To fix this:

1. Remove the unused import: Delete the line `import os`
2. Or if you plan to use it later, add a comment: `import os  # TODO: will be used for file operations`
3. Alternatively, if it's used in a way the linter doesn't detect, you can disable the warning: `import os  # noqa: F401`

**Best Practice:** Only import modules that you actually use to keep your code clean and improve performance.

---

### 2. styles/main.css

**Line 23** - stylelint (block-no-empty)

**Error:** Unexpected empty block

**AI Suggestion:**

Empty CSS blocks serve no purpose and should be removed. To fix this:

1. **Remove the empty block entirely** if it's not needed
2. **Add CSS properties** if the selector should style something
3. **Add a comment** if you're planning to add styles later

Example fix:
```css
/* Remove this: */
.empty-class {
}

/* Or add content: */
.empty-class {
  /* Styles will be added later */
}
```

## Limitations & Considerations

- **API Costs**: Cloud providers charge for API usage
- **Rate Limits**: Providers may have request limits
- **Token Limits**: Large files may be truncated for analysis
- **Accuracy**: AI suggestions should be reviewed before applying
- **Privacy**: Code snippets are sent to the LLM provider for analysis (use local Ollama for private code)

## Troubleshooting

### Common Issues

1. **"LLM Advisor not available"**

   - Check that `LLM_ADVISOR_ENABLED: true`
   - Verify LangChain dependencies are installed
   - Ensure API keys are set correctly

2. **"Failed to initialize LLM"**

   - Verify API key is valid and has sufficient credits
   - Check internet connection for cloud providers
   - For Ollama, ensure the service is running locally

3. **No suggestions generated**

   - Check if errors were detected by linters
   - Verify the linter output format is parseable
   - Review logs for parsing errors

### Debug Mode

Enable debug logging to troubleshoot issues:

```yaml
LOG_LEVEL: DEBUG
```

This will show detailed information about LLM requests and responses.
```
