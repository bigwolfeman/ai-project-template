"""Adapter registry. Default: generic_command."""

from __future__ import annotations

from typing import Any

from ..errors import AdapterError
from .base import Adapter
from .generic_command import GenericCommandAdapter
from .prompt_eval import PromptEvalAdapter
from .pytest_benchmark import PytestBenchmarkAdapter

_REGISTRY: dict[str, type] = {
    "generic_command": GenericCommandAdapter,
    "pytest_benchmark": PytestBenchmarkAdapter,
    "prompt_eval": PromptEvalAdapter,
}


def register_adapter(name: str, cls: type) -> None:
    if not name:
        raise AdapterError("adapter name must be non-empty", field="adapter")
    _REGISTRY[name] = cls


def get_adapter(name: str) -> Adapter:
    """Return an adapter instance by name."""
    key = (name or "generic_command").strip()
    if key not in _REGISTRY:
        known = ", ".join(sorted(_REGISTRY))
        raise AdapterError(
            f"unknown adapter {key!r}; known: {known}",
            field="adapter",
        )
    cls = _REGISTRY[key]
    instance: Any = cls()
    return instance  # type: ignore[no-any-return]


def adapter_name_from_manifest(manifest: dict[str, Any]) -> str:
    """Resolve adapter name from optional manifest field `adapter`."""
    raw = manifest.get("adapter")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    return "generic_command"
