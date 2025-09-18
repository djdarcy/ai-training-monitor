"""
Base parser interface for AI training frameworks
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pathlib import Path
import re


class BaseParser(ABC):
    """Base class for all training log parsers"""

    # Framework name (override in subclass)
    name: str = "base"

    # Description for UI
    description: str = "Base parser"

    # File patterns this parser can handle
    file_patterns: List[str] = ["*.log", "*.txt"]

    # Metric patterns (override in subclass)
    patterns: Dict[str, str] = {}

    def __init__(self, log_path: Optional[Path] = None):
        """
        Initialize parser

        Args:
            log_path: Path to log file or directory
        """
        self.log_path = Path(log_path) if log_path else None
        self.file_handle = None
        self.position = 0

    @abstractmethod
    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single line from the log

        Args:
            line: Log line to parse

        Returns:
            Dictionary of extracted metrics or None if no metrics found
        """
        pass

    @abstractmethod
    def detect_format(self, sample_lines: List[str]) -> float:
        """
        Detect if this parser can handle the log format

        Args:
            sample_lines: Sample lines from the log file

        Returns:
            Confidence score (0.0 to 1.0) that this parser can handle the format
        """
        pass

    def find_log_file(self) -> Optional[Path]:
        """
        Find the appropriate log file to monitor

        Returns:
            Path to log file or None if not found
        """
        if self.log_path is None:
            return None

        if self.log_path.is_file():
            return self.log_path

        if self.log_path.is_dir():
            # Look for common log file names
            for pattern in self.file_patterns:
                for log_file in self.log_path.glob(pattern):
                    if log_file.is_file():
                        return log_file

        return None

    def open_file(self):
        """Open the log file for reading"""
        log_file = self.find_log_file()
        if log_file and log_file.exists():
            self.file_handle = open(log_file, 'r')
            # Go to end of file for tailing
            self.file_handle.seek(0, 2)
            self.position = self.file_handle.tell()

    def close_file(self):
        """Close the log file"""
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None

    def tail_file(self) -> List[str]:
        """
        Read new lines from the log file (like tail -f)

        Returns:
            List of new lines
        """
        new_lines = []

        if not self.file_handle:
            self.open_file()

        if self.file_handle:
            # Seek to last position
            self.file_handle.seek(self.position)

            # Read new lines
            for line in self.file_handle:
                line = line.strip()
                if line:
                    new_lines.append(line)

            # Update position
            self.position = self.file_handle.tell()

        return new_lines

    def extract_metric(self, line: str, metric_name: str, pattern: str) -> Optional[float]:
        """
        Extract a numeric metric from a line using regex

        Args:
            line: Log line
            metric_name: Name of the metric
            pattern: Regex pattern to extract the metric

        Returns:
            Extracted metric value or None
        """
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except (ValueError, IndexError):
                pass
        return None

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the training run

        Returns:
            Dictionary of metadata (model name, dataset, etc.)
        """
        return {
            'parser': self.name,
            'log_path': str(self.log_path) if self.log_path else None
        }

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"