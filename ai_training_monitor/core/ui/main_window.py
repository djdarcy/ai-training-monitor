"""
Main window for AI Training Monitor application
"""
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QFileDialog, QMenuBar, QMenu,
                            QStatusBar, QSplitter, QMessageBox, QLineEdit,
                            QComboBox, QLabel, QToolBar, QSpinBox, QTabWidget)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QKeySequence

from .graphs import MultiGraphWidget
from .omni_graph import OmniGraphPanel
from .status_panel import StatusPanel
from .interactive_status_panel import InteractiveStatusPanel
from ..monitor import TrainingMonitor
from ...parsers.ostris import OstrisParser


class MonitorThread(QThread):
    """Thread for running the training monitor"""

    metrics_updated = pyqtSignal(dict)
    analysis_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, monitor: TrainingMonitor):
        super().__init__()
        self.monitor = monitor

        # Connect callbacks
        self.monitor.register_callback('on_metrics', self.on_metrics)
        self.monitor.register_callback('on_analysis', self.on_analysis)
        self.monitor.register_callback('on_error', self.on_error)

    def on_metrics(self, metrics):
        self.metrics_updated.emit(metrics)

    def on_analysis(self, analysis):
        self.analysis_updated.emit(analysis)

    def on_error(self, error):
        self.error_occurred.emit(error)

    def run(self):
        self.monitor.start()

    def stop(self):
        self.monitor.stop()


class TrainingMonitorWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()

        self.monitor = None
        self.monitor_thread = None
        self.start_time = None
        self.update_timer = QTimer()

        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_connections()

    def _setup_ui(self):
        """Set up the user interface"""
        self.setWindowTitle("AI Training Monitor")
        self.setGeometry(100, 100, 1400, 900)

        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                border: 1px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4c4c4c;
            }
            QPushButton:pressed {
                background-color: #2c2c2c;
            }
            QLineEdit, QComboBox {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 3px;
            }
        """)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Control panel
        control_panel = self._create_control_panel()
        main_layout.addWidget(control_panel)

        # Create splitter for graphs and status
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Create tab widget for dual-mode view
        self.graph_tabs = QTabWidget()
        self.graph_tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.graph_tabs.setDocumentMode(False)  # Make tabs more visible

        # Style tabs to stand out
        self.graph_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #555;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #3c3c3c;
                color: #888;
                padding: 8px 16px;
                margin-right: 2px;
                border: 1px solid #555;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #4a90e2;
                color: white;
                border-color: #4a90e2;
            }
            QTabBar::tab:hover {
                background-color: #4c4c4c;
                color: white;
            }
        """)

        # Individual view tab
        self.graph_widget = MultiGraphWidget()
        self.graph_tabs.addTab(self.graph_widget, "Individual")

        # Initialize zones and default thresholds for individual graphs
        self.graph_widget.set_zones('loss')
        self.graph_widget.set_zones('speed')
        self.graph_widget.update_all_thresholds({
            'loss': 0.05,
            'lr': 1e-4,
            'speed': 5.0
        })

        # Omni view tab
        self.omni_graph = OmniGraphPanel()
        self.graph_tabs.addTab(self.omni_graph, "Omni")

        # Add tabs to splitter
        splitter.addWidget(self.graph_tabs)

        # Interactive status panel on the right
        self.status_panel = InteractiveStatusPanel()
        splitter.addWidget(self.status_panel)

        # Connect status panel signals
        self.status_panel.threshold_changed.connect(self.on_threshold_changed)
        self.status_panel.toggle_monitoring.connect(self.on_monitoring_toggled)
        self.status_panel.setting_changed.connect(self.on_setting_changed)

        # Set splitter sizes (70% graphs, 30% status)
        splitter.setSizes([980, 420])

        main_layout.addWidget(splitter)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _create_control_panel(self) -> QWidget:
        """Create the control panel"""
        panel = QWidget()
        layout = QHBoxLayout(panel)

        # File selection
        layout.addWidget(QLabel("Log:"))
        self.log_path_edit = QLineEdit()
        self.log_path_edit.setPlaceholderText("Select log file or directory...")
        layout.addWidget(self.log_path_edit, stretch=2)

        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_log)
        layout.addWidget(self.browse_btn)

        # Framework selector
        layout.addWidget(QLabel("Framework:"))
        self.framework_combo = QComboBox()
        self.framework_combo.addItems(["Auto-detect", "Ostris", "Kohya", "HuggingFace", "PyTorch"])
        layout.addWidget(self.framework_combo)

        # Update interval
        layout.addWidget(QLabel("Update (ms):"))
        self.update_spin = QSpinBox()
        self.update_spin.setRange(100, 5000)
        self.update_spin.setValue(1000)
        self.update_spin.setSingleStep(100)
        layout.addWidget(self.update_spin)

        # Control buttons
        self.start_btn = QPushButton("Start Monitoring")
        self.start_btn.clicked.connect(self.toggle_monitoring)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a5a2a;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a6a3a;
            }
        """)
        layout.addWidget(self.start_btn)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_data)
        layout.addWidget(self.clear_btn)

        return panel

    def _setup_menu(self):
        """Set up menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        open_action = QAction("Open Log...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.browse_log)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        export_action = QAction("Export Data...", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("View")

        # Graph mode submenu
        mode_menu = view_menu.addMenu("Graph Mode")

        individual_mode = QAction("Individual", self)
        individual_mode.setCheckable(True)
        individual_mode.setChecked(True)
        individual_mode.triggered.connect(lambda: self.graph_tabs.setCurrentIndex(0))
        mode_menu.addAction(individual_mode)

        omni_mode = QAction("Omni", self)
        omni_mode.setCheckable(True)
        omni_mode.triggered.connect(lambda: self.graph_tabs.setCurrentIndex(1))
        mode_menu.addAction(omni_mode)

        view_menu.addSeparator()

        clear_action = QAction("Clear All", self)
        clear_action.triggered.connect(self.clear_data)
        view_menu.addAction(clear_action)

        view_menu.addSeparator()

        theme_menu = view_menu.addMenu("Theme")
        dark_theme = QAction("Dark", self)
        dark_theme.setCheckable(True)
        dark_theme.setChecked(True)
        theme_menu.addAction(dark_theme)

        light_theme = QAction("Light", self)
        light_theme.setCheckable(True)
        theme_menu.addAction(light_theme)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _setup_toolbar(self):
        """Set up toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Add actions to toolbar
        start_action = QAction("▶", self)
        start_action.setToolTip("Start/Stop Monitoring")
        start_action.triggered.connect(self.toggle_monitoring)
        toolbar.addAction(start_action)

        toolbar.addSeparator()

        clear_action = QAction("🗑", self)
        clear_action.setToolTip("Clear Data")
        clear_action.triggered.connect(self.clear_data)
        toolbar.addAction(clear_action)

        export_action = QAction("💾", self)
        export_action.setToolTip("Export Data")
        export_action.triggered.connect(self.export_data)
        toolbar.addAction(export_action)

    def _setup_connections(self):
        """Set up signal connections"""
        self.update_timer.timeout.connect(self.update_display)

    def browse_log(self):
        """Browse for log file or directory"""
        path = QFileDialog.getOpenFileName(
            self,
            "Select Log File",
            "",
            "Log Files (*.log *.txt);;All Files (*.*)"
        )

        if path[0]:
            self.log_path_edit.setText(path[0])

    def toggle_monitoring(self):
        """Start or stop monitoring"""
        if self.monitor and self.monitor.running:
            self.stop_monitoring()
        else:
            self.start_monitoring()

    def start_monitoring(self):
        """Start monitoring"""
        log_path = self.log_path_edit.text()
        if not log_path:
            QMessageBox.warning(self, "No Log File", "Please select a log file to monitor")
            return

        try:
            # Create parser based on framework selection
            framework = self.framework_combo.currentText()
            if framework == "Auto-detect" or framework == "Ostris":
                parser = OstrisParser(Path(log_path))
            else:
                # Add other parsers as they're implemented
                parser = OstrisParser(Path(log_path))

            # Create monitor
            self.monitor = TrainingMonitor(
                log_path=Path(log_path),
                parser=parser,
                update_interval=self.update_spin.value() / 1000.0
            )

            # Create and start monitor thread
            self.monitor_thread = MonitorThread(self.monitor)
            self.monitor_thread.metrics_updated.connect(self.on_metrics_update)
            self.monitor_thread.analysis_updated.connect(self.on_analysis_update)
            self.monitor_thread.error_occurred.connect(self.on_error)
            self.monitor_thread.start()

            # Start display update timer
            self.start_time = datetime.now()
            self.update_timer.start(100)  # Update display every 100ms

            # Update UI
            self.start_btn.setText("Stop Monitoring")
            self.start_btn.setStyleSheet("""
                QPushButton {
                    background-color: #5a2a2a;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #6a3a3a;
                }
            """)
            self.status_bar.showMessage("Monitoring...")
            self.log_path_edit.setEnabled(False)
            self.framework_combo.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start monitoring: {e}")

    def stop_monitoring(self):
        """Stop monitoring"""
        if self.monitor_thread:
            self.monitor_thread.stop()
            self.monitor_thread.wait()
            self.monitor_thread = None

        if self.monitor:
            self.monitor.stop()
            self.monitor = None

        self.update_timer.stop()

        # Update UI
        self.start_btn.setText("Start Monitoring")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a5a2a;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a6a3a;
            }
        """)
        self.status_bar.showMessage("Ready")
        self.log_path_edit.setEnabled(True)
        self.framework_combo.setEnabled(True)

    def on_metrics_update(self, metrics):
        """Handle metrics update from monitor"""
        # Update status panel
        self.status_panel.update_metrics(metrics)

        # Update both graph views
        if self.monitor:
            data = self.monitor.data_manager

            # Update Individual view graphs
            if data.metrics['loss']:
                steps = list(data.metrics['step']) if data.metrics['step'] else list(range(len(data.metrics['loss'])))
                self.graph_widget.update_graph('loss', steps, list(data.metrics['loss']))

            if data.metrics['lr']:
                steps = list(data.metrics['step']) if data.metrics['step'] else list(range(len(data.metrics['lr'])))
                self.graph_widget.update_graph('lr', steps, list(data.metrics['lr']))

            if data.metrics['speed']:
                steps = list(data.metrics['step']) if data.metrics['step'] else list(range(len(data.metrics['speed'])))
                self.graph_widget.update_graph('speed', steps, list(data.metrics['speed']))

            # Update Omni view with latest metrics
            self.omni_graph.update_data(metrics)

    def on_analysis_update(self, analysis):
        """Handle analysis update from monitor"""
        self.status_panel.update_analysis(analysis)

    def on_error(self, error):
        """Handle error from monitor"""
        self.status_bar.showMessage(f"Error: {error}")

    def update_display(self):
        """Update time display"""
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            elapsed_str = str(elapsed).split('.')[0]  # Remove microseconds
            self.status_panel.update_time(elapsed_str)

    def clear_data(self):
        """Clear all data"""
        if self.monitor:
            self.monitor.clear_data()
        self.graph_widget.clear_all()
        self.omni_graph.clear()
        self.status_panel.clear_all()
        self.status_bar.showMessage("Data cleared")

    def export_data(self):
        """Export data to CSV"""
        if not self.monitor:
            QMessageBox.information(self, "No Data", "No data to export")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Data",
            f"training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv);;All Files (*.*)"
        )

        if filepath:
            try:
                self.monitor.export_data(filepath)
                QMessageBox.information(self, "Export Complete", f"Data exported to {filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export data: {e}")

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About AI Training Monitor",
            "AI Training Monitor v0.1.0\n\n"
            "A universal real-time training monitor for AI/ML frameworks.\n\n"
            "Like Process Explorer for AI training!"
        )

    def on_threshold_changed(self, metric: str, value: float):
        """Handle threshold change from status panel"""
        # Update Omni graph thresholds
        self.omni_graph.graph.set_threshold(metric, value)

        # Update Individual graph thresholds
        self.graph_widget.update_all_thresholds({metric: value})

        self.status_bar.showMessage(f"Updated {metric} threshold to {value}")

    def on_monitoring_toggled(self, feature: str, enabled: bool):
        """Handle monitoring feature toggle"""
        state = "enabled" if enabled else "disabled"
        self.status_bar.showMessage(f"{feature} monitoring {state}")

        # Handle time verification toggle for omni graph
        if feature == 'time_verify':
            self.omni_graph.graph.set_metric_enabled('time_blip', enabled)

    def on_setting_changed(self, setting: str, value):
        """Handle setting change from status panel"""
        if setting == 'paused':
            if value:
                self.update_timer.stop()
                self.status_bar.showMessage("Monitoring paused")
            else:
                self.update_timer.start(100)
                self.status_bar.showMessage("Monitoring resumed")
        elif setting == 'update_rate' and self.monitor:
            self.monitor.update_interval = value / 1000.0
            self.status_bar.showMessage(f"Update rate set to {value}ms")
        elif setting == 'snapshot':
            self.take_snapshot()
        elif setting == 'export':
            self.export_data()

    def take_snapshot(self):
        """Take a snapshot of current state"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.status_bar.showMessage(f"Snapshot taken at {timestamp}")
        # TODO: Implement actual snapshot functionality

    def closeEvent(self, event):
        """Handle window close"""
        if self.monitor and self.monitor.running:
            self.stop_monitoring()
        event.accept()