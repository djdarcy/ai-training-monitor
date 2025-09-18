#!/usr/bin/env python
"""
Quick start script for AI Training Monitor
"""
import sys
from pathlib import Path

# Add the package to path for development
sys.path.insert(0, str(Path(__file__).parent))

from ai_training_monitor.__main__ import main

if __name__ == '__main__':
    main()