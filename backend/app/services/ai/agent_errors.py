"""Exceptions raised inside agent tool execution.

These are caught by the agent engine and converted into tool_result error
messages that get fed back to Claude, so the model can react in natural
language. They are NOT 5xx HTTP errors — the agent loop continues.
"""


class AgentToolError(Exception):
    """Base for any tool-related failure that should be surfaced to the model."""

    def __init__(self, message: str, *, code: str = "TOOL_ERROR") -> None:
        super().__init__(message)
        self.code = code


class ToolValidationError(AgentToolError):
    """Inputs failed validation (out of bounds, ownership mismatch, etc.).

    Treat this like a 400-equivalent — Claude should rephrase or apologise to
    the user, not retry blindly.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message, code="TOOL_VALIDATION")


class ToolNotFoundError(AgentToolError):
    """Tool name is not registered."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Unknown tool: {name}", code="TOOL_NOT_FOUND")


class ToolExecutionError(AgentToolError):
    """Tool raised unexpectedly during execution."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="TOOL_EXECUTION")
