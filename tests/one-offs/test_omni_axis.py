#!/usr/bin/env python
"""
Test script to verify OmniGraph axis scaling
"""
import sys
from pathlib import Path
# Add the project root to path (go up from tests/one-offs to project root)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from ai_training_monitor.core.ui.omni_graph import OmniGraph

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OmniGraph Axis Test")
        self.setGeometry(100, 100, 800, 600)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Create OmniGraph
        self.graph = OmniGraph()
        layout.addWidget(self.graph)

        # Add test data button
        btn = QPushButton("Add Test Data & Switch Primary")
        btn.clicked.connect(self.add_test_data)
        layout.addWidget(btn)

        self.metric_index = 0

    def add_test_data(self):
        # Add some test data
        test_data = {
            'step': 1,
            'loss': 0.05,  # Typical loss value
            'lr': 1e-4,    # Typical learning rate
            'speed': 2.5    # Typical speed in s/it
        }

        # Add data multiple times to build up arrays
        for i in range(10):
            test_data['step'] = i
            test_data['loss'] = 0.05 + i * 0.002
            test_data['lr'] = 1e-4 * (1 - i * 0.05)
            test_data['speed'] = 2.5 + i * 0.1
            self.graph.update_data(test_data)

        # Cycle through primary metrics
        metrics = ['loss', 'lr', 'speed']
        self.metric_index = (self.metric_index + 1) % 3
        self.graph.set_primary_metric(metrics[self.metric_index])
        print(f"Switched to {metrics[self.metric_index]} as primary")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())