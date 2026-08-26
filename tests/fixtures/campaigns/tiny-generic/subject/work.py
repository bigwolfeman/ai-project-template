"""Mutable subject for the tiny-generic fixture campaign."""

# Baseline latency. Integration tests may lower this to demonstrate improvement.
LATENCY_MS = 100


def ok() -> bool:
    return True
