"""
Real-time graph widgets using PyQtGraph for smooth 60 FPS visualization
"""
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import numpy as np
from typing import Optional, Dict, Any, List


# Set default PyQtGraph settings for better appearance
pg.setConfigOptions(antialias=True, useOpenGL=True)


class MetricGraph(pg.PlotWidget):
    """Single metric real-time graph with smooth updates"""

    def __init__(self, title: str = "Metric",
                 y_label: str = "Value",
                 x_label: str = "Step",
                 color: str = "#00FF00",
                 parent=None):
        """
        Initialize metric graph

        Args:
            title: Graph title
            y_label: Y-axis label
            x_label: X-axis label
            color: Line color
            parent: Parent widget
        """
        super().__init__(parent=parent)

        self.title = title
        self.color = color

        # Configure plot with visible labels
        self.setTitle(title, color='#e0e0e0', size='12pt')
        self.setLabel('left', y_label, color='#e0e0e0', units='')
        self.setLabel('bottom', x_label, color='#e0e0e0', units='')

        # Style the axes
        axis_color = '#e0e0e0'
        for axis in ['left', 'bottom', 'right', 'top']:
            self.getAxis(axis).setPen(pg.mkPen(color=axis_color, width=1))
            self.getAxis(axis).setTextPen(pg.mkPen(color=axis_color))

        self.showGrid(x=True, y=True, alpha=0.3)
        self.setBackground('#1e1e1e')

        # Create plot curves
        self.main_curve = self.plot([], [], pen=pg.mkPen(color=color, width=2))
        self.ma_curve = None  # Moving average curve (optional)

        # Threshold overlays
        self.threshold_lines = {}
        self.threshold_fills = {}
        self.zones = []  # For colored background zones

        # Data storage
        self.x_data = []
        self.y_data = []
        self.max_points = 1000

        # Auto-range settings
        self.enableAutoRange()

    def update_data(self, x: List[float], y: List[float]) -> None:
        """
        Update graph with new data

        Args:
            x: X-axis data (steps/time)
            y: Y-axis data (metric values)
        """
        self.x_data = x[-self.max_points:] if len(x) > self.max_points else x
        self.y_data = y[-self.max_points:] if len(y) > self.max_points else y

        if self.x_data and self.y_data:
            self.main_curve.setData(self.x_data, self.y_data)

    def add_moving_average(self, window: int = 50, color: str = "#FF0000") -> None:
        """
        Add moving average curve

        Args:
            window: Window size for moving average
            color: Color for moving average line
        """
        if not self.ma_curve:
            self.ma_curve = self.plot([], [], pen=pg.mkPen(color=color, width=1, style=Qt.PenStyle.DashLine))

        if len(self.y_data) >= window:
            ma_data = np.convolve(self.y_data, np.ones(window)/window, mode='valid')
            ma_x = self.x_data[window-1:]
            self.ma_curve.setData(ma_x, ma_data)

    def clear_data(self) -> None:
        """Clear all data from graph"""
        self.x_data = []
        self.y_data = []
        self.main_curve.setData([], [])
        if self.ma_curve:
            self.ma_curve.setData([], [])

    def set_y_range(self, min_val: float, max_val: float) -> None:
        """Set Y-axis range"""
        self.setYRange(min_val, max_val)

    def add_threshold(self, name: str, value: float, color: str = "#FFA500",
                      style: str = "line", label: str = None) -> None:
        """
        Add a threshold overlay to the graph

        Args:
            name: Unique identifier for the threshold
            value: Y-axis value for the threshold
            color: Color for the threshold line
            style: 'line' for horizontal line, 'zone' for colored region
            label: Optional label for the threshold
        """
        # Remove existing threshold if it exists
        if name in self.threshold_lines:
            self.removeItem(self.threshold_lines[name])
            del self.threshold_lines[name]

        # Create threshold line
        pen = pg.mkPen(color=color, width=1.5, style=Qt.PenStyle.DashLine)
        threshold_line = pg.InfiniteLine(
            angle=0,
            movable=False,
            pen=pen,
            label=label,
            labelOpts={'position': 0.95, 'color': color}
        )
        threshold_line.setValue(value)
        self.addItem(threshold_line)
        self.threshold_lines[name] = threshold_line

    def add_zone(self, name: str, y_min: float, y_max: float,
                 color: str = "#FF0000", alpha: int = 30, label: str = None) -> None:
        """
        Add a colored zone (background region) to the graph

        Args:
            name: Unique identifier for the zone
            y_min: Lower Y-axis bound
            y_max: Upper Y-axis bound
            color: Zone color
            alpha: Transparency (0-255)
            label: Optional label for the zone
        """
        # Remove existing zone if it exists
        if name in self.threshold_fills:
            self.removeItem(self.threshold_fills[name])
            del self.threshold_fills[name]

        # Create linear region for the zone
        zone = pg.LinearRegionItem(
            values=(y_min, y_max),
            orientation='horizontal',
            movable=False,
            pen=pg.mkPen(None)
        )

        # Set zone color with transparency
        from PyQt6.QtGui import QColor
        qcolor = QColor(color)
        qcolor.setAlpha(alpha)
        zone.setBrush(qcolor)

        self.addItem(zone)
        self.threshold_fills[name] = zone

        # Move zone to background
        zone.setZValue(-10)

    def update_threshold(self, name: str, value: float) -> None:
        """Update an existing threshold value"""
        if name in self.threshold_lines:
            self.threshold_lines[name].setValue(value)

    def remove_threshold(self, name: str) -> None:
        """Remove a threshold line"""
        if name in self.threshold_lines:
            self.removeItem(self.threshold_lines[name])
            del self.threshold_lines[name]

    def remove_zone(self, name: str) -> None:
        """Remove a colored zone"""
        if name in self.threshold_fills:
            self.removeItem(self.threshold_fills[name])
            del self.threshold_fills[name]

    def clear_overlays(self) -> None:
        """Clear all threshold overlays"""
        for line in self.threshold_lines.values():
            self.removeItem(line)
        for zone in self.threshold_fills.values():
            self.removeItem(zone)
        self.threshold_lines.clear()
        self.threshold_fills.clear()

    def enable_log_scale(self, enable: bool = True) -> None:
        """Enable/disable logarithmic Y-axis"""
        self.setLogMode(x=False, y=enable)


