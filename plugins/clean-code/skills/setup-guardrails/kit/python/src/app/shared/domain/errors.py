"""Error hierarchy for domain and application code.

Rule: domain/application code never catches exceptions and never raises
built-ins (ValueError, RuntimeError...). It raises one of these, and a single
handler at the edge (HTTP, bot, CLI) translates the *category* into a response.
"""


class DomainError(Exception):
    code: str = "domain_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class InvalidValueError(DomainError):
    code = "invalid_value"

    def __init__(self, *, field: str, reason: str) -> None:
        super().__init__(f"{field}: {reason}")
        self.field = field


class NotFoundError(DomainError):
    code = "not_found"


class ConflictError(DomainError):
    code = "conflict"


class RuleViolationError(DomainError):
    code = "rule_violation"
