class BaseAdapter:
    """
    Abstract base class for LLM adapters. Defines the required methods for providers.
    """

    def send_prompt(self, prompt: str, **kwargs) -> dict:
        """
        Send a prompt to the LLM and return the response.
        """
        raise NotImplementedError

    def estimate_tokens(self, prompt: str, **kwargs) -> int:
        """
        Estimate the number of tokens used by the prompt.
        """
        raise NotImplementedError

    def calculate_cost(self, tokens: int, **kwargs) -> float:
        """
        Calculate the cost of the tokens based on the provider's pricing.
        """
        raise NotImplementedError