class MultiGraphWidget(QWidget):
    """Widget containing multiple synchronized graphs"""

    def __init__(self, parent=None):
        """Initialize multi-graph widget"""
        super().__init__(parent)

        self.graphs = {}
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)

        # Create default graphs
        self._create_default_graphs()

        # Link X-axes for synchronized scrolling/zooming
        self._link_axes()

    def _create_default_graphs(self) -> None:
        """Create default set of graphs"""
        # Loss graph (main, takes more space)
        self.graphs['loss'] = MetricGraph(
            title="Loss",
            y_label="Loss",
            x_label="Step",
            color="#4ade80"  # Bright green
        )
        self.graphs['loss'].setMinimumHeight(250)
        self.layout.addWidget(self.graphs['loss'], stretch=2)

        # Create horizontal layout for smaller graphs
        h_layout = QHBoxLayout()
        h_layout.setSpacing(5)

        # Learning rate graph
        self.graphs['lr'] = MetricGraph(
            title="Learning Rate",
            y_label="LR",
            x_label="Step",
            color="#fbbf24"  # Bright amber/yellow
        )
        self.graphs['lr'].enable_log_scale(True)
        h_layout.addWidget(self.graphs['lr'])

        # Speed graph
        self.graphs['speed'] = MetricGraph(
            title="Training Speed",
            y_label="s/it",
            x_label="Step",
            color="#60a5fa"  # Bright blue
        )
        h_layout.addWidget(self.graphs['speed'])

        self.layout.addLayout(h_layout, stretch=1)

    def _link_axes(self) -> None:
        """Link X-axes of all graphs for synchronized interaction"""
        if len(self.graphs) > 1:
            first_graph = list(self.graphs.values())[0]
            for graph in list(self.graphs.values())[1:]:
                graph.setXLink(first_graph)

    def update_graph(self, name: str, x: List[float], y: List[float]) -> None:
        """
        Update specific graph

        Args:
            name: Graph name ('loss', 'lr', 'speed')
            x: X-axis data
            y: Y-axis data
        """
        if name in self.graphs:
            self.graphs[name].update_data(x, y)

            # Add moving average to loss graph
            if name == 'loss' and len(y) > 50:
                self.graphs[name].add_moving_average(window=50, color="#FF0000")

    def set_threshold(self, graph_name: str, threshold_name: str, value: float,
                      color: str = "#FFA500", label: str = None) -> None:
        """
        Set a threshold on a specific graph

        Args:
            graph_name: Name of the graph ('loss', 'lr', 'speed')
            threshold_name: Unique identifier for the threshold
            value: Threshold value
            color: Color for the threshold line
            label: Optional label
        """
        if graph_name in self.graphs:
            self.graphs[graph_name].add_threshold(threshold_name, value, color, label=label)

    def set_zones(self, graph_name: str, threshold_value: float = None) -> None:
        """
        Set dynamic zones for specific graphs based on thresholds

        Args:
            graph_name: Name of the graph to set zones for
            threshold_value: Optional threshold value to base zones on
        """
        if graph_name not in self.graphs:
            return

        graph = self.graphs[graph_name]

        if graph_name == 'loss':
            # Define zones for loss based on threshold
            base = threshold_value if threshold_value else 0.05
            # Optimal: 0 to 40% of threshold
            graph.add_zone('optimal', 0, base * 0.4, '#00FF00', 20, 'Optimal')
            # Acceptable: 40% to 100% of threshold
            graph.add_zone('acceptable', base * 0.4, base, '#FFD700', 20, 'Acceptable')
            # Warning: 100% to 200% of threshold
            graph.add_zone('warning', base, base * 2, '#FFA500', 20, 'Warning')
            # Critical zone will be anything above 200% of threshold

        elif graph_name == 'speed':
            # Define zones for training speed based on threshold (lower is better)
            base = threshold_value if threshold_value else 5.0
            # Fast: 0 to 20% of threshold
            graph.add_zone('fast', 0, base * 0.2, '#00FF00', 20, 'Fast')
            # Normal: 20% to 60% of threshold
            graph.add_zone('normal', base * 0.2, base * 0.6, '#FFD700', 20, 'Normal')
            # Slow: 60% to 100% of threshold
            graph.add_zone('slow', base * 0.6, base, '#FFA500', 20, 'Slow')
            # Very slow will be anything above the threshold

        elif graph_name == 'lr':
            # Learning rate zones (optional, based on threshold being minimum acceptable)
            if threshold_value:
                # Too low: below threshold
                graph.add_zone('too_low', 0, threshold_value, '#FF6B6B', 15, 'Too Low')
                # Good range: threshold to 10x threshold
                graph.add_zone('good', threshold_value, threshold_value * 10, '#00FF00', 15, 'Good')

    def update_all_thresholds(self, thresholds: Dict[str, float]) -> None:
        """
        Update thresholds and zones for all graphs based on control panel values

        Args:
            thresholds: Dictionary mapping metric names to threshold values
        """
        if 'loss' in thresholds and 'loss' in self.graphs:
            self.graphs['loss'].add_threshold('critical', thresholds['loss'],
                                             '#FF0000', label='Critical')
            # Update zones dynamically based on new threshold
            self.set_zones('loss', thresholds['loss'])

        if 'lr' in thresholds and 'lr' in self.graphs:
            self.graphs['lr'].add_threshold('minimum', thresholds['lr'],
                                           '#FFA500', label='Min LR')
            # Update zones if needed
            self.set_zones('lr', thresholds['lr'])

        if 'speed' in thresholds and 'speed' in self.graphs:
            self.graphs['speed'].add_threshold('slow', thresholds['speed'],
                                              '#FF0000', label='Too Slow')
            # Update zones dynamically based on new threshold
            self.set_zones('speed', thresholds['speed'])

    def clear_all(self) -> None:
        """Clear all graphs"""
        for graph in self.graphs.values():
            graph.clear_data()
            graph.clear_overlays()

    def add_custom_graph(self, name: str, title: str,
                        y_label: str = "Value",
                        color: str = "#00FFFF") -> None:
        """
        Add custom graph

        Args:
            name: Internal name for the graph
            title: Display title
            y_label: Y-axis label
            color: Line color
        """
        if name not in self.graphs:
            graph = MetricGraph(title=title, y_label=y_label, color=color)
            self.graphs[name] = graph
            self.layout.addWidget(graph)
            self._link_axes()

    def remove_graph(self, name: str) -> None:
        """Remove graph by name"""
        if name in self.graphs:
            graph = self.graphs[name]
            self.layout.removeWidget(graph)
            graph.deleteLater()
            del self.graphs[name]

    def set_theme(self, theme: str = "dark") -> None:
        """
        Set color theme

        Args:
            theme: Theme name ('dark', 'light')
        """
        if theme == "dark":
            bg_color = '#1e1e1e'
            fg_color = 'w'
        else:
            bg_color = '#ffffff'
            fg_color = 'k'

        for graph in self.graphs.values():
            graph.setBackground(bg_color)
            # Update text colors
            for item in graph.items:
                if hasattr(item, 'setColor'):
                    item.setColor(fg_color)