"""
AI Training Monitor - Universal training visualization for AI/ML frameworks

A Process Explorer-style application for monitoring AI training in real-time.
"""

from .version import __version__, get_version, get_base_version, VERSION, BASE_VERSION

__author__ = "AI Training Monitor Contributors"

from .core.monitor import TrainingMonitor
from .parsers.base import BaseParser

__all__ = [
    "TrainingMonitor",
    "BaseParser",
    "__version__",
    "get_version",
    "get_base_version",
    "VERSION",
    "BASE_VERSION",
]