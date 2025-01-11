# WordToken

WordToken is a lightweight and flexible Python library for interacting with popular large language model (LLM) providers, such as OpenAI and Anthropic's Claude. It offers a unified interface for generating text, estimating token usage, and calculating costs, making it ideal for both experimentation and production use.

## Features

- **Unified Interface**: Interact seamlessly with multiple LLM providers through a single API.
- **Token Management**: Estimate token usage for prompts and responses.
- **Cost Estimation**: Calculate costs based on provider-specific pricing.
- **Extensible**: Easily add support for additional LLM providers.
- **Sandbox-Friendly**: Designed for experimentation and real-world integration.

## Installation

Install WordToken using pip:

```bash
pip install wordtoken
```

## Supported LLM Providers
	•	OpenAI
	•	Anthropic Claude

## Usage

### Initialize the Library

```
from wordtoken import WordToken

# Initialize WordToken with your API key
token = WordToken(api_key="your-api-key")
```

### Generate Text

```
# Generate text with OpenAI
response = wordtoken.send_prompt(
    prompt="Write a short story about a robot learning to love.",
    model="gpt-3.5-turbo",
    max_tokens=100,
    temperature=0.7
)
print(response["output"])
```


### Estimate Tokens

```
# Estimate tokens for a prompt
tokens = wordtoken.estimate_tokens(prompt="Hello, world!", model="gpt-3.5-turbo")
print(f"Estimated tokens: {tokens}")
```

### Estimate Costs

```
# Estimate cost for a given number of tokens
tokens = 100  # Example token count
cost = wordtoken.calculate_cost(tokens=tokens, model="gpt-3.5-turbo")
print(f"Estimated cost: ${cost:.4f}")
```

## Configuration

### Available Models and Defaults
 * OpenAI:
 *   Models: gpt-3.5-turbo, gpt-4, gpt-4o
 *   Pricing: Automatically managed based on the latest OpenAI rates.
 * Claude (Anthropic):
 *   Models: claude-v1, claude-v2, etc.
 *   Pricing: Configurable for Anthropic's usage tiers. 

### Adding New Providers

Extend the library by adding a new adapter in the adapters.py file and updating the unified interface in the __init__.py file.


## Development

### Clone the Repository
```
git clone https://github.com/your-username/wordtoken.git
cd wordtoken
```

### Install Dependencies
```
pip install -r requirements.txt
```

### Run Tests
```
pytest
```

## License

WordToken is licensed under the Apache License 2.0.

## Contributing

Contributions are welcome! Please feel free to submit a pull request.


## Roadmap
	•	Support for additional LLM providers (e.g., Google Gemini, Cohere).
	•	Advanced token visualization and usage analytics.
	•	Integration with sandbox tools for prompt experimentation.

## Contact

For questions or feedback, please contact contact@wordtoken.com.

