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

        # Configure plot
        self.setTitle(title, color='w', size='12pt')
        self.setLabel('left', y_label, color='w')
        self.setLabel('bottom', x_label, color='w')
        self.showGrid(x=True, y=True, alpha=0.3)
        self.setBackground('#1e1e1e')

        # Create plot curves
        self.main_curve = self.plot([], [], pen=pg.mkPen(color=color, width=2))
        self.ma_curve = None  # Moving average curve (optional)

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
            color="#00FF00"
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
            color="#FFD700"
        )
        self.graphs['lr'].enable_log_scale(True)
        h_layout.addWidget(self.graphs['lr'])

        # Speed graph
        self.graphs['speed'] = MetricGraph(
            title="Training Speed",
            y_label="s/it",
            x_label="Step",
            color="#FF69B4"
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

    def clear_all(self) -> None:
        """Clear all graphs"""
        for graph in self.graphs.values():
            graph.clear_data()

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