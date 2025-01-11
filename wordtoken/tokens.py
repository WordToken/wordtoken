from typing import Dict

class TokenEstimator:
    """
    Centralized token estimator that delegates to provider-specific strategies.
    """

    def __init__(self):
        self.strategies: Dict[str, object] = {
            "openai": OpenAITokenStrategy(),
            "claude": ClaudeTokenStrategy(),
        }

    def estimate_tokens(self, prompt: str, provider: str, model: str = None) -> int:
        """
        Estimate tokens for a given provider.

        Args:
            prompt (str): The input prompt.
            provider (str): The provider name (e.g., "openai", "claude").
            model (str): The model name (optional, required for some providers).

        Returns:
            int: Estimated token count.
        """
        provider = provider.lower()
        if provider not in self.strategies:
            raise ValueError(f"Unsupported provider: {provider}")
        strategy = self.strategies[provider]
        if model:
            return strategy.estimate_tokens(prompt, model)
        return strategy.estimate_tokens(prompt)


class OpenAITokenStrategy:
    """
    Token estimation strategy for OpenAI models.
    """

    def estimate_tokens(self, prompt: str, model: str = "gpt-3.5-turbo") -> int:
        from tiktoken import encoding_for_model

        encoder = encoding_for_model(model)
        tokens = encoder.encode(prompt)
        return len(tokens)


class ClaudeTokenStrategy:
    """
    Token estimation strategy for Claude models.
    """

    def estimate_tokens(self, prompt: str) -> int:
        return len(prompt.split())