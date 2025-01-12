from .base_adapter import BaseAdapter
from .tokens import TokenEstimator
from .costs import CostEstimator
from openai import OpenAI

client = OpenAI(api_key=api_key)


class OpenAIAdapter(BaseAdapter):
    """
    Adapter for interacting with OpenAI's API and estimating costs.
    """

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.token_estimator = TokenEstimator()
        self.cost_estimator = CostEstimator()

    def send_prompt(self, prompt: str, model: str = "gpt-3.5-turbo", **kwargs) -> dict:
        response = client.chat.completions.create(model=model,
        messages=[{"role": "user", "content": prompt}],
        **kwargs)
        return {"output": response.choices[0].message.content}

    def estimate_tokens(self, prompt: str, model: str = "gpt-3.5-turbo") -> int:
        return self.token_estimator.estimate_tokens(prompt, provider="openai", model=model)

    def calculate_cost(self, tokens: int, model: str = "gpt-3.5-turbo") -> float:
        return self.cost_estimator.calculate_cost(tokens, provider="openai", model=model)


class ClaudeAdapter(BaseAdapter):
    """
    Adapter for interacting with Anthropic's Claude API and estimating costs.
    """

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.token_estimator = TokenEstimator()
        self.cost_estimator = CostEstimator()

    def send_prompt(self, prompt: str, model: str = "claude-v1", **kwargs) -> dict:
        # Replace this with an actual API call to Claude
        response = {"completion": "Generated response from Claude"}
        return {"output": response.completion}

    def estimate_tokens(self, prompt: str, model: str = "claude-v1") -> int:
        return self.token_estimator.estimate_tokens(prompt, provider="claude", model=model)

    def calculate_cost(self, tokens: int, model: str = "claude-v1") -> float:
        return self.cost_estimator.calculate_cost(tokens, provider="claude", model=model)