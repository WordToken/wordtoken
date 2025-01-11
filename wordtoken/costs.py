from typing import Dict

class CostEstimator:
    """
    Centralized cost estimator that delegates to provider-specific strategies.
    """

    def __init__(self):
        self.strategies: Dict[str, object] = {
            "openai": OpenAICostStrategy(),
            "claude": ClaudeCostStrategy(),
        }

    def calculate_cost(self, tokens: int, provider: str, model: str) -> float:
        """
        Calculate cost for a given provider.

        Args:
            tokens (int): Number of tokens.
            provider (str): The provider name (e.g., "openai", "claude").
            model (str): The model name.

        Returns:
            float: Estimated cost in USD.
        """
        provider = provider.lower()
        if provider not in self.strategies:
            raise ValueError(f"Unsupported provider: {provider}")
        strategy = self.strategies[provider]
        return strategy.calculate_cost(tokens, model)


class OpenAICostStrategy:
    """
    Cost estimation strategy for OpenAI models.
    """

    PRICING = {
        "gpt-3.5-turbo": 0.002,
        "gpt-4": 0.03,
    }

    def calculate_cost(self, tokens: int, model: str = "gpt-3.5-turbo") -> float:
        if model not in self.PRICING:
            raise ValueError(f"Unsupported OpenAI model: {model}")
        cost_per_1000_tokens = self.PRICING[model]
        return (tokens / 1000) * cost_per_1000_tokens


class ClaudeCostStrategy:
    """
    Cost estimation strategy for Claude models.
    """

    PRICING = {
        "claude-v1": 0.015,
    }

    def calculate_cost(self, tokens: int, model: str = "claude-v1") -> float:
        if model not in self.PRICING:
            raise ValueError(f"Unsupported Claude model: {model}")
        cost_per_1000_tokens = self.PRICING[model]
        return (tokens / 1000) * cost_per_1000_tokens