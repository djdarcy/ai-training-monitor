"""
Interactive status panel with control center features
"""
from PyQt6.QtWidgets import (QWidget, QGridLayout, QLabel, QGroupBox,
                            QVBoxLayout, QHBoxLayout, QProgressBar,
                            QPushButton, QSlider, QCheckBox, QSpinBox,
                            QDoubleSpinBox, QComboBox, QLineEdit)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor
from typing import Dict, Any, Optional


class InteractiveStatusPanel(QWidget):
    """Enhanced status panel with interactive controls"""

    # Signals for control changes
    threshold_changed = pyqtSignal(str, float)  # metric, value
    toggle_monitoring = pyqtSignal(str, bool)  # feature, enabled
    setting_changed = pyqtSignal(str, object)  # setting, value

    def __init__(self, parent=None):
        """Initialize interactive status panel"""
        super().__init__(parent)

        self.labels = {}
        self.values = {}
        self.controls = {}
        self.thresholds = {
            'loss': 0.05,
            'lr': 1e-4,
            'speed': 5.0
        }

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI with interactive controls"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Training Status Group (unchanged from original)
        status_group = self._create_status_group()
        layout.addWidget(status_group)

        # Interactive Metrics Group (enhanced)
        metrics_group = self._create_interactive_metrics_group()
        layout.addWidget(metrics_group)

        # Control Center Group (new)
        control_group = self._create_control_center()
        layout.addWidget(control_group)

        # Analysis Group (enhanced with controls)
        analysis_group = self._create_analysis_group()
        layout.addWidget(analysis_group)

        # Add stretch to push everything to top
        layout.addStretch()

    def _create_status_group(self) -> QGroupBox:
        """Create the training status group"""
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
        return status_group

    def _create_interactive_metrics_group(self) -> QGroupBox:
        """Create metrics group with threshold controls"""
        metrics_group = QGroupBox("Metrics & Thresholds")
        metrics_layout = QGridLayout()

        # Loss with threshold control
        row = 0
        label = QLabel("Loss:")
        label.setStyleSheet("font-weight: bold;")
        metrics_layout.addWidget(label, row, 0)

        self.values['loss'] = QLabel("-.----")
        metrics_layout.addWidget(self.values['loss'], row, 1)

        loss_threshold = QDoubleSpinBox()
        loss_threshold.setRange(0.001, 10.0)
        loss_threshold.setSingleStep(0.01)
        loss_threshold.setValue(self.thresholds['loss'])
        loss_threshold.setPrefix("⚠ ")
        loss_threshold.setToolTip("Alert threshold for loss")
        loss_threshold.valueChanged.connect(lambda v: self.threshold_changed.emit('loss', v))
        metrics_layout.addWidget(loss_threshold, row, 2)
        self.controls['loss_threshold'] = loss_threshold

        # Learning Rate with threshold
        row = 1
        label = QLabel("Learning Rate:")
        label.setStyleSheet("font-weight: bold;")
        metrics_layout.addWidget(label, row, 0)

        self.values['learning_rate'] = QLabel("-.--e--")
        metrics_layout.addWidget(self.values['learning_rate'], row, 1)

        lr_threshold = QDoubleSpinBox()
        lr_threshold.setRange(1e-8, 1.0)
        lr_threshold.setSingleStep(1e-5)
        lr_threshold.setValue(self.thresholds['lr'])
        lr_threshold.setDecimals(8)
        lr_threshold.setPrefix("⚠ ")
        lr_threshold.setToolTip("Alert threshold for learning rate")
        lr_threshold.valueChanged.connect(lambda v: self.threshold_changed.emit('lr', v))
        metrics_layout.addWidget(lr_threshold, row, 2)
        self.controls['lr_threshold'] = lr_threshold

        # Speed with threshold
        row = 2
        label = QLabel("Speed:")
        label.setStyleSheet("font-weight: bold;")
        metrics_layout.addWidget(label, row, 0)

        self.values['speed'] = QLabel("--.-- s/it")
        metrics_layout.addWidget(self.values['speed'], row, 1)

        speed_threshold = QDoubleSpinBox()
        speed_threshold.setRange(0.1, 100.0)
        speed_threshold.setSingleStep(1.0)
        speed_threshold.setValue(self.thresholds['speed'])
        speed_threshold.setPrefix("⚠ ")
        speed_threshold.setSuffix(" s/it")
        speed_threshold.setToolTip("Alert threshold for training speed")
        speed_threshold.valueChanged.connect(lambda v: self.threshold_changed.emit('speed', v))
        metrics_layout.addWidget(speed_threshold, row, 2)
        self.controls['speed_threshold'] = speed_threshold

        # GPU Memory
        row = 3
        label = QLabel("GPU Memory:")
        label.setStyleSheet("font-weight: bold;")
        metrics_layout.addWidget(label, row, 0)

        self.values['gpu_memory'] = QLabel("--/-- GB")
        metrics_layout.addWidget(self.values['gpu_memory'], row, 1)

        # Statistics
        row = 4
        label = QLabel("Mean Loss:")
        label.setStyleSheet("font-weight: bold;")
        metrics_layout.addWidget(label, row, 0)

        self.values['mean_loss'] = QLabel("-.----")
        metrics_layout.addWidget(self.values['mean_loss'], row, 1)

        label = QLabel("Std:")
        metrics_layout.addWidget(label, row, 2)

        self.values['loss_std'] = QLabel("-.----")
        metrics_layout.addWidget(self.values['loss_std'], row, 3)

        metrics_group.setLayout(metrics_layout)
        return metrics_group

    def _create_control_center(self) -> QGroupBox:
        """Create control center with toggles and settings"""
        control_group = QGroupBox("Control Center")
        control_layout = QVBoxLayout()

        # Monitoring toggles
        toggle_layout = QGridLayout()

        # Pattern detection toggles
        self.overfitting_check = QCheckBox("Overfitting Detection")
        self.overfitting_check.setChecked(True)
        self.overfitting_check.toggled.connect(
            lambda c: self.toggle_monitoring.emit('overfitting', c)
        )
        toggle_layout.addWidget(self.overfitting_check, 0, 0)

        self.plateau_check = QCheckBox("Plateau Detection")
        self.plateau_check.setChecked(True)
        self.plateau_check.toggled.connect(
            lambda c: self.toggle_monitoring.emit('plateau', c)
        )
        toggle_layout.addWidget(self.plateau_check, 0, 1)

        self.divergence_check = QCheckBox("Divergence Detection")
        self.divergence_check.setChecked(True)
        self.divergence_check.toggled.connect(
            lambda c: self.toggle_monitoring.emit('divergence', c)
        )
        toggle_layout.addWidget(self.divergence_check, 1, 0)

        self.time_verify_check = QCheckBox("Time Verification")
        self.time_verify_check.setChecked(False)
        self.time_verify_check.toggled.connect(
            lambda c: self.toggle_monitoring.emit('time_verify', c)
        )
        toggle_layout.addWidget(self.time_verify_check, 1, 1)

        control_layout.addLayout(toggle_layout)

        # Settings controls
        settings_layout = QHBoxLayout()

        # Window size control
        settings_layout.addWidget(QLabel("Window:"))
        window_spin = QSpinBox()
        window_spin.setRange(100, 10000)
        window_spin.setSingleStep(100)
        window_spin.setValue(1000)
        window_spin.setSuffix(" points")
        window_spin.setToolTip("Analysis window size")
        window_spin.valueChanged.connect(lambda v: self.setting_changed.emit('window_size', v))
        settings_layout.addWidget(window_spin)
        self.controls['window_size'] = window_spin

        # Update rate control
        settings_layout.addWidget(QLabel("Update:"))
        update_spin = QSpinBox()
        update_spin.setRange(100, 5000)
        update_spin.setSingleStep(100)
        update_spin.setValue(1000)
        update_spin.setSuffix(" ms")
        update_spin.setToolTip("Update interval")
        update_spin.valueChanged.connect(lambda v: self.setting_changed.emit('update_rate', v))
        settings_layout.addWidget(update_spin)
        self.controls['update_rate'] = update_spin

        control_layout.addLayout(settings_layout)

        # Action buttons
        button_layout = QHBoxLayout()

        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.setCheckable(True)
        self.pause_btn.clicked.connect(self._on_pause_clicked)
        button_layout.addWidget(self.pause_btn)

        self.snapshot_btn = QPushButton("📷 Snapshot")
        self.snapshot_btn.clicked.connect(lambda: self.setting_changed.emit('snapshot', True))
        button_layout.addWidget(self.snapshot_btn)

        self.export_btn = QPushButton("💾 Export")
        self.export_btn.clicked.connect(lambda: self.setting_changed.emit('export', True))
        button_layout.addWidget(self.export_btn)

        control_layout.addLayout(button_layout)

        control_group.setLayout(control_layout)
        return control_group

    def _create_analysis_group(self) -> QGroupBox:
        """Create analysis group with enhanced controls"""
        analysis_group = QGroupBox("Analysis")
        analysis_layout = QVBoxLayout()

        # Health indicator with threshold adjustment
        health_layout = QHBoxLayout()
        health_label = QLabel("Health:")
        health_label.setStyleSheet("font-weight: bold;")
        health_layout.addWidget(health_label)

        self.health_indicator = QLabel("●")
        self.health_indicator.setStyleSheet("color: gray; font-size: 20px;")
        health_layout.addWidget(self.health_indicator)

        self.health_text = QLabel("Unknown")
        health_layout.addWidget(self.health_text)

        # Alert mode selector
        self.alert_combo = QComboBox()
        self.alert_combo.addItems(["Auto", "Strict", "Relaxed", "Custom"])
        self.alert_combo.setToolTip("Alert sensitivity mode")
        self.alert_combo.currentTextChanged.connect(
            lambda t: self.setting_changed.emit('alert_mode', t)
        )
        health_layout.addWidget(self.alert_combo)
        health_layout.addStretch()

        analysis_layout.addLayout(health_layout)

        # Recommendation with action buttons
        rec_layout = QVBoxLayout()

        rec_label = QLabel("Recommendation:")
        rec_label.setStyleSheet("font-weight: bold;")
        rec_layout.addWidget(rec_label)

        self.recommendation = QLabel("Waiting for data...")
        self.recommendation.setWordWrap(True)
        self.recommendation.setStyleSheet("padding: 5px; background-color: #2b2b2b; border-radius: 3px;")
        rec_layout.addWidget(self.recommendation)

        # Action buttons for recommendations
        rec_action_layout = QHBoxLayout()

        self.apply_rec_btn = QPushButton("Apply")
        self.apply_rec_btn.setEnabled(False)
        self.apply_rec_btn.clicked.connect(self._apply_recommendation)
        rec_action_layout.addWidget(self.apply_rec_btn)

        self.dismiss_rec_btn = QPushButton("Dismiss")
        self.dismiss_rec_btn.clicked.connect(self._dismiss_recommendation)
        rec_action_layout.addWidget(self.dismiss_rec_btn)

        rec_action_layout.addStretch()
        rec_layout.addLayout(rec_action_layout)

        analysis_layout.addLayout(rec_layout)

        analysis_group.setLayout(analysis_layout)
        return analysis_group

    def _on_pause_clicked(self):
        """Handle pause button click"""
        if self.pause_btn.isChecked():
            self.pause_btn.setText("▶ Resume")
            self.setting_changed.emit('paused', True)
        else:
            self.pause_btn.setText("⏸ Pause")
            self.setting_changed.emit('paused', False)

    def _apply_recommendation(self):
        """Apply the current recommendation"""
        # This would emit a signal with the recommendation action
        self.setting_changed.emit('apply_recommendation', True)
        self.apply_rec_btn.setEnabled(False)

    def _dismiss_recommendation(self):
        """Dismiss the current recommendation"""
        self.recommendation.setText("Monitoring...")
        self.apply_rec_btn.setEnabled(False)

    def update_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Update displayed metrics and check thresholds

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

        # Update individual metrics with threshold checking
        if 'loss' in metrics:
            loss_val = metrics['loss']
            self.values['loss'].setText(f"{loss_val:.4f}")

            # Check threshold
            if loss_val > self.thresholds['loss']:
                self.values['loss'].setStyleSheet("color: #ff6b6b; font-weight: bold;")
            else:
                self.values['loss'].setStyleSheet("")

        if 'lr' in metrics:
            lr_val = metrics['lr']
            self.values['learning_rate'].setText(f"{lr_val:.2e}")

            # Check threshold
            if lr_val < self.thresholds['lr']:
                self.values['learning_rate'].setStyleSheet("color: #ffa500; font-weight: bold;")
            else:
                self.values['learning_rate'].setStyleSheet("")

        if 'speed' in metrics:
            speed_val = metrics['speed']
            self.values['speed'].setText(f"{speed_val:.2f} s/it")

            # Check threshold
            if speed_val > self.thresholds['speed']:
                self.values['speed'].setStyleSheet("color: #ff6b6b; font-weight: bold;")
            else:
                self.values['speed'].setStyleSheet("")

        if 'gpu_used' in metrics and 'gpu_total' in metrics:
            self.values['gpu_memory'].setText(f"{metrics['gpu_used']:.1f}/{metrics['gpu_total']:.1f} GB")

        if 'epoch' in metrics:
            self.values['epoch'].setText(str(metrics['epoch']))

    def update_analysis(self, analysis: Dict[str, Any]) -> None:
        """
        Update analysis display with interactive elements

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

        # Update recommendation with actionable status
        if 'recommendation' in analysis:
            rec_text = analysis['recommendation']
            self.recommendation.setText(rec_text)

            # Enable apply button for actionable recommendations
            actionable_keywords = ['reduce', 'increase', 'stop', 'adjust', 'change']
            if any(keyword in rec_text.lower() for keyword in actionable_keywords):
                self.apply_rec_btn.setEnabled(True)
            else:
                self.apply_rec_btn.setEnabled(False)

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

    def update_threshold(self, metric: str, value: float):
        """Update threshold value for a metric"""
        if metric in self.thresholds:
            self.thresholds[metric] = value

            # Update corresponding control
            if f'{metric}_threshold' in self.controls:
                self.controls[f'{metric}_threshold'].setValue(value)

    def clear_all(self) -> None:
        """Clear all displays"""
        # Reset all value labels
        for key, widget in self.values.items():
            if isinstance(widget, QLabel):
                if 'loss' in key or 'rate' in key:
                    widget.setText("-.----")
                    widget.setStyleSheet("")  # Clear threshold styling
                elif key == 'step':
                    widget.setText("0/0")
                elif key == 'status':
                    widget.setText("Not Started")
                elif key == 'speed':
                    widget.setText("--.-- s/it")
                    widget.setStyleSheet("")  # Clear threshold styling
                else:
                    widget.setText("--")
            elif isinstance(widget, QProgressBar):
                widget.setValue(0)

        # Reset health indicator
        self.health_indicator.setStyleSheet("color: gray; font-size: 20px;")
        self.health_text.setText("Unknown")
        self.recommendation.setText("Waiting for data...")
        self.apply_rec_btn.setEnabled(False)

        # Reset pause button
        self.pause_btn.setChecked(False)
        self.pause_btn.setText("⏸ Pause")