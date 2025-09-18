"""
Parser for Ostris AI Toolkit training logs
"""
import re
from typing import Dict, Optional, Any, List
from pathlib import Path

from .base import BaseParser


class OstrisParser(BaseParser):
    """Parser for Ostris AI Toolkit log format"""

    name = "ostris"
    description = "Ostris AI Toolkit (LoRA/Dreambooth training)"

    # File patterns for Ostris logs
    file_patterns = ["log.txt", "*.log", "logs/*.txt"]

    # Regex patterns for extracting metrics
    patterns = {
        # Main training line pattern: "1335/3000 [12:53<4:03:22, 8.77s/it, lr: 2.0e-04 loss: 6.751e-02]"
        'main_pattern': r'(\d+)/(\d+)\s*\[.*?(\d+\.?\d*)s/it.*?lr:\s*([\d.e+-]+).*?loss:\s*([\d.e+-]+)',

        # Alternative patterns for different Ostris versions
        'loss': r'loss[:\s]*([\d.e+-]+)',
        'lr': r'lr[:\s]*([\d.e+-]+)',
        'speed': r'(\d+\.?\d*)s/it',
        'step': r'(\d+)/(\d+)',
        'epoch': r'epoch[:\s]*(\d+)',
        'gpu_memory': r'(\d+\.?\d*)G/(\d+\.?\d*)G',

        # Additional Ostris-specific patterns
        'sample_loss': r'sample_loss[:\s]*([\d.e+-]+)',
        'prior_loss': r'prior_loss[:\s]*([\d.e+-]+)',
        'kl_loss': r'kl_loss[:\s]*([\d.e+-]+)',
    }

    def __init__(self, log_path: Optional[Path] = None):
        """Initialize Ostris parser"""
        super().__init__(log_path)
        self.last_step = 0
        self.total_steps = None

    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single line from Ostris log

        Args:
            line: Log line to parse

        Returns:
            Dictionary of extracted metrics or None
        """
        if not line or line.isspace():
            return None

        metrics = {}

        # Try main pattern first (most common Ostris format)
        main_match = re.search(self.patterns['main_pattern'], line)
        if main_match:
            metrics['current_step'] = int(main_match.group(1))
            metrics['total_steps'] = int(main_match.group(2))
            metrics['speed'] = float(main_match.group(3))
            metrics['lr'] = float(main_match.group(4))
            metrics['loss'] = float(main_match.group(5))

            # Store for progress tracking
            self.last_step = metrics['current_step']
            self.total_steps = metrics['total_steps']

            # Calculate epoch if we have dataset size info
            # This would need to be enhanced with actual dataset size
            metrics['step'] = metrics['current_step']

        else:
            # Fall back to individual pattern matching
            for metric, pattern in self.patterns.items():
                if metric == 'main_pattern':
                    continue

                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    if metric == 'step':
                        metrics['current_step'] = int(match.group(1))
                        metrics['total_steps'] = int(match.group(2))
                        metrics['step'] = metrics['current_step']
                        self.last_step = metrics['current_step']
                        self.total_steps = metrics['total_steps']
                    elif metric == 'gpu_memory':
                        metrics['gpu_used'] = float(match.group(1))
                        metrics['gpu_total'] = float(match.group(2))
                    elif metric in ['sample_loss', 'prior_loss', 'kl_loss']:
                        # Additional Ostris-specific losses
                        metrics[metric] = float(match.group(1))
                    else:
                        try:
                            metrics[metric] = float(match.group(1))
                        except (ValueError, IndexError):
                            pass

        # Only return if we found meaningful metrics
        if metrics and ('loss' in metrics or 'current_step' in metrics):
            return metrics

        return None

    def detect_format(self, sample_lines: List[str]) -> float:
        """
        Detect if this parser can handle the log format

        Args:
            sample_lines: Sample lines from the log file

        Returns:
            Confidence score (0.0 to 1.0)
        """
        if not sample_lines:
            return 0.0

        matches = 0
        ostris_indicators = [
            'loss:',
            'lr:',
            's/it',
            'Training LoRA',
            'Ostris',
            'kohya',
            'sample_loss',
        ]

        for line in sample_lines:
            line_lower = line.lower()

            # Check for Ostris-specific indicators
            for indicator in ostris_indicators:
                if indicator.lower() in line_lower:
                    matches += 1
                    break

            # Check for main pattern
            if re.search(self.patterns['main_pattern'], line):
                matches += 2  # Strong indicator

        # Calculate confidence
        confidence = min(matches / max(len(sample_lines), 1), 1.0)

        # Boost confidence if we see specific Ostris patterns
        if any('ostris' in line.lower() or 'kohya' in line.lower() for line in sample_lines):
            confidence = min(confidence + 0.3, 1.0)

        return confidence

    def find_log_file(self) -> Optional[Path]:
        """
        Find Ostris log file in standard locations

        Returns:
            Path to log file or None
        """
        if self.log_path is None:
            return None

        # If it's a file, return it
        if self.log_path.is_file():
            return self.log_path

        # If it's a directory, look for Ostris log patterns
        if self.log_path.is_dir():
            # Check for main log.txt
            main_log = self.log_path / "log.txt"
            if main_log.exists():
                return main_log

            # Check logs subdirectory
            logs_dir = self.log_path / "logs"
            if logs_dir.exists():
                # Find most recent log
                log_files = list(logs_dir.glob("*.txt")) + list(logs_dir.glob("*.log"))
                if log_files:
                    # Sort by modification time
                    log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                    return log_files[0]

            # Check for any .log or .txt in main directory
            for pattern in ["*.log", "*.txt"]:
                for log_file in self.log_path.glob(pattern):
                    if log_file.is_file():
                        return log_file

        return None

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the Ostris training run

        Returns:
            Dictionary of metadata
        """
        metadata = super().get_metadata()

        # Add Ostris-specific metadata
        metadata.update({
            'framework': 'Ostris AI Toolkit',
            'training_type': 'LoRA/Dreambooth',
            'last_step': self.last_step,
            'total_steps': self.total_steps,
        })

        # Try to extract model info from log path
        if self.log_path:
            # Path might be like: output/character/log.txt
            parts = self.log_path.parts
            if 'output' in parts:
                idx = parts.index('output')
                if idx + 1 < len(parts):
                    metadata['model_name'] = parts[idx + 1]

        return metadata