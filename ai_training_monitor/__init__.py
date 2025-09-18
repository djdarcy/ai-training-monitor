"""
AI Training Monitor - Universal training visualization for AI/ML frameworks

A Process Explorer-style application for monitoring AI training in real-time.
"""

__version__ = "0.1.0"
__author__ = "AI Training Monitor Contributors"

from .core.monitor import TrainingMonitor
from .parsers.base import BaseParser

__all__ = [
    "TrainingMonitor",
    "BaseParser",
    "__version__",
]