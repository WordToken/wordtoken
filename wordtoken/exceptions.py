class WordTokenError(Exception):
    """Base exception for WordToken library."""
    pass

class AdapterError(WordTokenError):
    """Exception for adapter-specific errors."""
    pass