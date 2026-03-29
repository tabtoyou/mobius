"""Mobius core module - shared types, errors, and protocols.

This package uses lazy re-exports so importing submodules such as
`mobius.core.errors` does not eagerly import heavier modules like
`mobius.core.context` and create circular import chains during CLI startup.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORTS: dict[str, tuple[str, str]] = {
    # Types
    "Result": ("mobius.core.types", "Result"),
    "EventPayload": ("mobius.core.types", "EventPayload"),
    "CostUnits": ("mobius.core.types", "CostUnits"),
    "DriftScore": ("mobius.core.types", "DriftScore"),
    # Errors
    "MobiusError": ("mobius.core.errors", "MobiusError"),
    "ProviderError": ("mobius.core.errors", "ProviderError"),
    "ConfigError": ("mobius.core.errors", "ConfigError"),
    "PersistenceError": ("mobius.core.errors", "PersistenceError"),
    "ValidationError": ("mobius.core.errors", "ValidationError"),
    # Seed
    "Seed": ("mobius.core.seed", "Seed"),
    "SeedMetadata": ("mobius.core.seed", "SeedMetadata"),
    "OntologySchema": ("mobius.core.seed", "OntologySchema"),
    "OntologyField": ("mobius.core.seed", "OntologyField"),
    "EvaluationPrinciple": ("mobius.core.seed", "EvaluationPrinciple"),
    "ExitCondition": ("mobius.core.seed", "ExitCondition"),
    # Context management
    "WorkflowContext": ("mobius.core.context", "WorkflowContext"),
    "ContextMetrics": ("mobius.core.context", "ContextMetrics"),
    "CompressionResult": ("mobius.core.context", "CompressionResult"),
    "FilteredContext": ("mobius.core.context", "FilteredContext"),
    "count_tokens": ("mobius.core.context", "count_tokens"),
    "count_context_tokens": ("mobius.core.context", "count_context_tokens"),
    "get_context_metrics": ("mobius.core.context", "get_context_metrics"),
    "compress_context": ("mobius.core.context", "compress_context"),
    "compress_context_with_llm": ("mobius.core.context", "compress_context_with_llm"),
    "create_filtered_context": ("mobius.core.context", "create_filtered_context"),
    # Git workflow
    "GitWorkflowConfig": ("mobius.core.git_workflow", "GitWorkflowConfig"),
    "detect_git_workflow": ("mobius.core.git_workflow", "detect_git_workflow"),
    "is_on_protected_branch": ("mobius.core.git_workflow", "is_on_protected_branch"),
    # Security utilities
    "InputValidator": ("mobius.core.security", "InputValidator"),
    "mask_api_key": ("mobius.core.security", "mask_api_key"),
    "validate_api_key_format": ("mobius.core.security", "validate_api_key_format"),
    "sanitize_for_logging": ("mobius.core.security", "sanitize_for_logging"),
}

__all__ = list(_EXPORTS)


def __getattr__(name: str) -> Any:
    """Lazily import shared core symbols on first access."""
    try:
        module_name, attr_name = _EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(f"module 'mobius.core' has no attribute {name!r}") from exc

    value = getattr(import_module(module_name), attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    """Expose lazy exports to interactive tooling."""
    return sorted(set(globals()) | set(__all__))
