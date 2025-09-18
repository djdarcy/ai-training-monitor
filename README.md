# AI Training Monitor

[![Python](https://img.shields.io/badge/python-%3E%3D3.8-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20|%20Linux%20|%20macOS-lightgrey)](https://github.com)

Universal AI training monitor with real-time graphs like Process Explorer - monitor any AI/ML training framework with smooth, professional visualizations.

## Overview

AI Training Monitor is a native desktop application that provides real-time visualization of AI/ML training metrics. Similar to Windows Process Explorer but designed specifically for monitoring training progress, it offers smooth 60 FPS graphs, automatic pattern detection, and a plugin architecture that supports any training framework.

## Features

- 🎯 **Universal Plugin Architecture** - Works with any training framework through extensible parsers
- 📊 **Real-time Smooth Graphs** - 60 FPS visualization using PyQtGraph (not terminal-based)
- 🔍 **Intelligent Analysis** - Automatic detection of overfitting, plateaus, and divergence
- 🎨 **Professional Native UI** - Desktop application with Process Explorer-style interface
- 📈 **Multi-Metric Tracking** - Monitor loss, learning rate, speed, memory usage simultaneously
- 🔌 **Framework Support** - Ostris, Kohya_ss, HuggingFace, PyTorch Lightning, and more
- 💾 **Export Options** - Save graphs as images, export data as CSV
- 🖥️ **Cross-Platform** - Works on Windows, Linux, and macOS

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-training-monitor.git
cd ai-training-monitor

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

## Usage

```bash
# Auto-detect framework and monitor
python -m ai_training_monitor /path/to/training/output

# Specify framework explicitly
python -m ai_training_monitor --framework ostris /path/to/output/MacyDek2

# Monitor specific log file
python -m ai_training_monitor --log /path/to/log.txt --framework kohya

## Development

### Prerequisites

- List prerequisites here

### Setup

```bash
# Setup instructions here
```

## Contributions
Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on how to contribute.

Like the project?

[!["Buy Me A Coffee"](https://camo.githubusercontent.com/0b448aabee402aaf7b3b256ae471e7dc66bcf174fad7d6bb52b27138b2364e47/68747470733a2f2f7777772e6275796d6561636f666665652e636f6d2f6173736574732f696d672f637573746f6d5f696d616765732f6f72616e67655f696d672e706e67)](https://www.buymeacoffee.com/djdarcy)

## License

This project is licensed under the terms specified in the LICENSE file.

## Acknowledgements

Dustin 6962246+djdarcy@users.noreply.github.com
