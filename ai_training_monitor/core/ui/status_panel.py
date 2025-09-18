"""
Status panel showing training metrics and analysis
"""
from PyQt6.QtWidgets import (QWidget, QGridLayout, QLabel, QGroupBox,
                            QVBoxLayout, QHBoxLayout, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor
from typing import Dict, Any, Optional


class StatusPanel(QWidget):
    """Panel displaying current training status and metrics"""

    def __init__(self, parent=None):
        """Initialize status panel"""
        super().__init__(parent)

        self.labels = {}
        self.values = {}

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Training Status Group
        status_group = QGroupBox("Training Status")
        status_layout = QGridLayout()

        # Create status items
        status_items = [
            ("Step", "0/0", 0, 0),
            ("Epoch", "0", 0, 2),
            ("Progress", None, 1, 0),  # Progress bar
            ("Time Elapsed", "00:00:00", 2, 0),
            ("ETA", "--:--:--", 2, 2),
            ("Status", "Not Started", 3, 0),
        ]

        for item in status_items:
            if len(item) == 4:
                label_text, default, row, col = item

                label = QLabel(f"{label_text}:")
                label.setStyleSheet("font-weight: bold;")
                status_layout.addWidget(label, row, col)

                if label_text == "Progress":
                    # Create progress bar
                    progress = QProgressBar()
                    progress.setRange(0, 100)
                    progress.setValue(0)
                    progress.setTextVisible(True)
                    status_layout.addWidget(progress, row, col + 1, 1, 3)
                    self.values["progress"] = progress
                else:
                    value_label = QLabel(default)
                    status_layout.addWidget(value_label, row, col + 1)
                    self.values[label_text.lower().replace(" ", "_")] = value_label

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # Metrics Group
        metrics_group = QGroupBox("Current Metrics")
        metrics_layout = QGridLayout()

        metrics_items = [
            ("Loss", "-.----", 0, 0),
            ("Learning Rate", "-.--e--", 0, 2),
            ("Speed", "--.-- s/it", 1, 0),
            ("GPU Memory", "--/-- GB", 1, 2),
            ("Mean Loss", "-.----", 2, 0),
            ("Loss Std", "-.----", 2, 2),
        ]

        for label_text, default, row, col in metrics_items:
            label = QLabel(f"{label_text}:")
            label.setStyleSheet("font-weight: bold;")
            metrics_layout.addWidget(label, row, col)

            value_label = QLabel(default)
            metrics_layout.addWidget(value_label, row, col + 1)
            self.values[label_text.lower().replace(" ", "_")] = value_label

        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)

        # Analysis Group
        analysis_group = QGroupBox("Analysis")
        analysis_layout = QVBoxLayout()

        # Health indicator
        health_layout = QHBoxLayout()
        health_label = QLabel("Health:")
        health_label.setStyleSheet("font-weight: bold;")
        health_layout.addWidget(health_label)

        self.health_indicator = QLabel("●")
        self.health_indicator.setStyleSheet("color: gray; font-size: 20px;")
        health_layout.addWidget(self.health_indicator)

        self.health_text = QLabel("Unknown")
        health_layout.addWidget(self.health_text)
        health_layout.addStretch()

        analysis_layout.addLayout(health_layout)

        # Recommendation
        rec_label = QLabel("Recommendation:")
        rec_label.setStyleSheet("font-weight: bold;")
        analysis_layout.addWidget(rec_label)

        self.recommendation = QLabel("Waiting for data...")
        self.recommendation.setWordWrap(True)
        self.recommendation.setStyleSheet("padding: 5px; background-color: #2b2b2b; border-radius: 3px;")
        analysis_layout.addWidget(self.recommendation)

        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)

        # Add stretch to push everything to top
        layout.addStretch()

    def update_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Update displayed metrics

        Args:
            metrics: Dictionary of metric values
        """
        # Update step counter
        if 'current_step' in metrics and 'total_steps' in metrics:
            self.values['step'].setText(f"{metrics['current_step']}/{metrics['total_steps']}")

            # Update progress bar
            if metrics['total_steps'] > 0:
                progress = (metrics['current_step'] / metrics['total_steps']) * 100
                self.values['progress'].setValue(int(progress))

        # Update individual metrics
        if 'loss' in metrics:
            self.values['loss'].setText(f"{metrics['loss']:.4f}")

        if 'lr' in metrics:
            self.values['learning_rate'].setText(f"{metrics['lr']:.2e}")

        if 'speed' in metrics:
            self.values['speed'].setText(f"{metrics['speed']:.2f} s/it")

        if 'gpu_used' in metrics and 'gpu_total' in metrics:
            self.values['gpu_memory'].setText(f"{metrics['gpu_used']:.1f}/{metrics['gpu_total']:.1f} GB")

        if 'epoch' in metrics:
            self.values['epoch'].setText(str(metrics['epoch']))

    def update_analysis(self, analysis: Dict[str, Any]) -> None:
        """
        Update analysis display

        Args:
            analysis: Analysis results from MetricsAnalyzer
        """
        # Update status
        if 'status' in analysis:
            self.values['status'].setText(analysis['status'])

        # Update health indicator
        if 'health' in analysis:
            health = analysis['health']
            colors = {
                'good': '#00FF00',
                'warning': '#FFA500',
                'critical': '#FF0000',
                'neutral': '#808080',
            }
            color = colors.get(health, '#808080')
            self.health_indicator.setStyleSheet(f"color: {color}; font-size: 20px;")

            # Update health text
            health_text = {
                'good': 'Healthy',
                'warning': 'Warning',
                'critical': 'Critical',
                'neutral': 'Unknown',
            }.get(health, 'Unknown')
            self.health_text.setText(health_text)

        # Update recommendation
        if 'recommendation' in analysis:
            self.recommendation.setText(analysis['recommendation'])

        # Update statistics
        if 'statistics' in analysis:
            stats = analysis['statistics']

            if 'loss' in stats and isinstance(stats['loss'], dict):
                if 'mean' in stats['loss']:
                    self.values['mean_loss'].setText(f"{stats['loss']['mean']:.4f}")
                if 'std' in stats['loss']:
                    self.values['loss_std'].setText(f"{stats['loss']['std']:.4f}")

    def update_time(self, elapsed: str, eta: Optional[str] = None) -> None:
        """
        Update time displays

        Args:
            elapsed: Elapsed time string
            eta: Estimated time to completion
        """
        self.values['time_elapsed'].setText(elapsed)
        if eta:
            self.values['eta'].setText(eta)
        else:
            self.values['eta'].setText("--:--:--")

    def clear_all(self) -> None:
        """Clear all displays"""
        # Reset all value labels
        for key, widget in self.values.items():
            if isinstance(widget, QLabel):
                if 'loss' in key or 'rate' in key:
                    widget.setText("-.----")
                elif key == 'step':
                    widget.setText("0/0")
                elif key == 'status':
                    widget.setText("Not Started")
                else:
                    widget.setText("--")
            elif isinstance(widget, QProgressBar):
                widget.setValue(0)

        # Reset health indicator
        self.health_indicator.setStyleSheet("color: gray; font-size: 20px;")
        self.health_text.setText("Unknown")
        self.recommendation.setText("Waiting for data...")