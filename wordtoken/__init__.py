from .adapters import OpenAIAdapter, ClaudeAdapter
from .base_adapter import BaseAdapter


class WordToken:
    """
    Unified interface for interacting with various LLM providers.
    """

    def __init__(self, provider: str, api_key: str) -> None:
        self.adapter: BaseAdapter = self._initialize_adapter(provider, api_key)

    def _initialize_adapter(self, provider: str, api_key: str) -> BaseAdapter:
        if provider.lower() == "openai":
            return OpenAIAdapter(api_key)
        elif provider.lower() == "claude":
            return ClaudeAdapter(api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def set_provider(self, provider: str, api_key: str) -> None:
        self.adapter = self._initialize_adapter(provider, api_key)

    def send_prompt(self, prompt: str, **kwargs) -> dict:
        return self.adapter.send_prompt(prompt, **kwargs)

    def estimate_tokens(self, prompt: str, **kwargs) -> int:
        return self.adapter.estimate_tokens(prompt, **kwargs)

    def calculate_cost(self, tokens: int, **kwargs) -> float:
        return self.adapter.calculate_cost(tokens, **kwargs)