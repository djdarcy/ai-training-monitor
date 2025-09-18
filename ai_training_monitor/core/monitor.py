"""
Main training monitor orchestrator
"""
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

from ..parsers.base import BaseParser
from .data_manager import DataManager
from .analyzer import MetricsAnalyzer


logger = logging.getLogger(__name__)


class TrainingMonitor:
    """Main training monitor that coordinates parsing, analysis, and data management"""

    def __init__(self, log_path: Optional[Path] = None,
                 parser: Optional[BaseParser] = None,
                 max_points: int = 5000,
                 update_interval: float = 1.0):
        """
        Initialize training monitor

        Args:
            log_path: Path to log file or directory
            parser: Parser instance to use (auto-detected if None)
            max_points: Maximum data points to keep in memory
            update_interval: Update interval in seconds
        """
        self.log_path = Path(log_path) if log_path else None
        self.parser = parser
        self.max_points = max_points
        self.update_interval = update_interval

        # Core components
        self.data_manager = DataManager(max_points=max_points)
        self.analyzer = MetricsAnalyzer()

        # Threading control
        self.monitor_thread = None
        self.stop_event = threading.Event()
        self.running = False

        # Callbacks
        self.callbacks = {
            'on_metrics': [],
            'on_analysis': [],
            'on_error': [],
        }

        # Auto-detect parser if needed
        if self.log_path and not self.parser:
            self.parser = self._auto_detect_parser()

    def _auto_detect_parser(self) -> Optional[BaseParser]:
        """Auto-detect appropriate parser based on log content"""
        # This will be enhanced to actually detect based on log content
        # For now, we'll import available parsers dynamically
        try:
            from ..parsers.ostris import OstrisParser
            return OstrisParser(self.log_path)
        except ImportError:
            logger.warning("No specific parser found, using base parser")
            return BaseParser(self.log_path)

    def start(self) -> None:
        """Start monitoring"""
        if self.running:
            logger.warning("Monitor already running")
            return

        if not self.parser:
            raise ValueError("No parser configured")

        self.running = True
        self.stop_event.clear()

        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        logger.info(f"Started monitoring {self.log_path}")

    def stop(self) -> None:
        """Stop monitoring"""
        if not self.running:
            return

        self.running = False
        self.stop_event.set()

        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)

        # Close parser
        if self.parser:
            self.parser.close_file()

        logger.info("Stopped monitoring")

    def _monitor_loop(self) -> None:
        """Main monitoring loop"""
        while self.running and not self.stop_event.is_set():
            try:
                # Read new lines from log
                new_lines = self.parser.tail_file()

                # Parse metrics from new lines
                for line in new_lines:
                    metrics = self.parser.parse_line(line)
                    if metrics:
                        self._process_metrics(metrics)

                # Perform analysis periodically
                if self.data_manager.metrics['loss']:
                    self._perform_analysis()

            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                self._trigger_callbacks('on_error', str(e))

            # Wait for next update
            self.stop_event.wait(self.update_interval)

    def _process_metrics(self, metrics: Dict[str, Any]) -> None:
        """Process new metrics"""
        # Add to data manager
        self.data_manager.add_metrics(metrics)

        # Trigger callbacks
        self._trigger_callbacks('on_metrics', metrics)

    def _perform_analysis(self) -> None:
        """Perform analysis on current data"""
        # Get data for analysis
        loss_history = list(self.data_manager.metrics['loss'])
        lr_history = list(self.data_manager.metrics['lr']) if self.data_manager.metrics['lr'] else None
        steps = list(self.data_manager.metrics['step']) if self.data_manager.metrics['step'] else None

        # Analyze
        analysis = self.analyzer.analyze(loss_history, lr_history, steps)

        # Add statistics from data manager
        analysis['statistics'].update(self.data_manager.get_statistics())

        # Trigger callbacks
        self._trigger_callbacks('on_analysis', analysis)

    def register_callback(self, event: str, callback: callable) -> None:
        """
        Register a callback for an event

        Args:
            event: Event name ('on_metrics', 'on_analysis', 'on_error')
            callback: Callback function
        """
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    def unregister_callback(self, event: str, callback: callable) -> None:
        """Unregister a callback"""
        if event in self.callbacks and callback in self.callbacks[event]:
            self.callbacks[event].remove(callback)

    def _trigger_callbacks(self, event: str, data: Any) -> None:
        """Trigger all callbacks for an event"""
        for callback in self.callbacks.get(event, []):
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Error in callback: {e}")

    def get_current_data(self) -> Dict[str, Any]:
        """Get current data and analysis"""
        return {
            'metrics': self.data_manager.get_latest_metrics(),
            'statistics': self.data_manager.get_statistics(),
            'analysis': self.analyzer.analyze(
                list(self.data_manager.metrics['loss']),
                list(self.data_manager.metrics['lr']) if self.data_manager.metrics['lr'] else None,
                list(self.data_manager.metrics['step']) if self.data_manager.metrics['step'] else None,
            ),
        }

    def export_data(self, filepath: str) -> None:
        """Export data to CSV"""
        self.data_manager.export_to_csv(filepath)

    def clear_data(self) -> None:
        """Clear all stored data"""
        self.data_manager.clear_data()

    def set_parser(self, parser: BaseParser) -> None:
        """Set a new parser"""
        if self.running:
            raise RuntimeError("Cannot change parser while monitoring")
        self.parser = parser

    def set_log_path(self, log_path: Path) -> None:
        """Set a new log path"""
        if self.running:
            raise RuntimeError("Cannot change log path while monitoring")
        self.log_path = Path(log_path)
        if self.parser:
            self.parser.log_path = self.log_path