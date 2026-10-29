"""Compatibility exports; importing configuration creates no directories or clients."""
from rag_core.settings import Settings, initialize, load_settings

__all__ = ["Settings", "initialize", "load_settings"]
