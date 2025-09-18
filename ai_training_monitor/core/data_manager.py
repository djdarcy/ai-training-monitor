"""
Data management for training metrics with efficient circular buffers
"""
from collections import deque
from typing import Dict, List, Optional, Any
import numpy as np
import time
from datetime import datetime
import threading


class DataManager:
    """Manages training metrics data with efficient storage and retrieval"""

    def __init__(self, max_points: int = 5000):
        """
        Initialize data manager

        Args:
            max_points: Maximum number of data points to keep in memory
        """
        self.max_points = max_points
        self.lock = threading.RLock()

        # Circular buffers for each metric
        self.metrics = {
            'timestamp': deque(maxlen=max_points),
            'step': deque(maxlen=max_points),
            'loss': deque(maxlen=max_points),
            'lr': deque(maxlen=max_points),
            'speed': deque(maxlen=max_points),
            'gpu_memory': deque(maxlen=max_points),
            'epoch': deque(maxlen=max_points),
        }

        # Additional computed metrics
        self.computed = {
            'loss_ma_10': deque(maxlen=max_points),
            'loss_ma_50': deque(maxlen=max_points),
            'loss_ma_100': deque(maxlen=max_points),
        }

        # Metadata
        self.metadata = {
            'start_time': None,
            'last_update': None,
            'total_steps': None,
            'framework': None,
        }

    def add_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Add new metrics to the data store

        Args:
            metrics: Dictionary of metric values
        """
        with self.lock:
            # Add timestamp if not present
            if 'timestamp' not in metrics:
                metrics['timestamp'] = time.time()

            # Store first timestamp
            if self.metadata['start_time'] is None:
                self.metadata['start_time'] = metrics['timestamp']

            self.metadata['last_update'] = metrics['timestamp']

            # Add metrics to buffers
            for key, buffer in self.metrics.items():
                if key in metrics:
                    buffer.append(metrics[key])

            # Update total steps if provided
            if 'total_steps' in metrics:
                self.metadata['total_steps'] = metrics['total_steps']

            # Compute moving averages for loss
            if 'loss' in metrics and len(self.metrics['loss']) > 0:
                self._compute_moving_averages()

    def _compute_moving_averages(self) -> None:
        """Compute moving averages for loss"""
        losses = list(self.metrics['loss'])

        if len(losses) >= 10:
            ma_10 = np.mean(losses[-10:])
            self.computed['loss_ma_10'].append(ma_10)

        if len(losses) >= 50:
            ma_50 = np.mean(losses[-50:])
            self.computed['loss_ma_50'].append(ma_50)

        if len(losses) >= 100:
            ma_100 = np.mean(losses[-100:])
            self.computed['loss_ma_100'].append(ma_100)

    def get_latest_metrics(self) -> Dict[str, Any]:
        """Get the most recent metrics"""
        with self.lock:
            latest = {}
            for key, buffer in self.metrics.items():
                if buffer:
                    latest[key] = buffer[-1]
            return latest

    def get_data_arrays(self, metric: str, max_points: Optional[int] = None) -> np.ndarray:
        """
        Get data as numpy array for plotting

        Args:
            metric: Metric name to retrieve
            max_points: Maximum number of points to return (from most recent)

        Returns:
            Numpy array of metric values
        """
        with self.lock:
            if metric in self.metrics:
                data = list(self.metrics[metric])
            elif metric in self.computed:
                data = list(self.computed[metric])
            else:
                return np.array([])

            if max_points and len(data) > max_points:
                data = data[-max_points:]

            return np.array(data)

    def get_time_range(self) -> tuple:
        """Get the time range of stored data"""
        with self.lock:
            if not self.metrics['timestamp']:
                return (0, 0)
            return (self.metrics['timestamp'][0], self.metrics['timestamp'][-1])

    def clear_data(self) -> None:
        """Clear all stored data"""
        with self.lock:
            for buffer in self.metrics.values():
                buffer.clear()
            for buffer in self.computed.values():
                buffer.clear()
            self.metadata['start_time'] = None
            self.metadata['last_update'] = None

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistical summary of metrics"""
        with self.lock:
            stats = {}

            # Loss statistics
            if self.metrics['loss']:
                losses = np.array(list(self.metrics['loss']))
                stats['loss'] = {
                    'current': losses[-1] if len(losses) > 0 else None,
                    'min': np.min(losses),
                    'max': np.max(losses),
                    'mean': np.mean(losses),
                    'std': np.std(losses),
                    'median': np.median(losses),
                }

            # Learning rate statistics
            if self.metrics['lr']:
                lrs = np.array(list(self.metrics['lr']))
                stats['lr'] = {
                    'current': lrs[-1] if len(lrs) > 0 else None,
                    'min': np.min(lrs),
                    'max': np.max(lrs),
                }

            # Speed statistics
            if self.metrics['speed']:
                speeds = np.array(list(self.metrics['speed']))
                stats['speed'] = {
                    'current': speeds[-1] if len(speeds) > 0 else None,
                    'mean': np.mean(speeds),
                    'min': np.min(speeds),
                    'max': np.max(speeds),
                }

            # Progress
            if self.metrics['step'] and self.metadata['total_steps']:
                current_step = self.metrics['step'][-1]
                stats['progress'] = {
                    'current_step': current_step,
                    'total_steps': self.metadata['total_steps'],
                    'percentage': (current_step / self.metadata['total_steps']) * 100,
                }

            return stats

    def export_to_csv(self, filepath: str) -> None:
        """Export data to CSV file"""
        import csv

        with self.lock:
            # Get all metric names that have data
            active_metrics = [k for k, v in self.metrics.items() if v]

            if not active_metrics:
                return

            # Get the minimum length
            min_len = min(len(self.metrics[k]) for k in active_metrics)

            with open(filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow(active_metrics)

                # Write data rows
                for i in range(min_len):
                    row = [self.metrics[k][i] for k in active_metrics]
                    writer.writerow(row)