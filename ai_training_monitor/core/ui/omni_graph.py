"""
Omni-view graph widget for unified metrics display
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np

import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPen


class OmniGraph(pg.PlotWidget):
    """
    Unified graph widget displaying multiple metrics on a single plot
    with configurable axes and scaling modes.
    """

    def __init__(self):
        super().__init__()

        # Configure plot appearance
        self.setBackground('#1e1e1e')
        self.showGrid(x=True, y=True, alpha=0.3)
        self.setLabel('bottom', 'Step')

        # Metric configurations
        self.metrics_config = {
            'loss': {
                'color': '#ff6b6b',  # Red
                'name': 'Loss',
                'axis': 'primary',
                'enabled': True,
                'line_width': 2.0,
                'style': Qt.PenStyle.SolidLine,
                'threshold': None,  # Will be set dynamically
                'normalize': False
            },
            'lr': {
                'color': '#ffd93d',  # Yellow
                'name': 'Learning Rate',
                'axis': 'secondary',
                'enabled': True,
                'line_width': 1.5,
                'style': Qt.PenStyle.DashLine,
                'threshold': None,
                'normalize': True
            },
            'speed': {
                'color': '#6bcb77',  # Green
                'name': 'Training Speed (s/it)',
                'axis': 'secondary',
                'enabled': True,
                'line_width': 1.5,
                'style': Qt.PenStyle.SolidLine,
                'threshold': None,
                'normalize': True
            },
            'time_blip': {
                'color': '#00d4ff',  # Cyan
                'name': 'Time Verification',
                'axis': 'overlay',
                'enabled': False,  # Off by default
                'line_width': 1.0,
                'style': Qt.PenStyle.DotLine,
                'threshold': None,
                'normalize': False
            }
        }

        # Plot items for each metric
        self.plot_items = {}
        self.threshold_items = {}

        # Data storage
        self.data = {
            'step': [],
            'loss': [],
            'lr': [],
            'speed': [],
            'time_actual': [],
            'time_reported': []
        }

        # Axis management
        self.primary_axis = self.getAxis('left')
        self.primary_axis.setLabel('Loss', color='#ff6b6b')

        # Create secondary Y-axis for normalized metrics
        self.secondary_axis = pg.ViewBox()
        self.plotItem.scene().addItem(self.secondary_axis)
        self.plotItem.getAxis('right').linkToView(self.secondary_axis)
        self.secondary_axis.setXLink(self.plotItem)
        self.plotItem.getAxis('right').setLabel('Normalized Scale (0-1)', color='#888888')

        # Connect view changes
        self.plotItem.vb.sigResized.connect(self.update_views)

        # Initialize plot items
        self._initialize_plot_items()

        # Legend
        self.addLegend()

        # Zone storage
        self.zones = {}

    def _add_loss_zones(self, threshold: float):
        """Add colored zones based on loss threshold"""
        # Clear existing zones
        for zone_name in ['optimal', 'acceptable', 'warning']:
            if zone_name in self.zones:
                self.removeItem(self.zones[zone_name])
                del self.zones[zone_name]

        # Create zones relative to threshold
        # Optimal: 0 to 40% of threshold
        optimal_zone = pg.LinearRegionItem(
            values=(0, threshold * 0.4),
            orientation='horizontal',
            movable=False,
            pen=pg.mkPen(None)
        )
        optimal_zone.setBrush(pg.mkBrush(0, 255, 0, 20))  # Green with transparency
        optimal_zone.setZValue(-10)  # Put behind data
        self.addItem(optimal_zone)
        self.zones['optimal'] = optimal_zone

        # Acceptable: 40% to 100% of threshold
        acceptable_zone = pg.LinearRegionItem(
            values=(threshold * 0.4, threshold),
            orientation='horizontal',
            movable=False,
            pen=pg.mkPen(None)
        )
        acceptable_zone.setBrush(pg.mkBrush(255, 215, 0, 20))  # Gold with transparency
        acceptable_zone.setZValue(-10)
        self.addItem(acceptable_zone)
        self.zones['acceptable'] = acceptable_zone

        # Warning: threshold to 2x threshold
        warning_zone = pg.LinearRegionItem(
            values=(threshold, threshold * 2),
            orientation='horizontal',
            movable=False,
            pen=pg.mkPen(None)
        )
        warning_zone.setBrush(pg.mkBrush(255, 165, 0, 20))  # Orange with transparency
        warning_zone.setZValue(-10)
        self.addItem(warning_zone)
        self.zones['warning'] = warning_zone

    def _initialize_plot_items(self):
        """Create plot items for each metric"""
        for metric_key, config in self.metrics_config.items():
            if metric_key == 'time_blip':
                # Special handling for time verification blip
                continue

            # Create pen for this metric
            pen = pg.mkPen(
                color=config['color'],
                width=config['line_width'],
                style=config['style']
            )

            # Create plot item based on axis type
            if config['axis'] == 'primary':
                plot_item = self.plot([], [], pen=pen, name=config['name'])
            else:
                plot_item = pg.PlotCurveItem([], [], pen=pen)
                self.secondary_axis.addItem(plot_item)

            self.plot_items[metric_key] = plot_item

            # Create threshold line if needed
            if config.get('threshold') is not None:
                threshold_pen = pg.mkPen(
                    color=config['color'],
                    width=1,
                    style=Qt.PenStyle.DashDotLine
                )
                threshold_line = pg.InfiniteLine(
                    angle=0,
                    movable=False,
                    pen=threshold_pen
                )
                threshold_line.setValue(config['threshold'])

                if config['axis'] == 'primary':
                    self.addItem(threshold_line)
                else:
                    self.secondary_axis.addItem(threshold_line)

                self.threshold_items[metric_key] = threshold_line

    def update_views(self):
        """Update secondary axis view to match primary"""
        self.secondary_axis.setGeometry(self.plotItem.vb.sceneBoundingRect())
        self.secondary_axis.linkedViewChanged(self.plotItem.vb, self.secondary_axis.XAxis)

    def _refresh_axes(self):
        """Force both axes to refresh their display"""
        # Clear the axis cache and force complete recalculation
        left_axis = self.getAxis('left')

        # Force the axis to recalculate its range and ticks
        if hasattr(left_axis, '_tickLevels'):
            left_axis._tickLevels = None
        if hasattr(left_axis, '_tickSpacing'):
            left_axis._tickSpacing = None

        # Update the view to force redraw
        self.plotItem.updateGrid()
        self.plotItem.vb.update()
        left_axis.update()
        self.getAxis('right').update()

    def set_metric_enabled(self, metric: str, enabled: bool):
        """Enable or disable a specific metric"""
        if metric in self.metrics_config:
            self.metrics_config[metric]['enabled'] = enabled
            if metric in self.plot_items:
                self.plot_items[metric].setVisible(enabled)
            if metric in self.threshold_items:
                self.threshold_items[metric].setVisible(enabled)

    def set_threshold(self, metric: str, value: float):
        """Set threshold value for a metric"""
        if metric in self.metrics_config:
            self.metrics_config[metric]['threshold'] = value

            if metric not in self.threshold_items:
                # Create new threshold line with label
                threshold_pen = pg.mkPen(
                    color=self.metrics_config[metric]['color'],
                    width=1.5,
                    style=Qt.PenStyle.DashDotLine
                )
                threshold_line = pg.InfiniteLine(
                    angle=0,
                    movable=False,
                    pen=threshold_pen,
                    label=f'{metric.upper()} Threshold',
                    labelOpts={'position': 0.95, 'color': self.metrics_config[metric]['color']}
                )

                if self.metrics_config[metric]['axis'] == 'primary':
                    self.addItem(threshold_line)
                else:
                    self.secondary_axis.addItem(threshold_line)

                self.threshold_items[metric] = threshold_line

            self.threshold_items[metric].setValue(value)

            # Add zones for loss metric
            if metric == 'loss' and self.metrics_config[metric]['axis'] == 'primary':
                self._add_loss_zones(value)

    def update_data(self, metrics: Dict):
        """Update graph with new metrics data"""
        # Store raw data
        if 'step' in metrics:
            self.data['step'].append(metrics['step'])
        else:
            # Use length as step if not provided
            self.data['step'].append(len(self.data['step']))

        for key in ['loss', 'lr', 'speed']:
            if key in metrics:
                self.data[key].append(metrics[key])
            else:
                # Append None to maintain alignment
                self.data[key].append(None)

        # Handle time data for blip visualization
        if 'time_actual' in metrics and 'time_reported' in metrics:
            self.data['time_actual'].append(metrics['time_actual'])
            self.data['time_reported'].append(metrics['time_reported'])

        # Update plots
        self._update_plots()

    def _update_plots(self):
        """Update all active plot items"""
        steps = self.data['step']

        # Track if we have secondary axis data and primary data range
        has_secondary_data = False
        primary_min, primary_max = None, None

        for metric_key, plot_item in self.plot_items.items():
            if not self.metrics_config[metric_key]['enabled']:
                continue

            metric_data = self.data.get(metric_key, [])
            if not metric_data:
                continue

            # Filter out None values
            valid_indices = [i for i, v in enumerate(metric_data) if v is not None]
            if not valid_indices:
                continue

            valid_steps = [steps[i] for i in valid_indices]
            valid_values = [metric_data[i] for i in valid_indices]

            # Store original values for primary axis tracking
            original_values = list(valid_values)

            # Apply normalization ONLY for secondary axis metrics
            if self.metrics_config[metric_key]['axis'] == 'secondary' and self.metrics_config[metric_key]['normalize']:
                valid_values = self._normalize_values(valid_values)
                has_secondary_data = True
                print(f"[DEBUG] Normalized {metric_key} for secondary axis")
            elif self.metrics_config[metric_key]['axis'] == 'primary':
                # Track primary axis data range using ORIGINAL values
                if original_values:
                    primary_min = min(original_values) if primary_min is None else min(primary_min, min(original_values))
                    primary_max = max(original_values) if primary_max is None else max(primary_max, max(original_values))
                    print(f"[DEBUG] Primary metric {metric_key} range: {min(original_values):.6f} to {max(original_values):.6f}")

            # Update plot
            plot_item.setData(valid_steps, valid_values)

        # Update primary axis range if we have primary data
        if primary_min is not None and primary_max is not None:
            padding = (primary_max - primary_min) * 0.1 if primary_max != primary_min else 0.1

            print(f"[DEBUG] Updated primary Y range: {primary_min - padding:.6f} to {primary_max + padding:.6f}")

            # Force the view to update with the new range
            self.plotItem.vb.setRange(yRange=(primary_min - padding, primary_max + padding), padding=0)

        # Update secondary axis range if we have data
        if has_secondary_data:
            self.secondary_axis.setYRange(0, 1, padding=0.1)

        # Update time verification blip if enabled
        if self.metrics_config['time_blip']['enabled']:
            self._update_time_blip()

    def _normalize_values(self, values: List[float]) -> List[float]:
        """Normalize values to 0-1 range"""
        if not values:
            return values

        min_val = min(values)
        max_val = max(values)

        if max_val == min_val:
            return [0.5] * len(values)

        return [(v - min_val) / (max_val - min_val) for v in values]

    def _update_time_blip(self):
        """Update time verification blip visualization"""
        if not self.data['time_actual'] or not self.data['time_reported']:
            return

        # Calculate divergence (area under the difference curve)
        steps = self.data['step']
        actual = self.data['time_actual']
        reported = self.data['time_reported']

        # Create fill area between actual and reported
        if 'time_fill' not in self.plot_items:
            brush = pg.mkBrush(color=(0, 212, 255, 50))  # Semi-transparent cyan
            fill_item = pg.FillBetweenItem(
                curve1=pg.PlotCurveItem([]),
                curve2=pg.PlotCurveItem([]),
                brush=brush
            )
            self.addItem(fill_item)
            self.plot_items['time_fill'] = fill_item

        # Update fill curves
        # This would show the divergence between actual and reported times
        # Implementation would depend on specific time tracking data structure
        pass

    def clear(self):
        """Clear all data and plots"""
        for key in self.data:
            self.data[key] = []

        for plot_item in self.plot_items.values():
            if isinstance(plot_item, pg.PlotDataItem):
                plot_item.setData([], [])
            elif isinstance(plot_item, pg.PlotCurveItem):
                plot_item.setData([], [])

    def set_primary_metric(self, metric: str):
        """Set which metric should be on the primary (absolute) axis"""
        if metric not in self.metrics_config:
            return

        # Don't do anything if it's already the primary
        if self.metrics_config[metric]['axis'] == 'primary':
            return

        # Store current data before clearing
        stored_data = dict(self.data)

        # Clear existing plot items properly
        for plot_item in list(self.plot_items.values()):
            if isinstance(plot_item, pg.PlotDataItem):
                self.removeItem(plot_item)
            elif isinstance(plot_item, pg.PlotCurveItem):
                self.secondary_axis.removeItem(plot_item)
            elif isinstance(plot_item, pg.FillBetweenItem):
                self.removeItem(plot_item)

        # Clear threshold items
        for threshold_item in list(self.threshold_items.values()):
            try:
                self.removeItem(threshold_item)
            except:
                try:
                    self.secondary_axis.removeItem(threshold_item)
                except:
                    pass

        self.plot_items.clear()
        self.threshold_items.clear()

        # Update metric configurations
        for key, config in self.metrics_config.items():
            if config['axis'] == 'primary':
                config['axis'] = 'secondary'
                config['normalize'] = True

        self.metrics_config[metric]['axis'] = 'primary'
        self.metrics_config[metric]['normalize'] = False

        # Update axis label and scaling
        self.primary_axis.setLabel(self.metrics_config[metric]['name'],
                                    color=self.metrics_config[metric]['color'])

        # Re-initialize plot items with new axis configuration
        self._initialize_plot_items()

        # Restore data
        self.data = stored_data

        # Force update the primary axis range based on the new primary metric data
        if metric in self.data and self.data[metric]:
            valid_data = [v for v in self.data[metric] if v is not None]
            if valid_data:
                data_min = min(valid_data)
                data_max = max(valid_data)
                padding = (data_max - data_min) * 0.1 if data_max != data_min else 0.1

                print(f"[DEBUG] Set primary Y range for {metric}: {data_min - padding:.6f} to {data_max + padding:.6f}")

                # Clear auto range and set manual range
                self.plotItem.vb.enableAutoRange(axis=1, enable=False)  # Disable Y auto range
                self.plotItem.vb.setRange(yRange=(data_min - padding, data_max + padding), padding=0, update=True)

                # Force the left axis to recognize the new range
                left_axis = self.getAxis('left')
                left_axis.linkToView(self.plotItem.vb)  # Re-link to ensure connection
                left_axis.setRange(data_min - padding, data_max + padding)
        else:
            # Reset to auto range if no data
            self.enableAutoRange(y=True)

        # Set secondary axis to normalized range
        self.secondary_axis.setYRange(0, 1, padding=0.1)

        # Refresh plots with existing data
        if any(self.data[key] for key in self.data):
            self._update_plots()

        # Force axes to refresh their display
        self._refresh_axes()


class OmniGraphPanel(QWidget):
    """
    Panel containing the OmniGraph with controls for metric selection
    and configuration.
    """

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Control bar
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(5, 5, 5, 5)

        # Metric checkboxes
        control_layout.addWidget(QLabel("Metrics:"))

        self.metric_checks = {}
        for metric in ['loss', 'lr', 'speed']:
            checkbox = QCheckBox(metric.upper())
            checkbox.setChecked(True)
            checkbox.toggled.connect(lambda checked, m=metric: self.toggle_metric(m, checked))
            control_layout.addWidget(checkbox)
            self.metric_checks[metric] = checkbox

        # Time verification toggle
        control_layout.addSpacing(20)
        self.time_check = QCheckBox("Time Verification")
        self.time_check.setChecked(False)
        self.time_check.toggled.connect(lambda checked: self.toggle_metric('time_blip', checked))
        control_layout.addWidget(self.time_check)

        # Primary metric selector
        control_layout.addSpacing(20)
        control_layout.addWidget(QLabel("Primary:"))
        self.primary_btn = QPushButton("Loss")
        self.primary_btn.clicked.connect(self.select_primary_metric)
        control_layout.addWidget(self.primary_btn)

        control_layout.addStretch()

        # Add control bar to layout
        control_widget = QWidget()
        control_widget.setLayout(control_layout)
        control_widget.setMaximumHeight(40)
        layout.addWidget(control_widget)

        # Add the graph
        self.graph = OmniGraph()
        layout.addWidget(self.graph)

    def toggle_metric(self, metric: str, enabled: bool):
        """Toggle metric visibility"""
        self.graph.set_metric_enabled(metric, enabled)

    def select_primary_metric(self):
        """Open dialog to select primary metric"""
        # For now, just cycle through metrics
        current = self.primary_btn.text().lower()
        metrics = ['loss', 'lr', 'speed']

        try:
            current_idx = metrics.index(current)
            next_idx = (current_idx + 1) % len(metrics)
            next_metric = metrics[next_idx]
        except ValueError:
            next_metric = 'loss'

        self.primary_btn.setText(next_metric.upper())
        self.graph.set_primary_metric(next_metric)

    def update_data(self, metrics: Dict):
        """Forward metrics to graph"""
        self.graph.update_data(metrics)

    def clear(self):
        """Clear the graph"""
        self.graph.clear()