"""Application services: thin wrappers around usecases that are injected with ports/adapters.
Controllers should call services rather than calling usecases directly to keep wiring in one place.
"""

__all__ = ["user_service"]
