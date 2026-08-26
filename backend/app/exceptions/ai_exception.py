class AIUnavailableError(Exception):
    """A controlled failure from the optional AI provider layer."""


class AIRateLimitError(AIUnavailableError):
    """Raised when an organization exceeds the configured AI request budget."""


class AIResponseValidationError(AIUnavailableError):
    """Raised when a provider response cannot satisfy the grounded contract."""
