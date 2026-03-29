"""LLM provider adapters for Mobius.

This module provides unified access to LLM providers through the LLMAdapter
protocol, plus factory helpers for selecting local Claude Code or LiteLLM-backed
providers from configuration.
"""

from mobius.providers.anthropic_adapter import AnthropicAdapter
from mobius.providers.base import (
    CompletionConfig,
    CompletionResponse,
    LLMAdapter,
    Message,
    MessageRole,
    UsageInfo,
)
from mobius.providers.factory import (
    create_llm_adapter,
    resolve_llm_backend,
    resolve_llm_permission_mode,
)


def __getattr__(name: str) -> object:
    """Lazy import for optional adapters to avoid hard dependency on optional packages."""
    if name == "LiteLLMAdapter":
        from mobius.providers.litellm_adapter import LiteLLMAdapter

        return LiteLLMAdapter
    if name == "CodexCliLLMAdapter":
        from mobius.providers.codex_cli_adapter import CodexCliLLMAdapter

        return CodexCliLLMAdapter
    # TODO: uncomment when OpenCode adapter is shipped
    # if name == "OpenCodeLLMAdapter":
    #     from mobius.providers.opencode_adapter import OpenCodeLLMAdapter
    #     return OpenCodeLLMAdapter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Protocol
    "LLMAdapter",
    # Models
    "Message",
    "MessageRole",
    "CompletionConfig",
    "CompletionResponse",
    "UsageInfo",
    # Implementations (AnthropicAdapter is the recommended default)
    "AnthropicAdapter",
    "CodexCliLLMAdapter",
    # "OpenCodeLLMAdapter",  # TODO: uncomment when shipped
    "LiteLLMAdapter",
    # Factory helpers
    "create_llm_adapter",
    "resolve_llm_backend",
    "resolve_llm_permission_mode",
]
