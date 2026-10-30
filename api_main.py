"""Compatibility factory: uvicorn api_main:create_app --factory (private config required)."""

from rag_core.api import create_app

__all__ = ["create_app"]
