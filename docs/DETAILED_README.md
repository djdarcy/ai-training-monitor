# AI Training Monitor

A universal, real-time training monitor for AI/ML frameworks. Think of it as "Process Explorer" for AI training - providing smooth, professional graphs and instant insights into your training progress.

![AI Training Monitor](docs/screenshot.png)

## Features

- 🎯 **Universal**: Works with any training framework through plugins
- 📊 **Real-time Graphs**: Smooth 60 FPS visualization like Process Explorer
- 🔌 **Plugin Architecture**: Easy to add support for new frameworks
- 🎨 **Professional UI**: Native desktop application with PyQt6
- 📈 **Multi-Metric Tracking**: Loss, learning rate, speed, memory usage
- 🔍 **Pattern Detection**: Automatic detection of overfitting, plateaus, divergence
- 💾 **Export Options**: Save graphs as images, export data as CSV
- 🖥️ **Cross-Platform**: Works on Windows, Linux, macOS

## Supported Frameworks

- ✅ **Ostris AI Toolkit** - LoRA/Dreambooth training
- ✅ **Kohya_ss** - Stable Diffusion training
- ✅ **HuggingFace Transformers** - LLM fine-tuning
- ✅ **PyTorch Lightning** - General deep learning
- ✅ **TensorFlow/Keras** - via TensorBoard logs
- 🔜 **Axolotl** - LLM training (coming soon)
- 🔜 **Custom Formats** - Define your own parser

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-training-monitor.git
cd ai-training-monitor

# Install dependencies
pip install -r requirements.txt

# Run the monitor
python training_monitor.py
```

### Basic Usage

```bash
# Auto-detect format and monitor
python training_monitor.py /path/to/training/output

# Specify framework explicitly
python training_monitor.py --framework ostris /path/to/output/MacyDek2

# Monitor specific log file
python training_monitor.py --log /path/to/log.txt --framework kohya
```

## How It Works

The monitor uses a plugin architecture to support different training frameworks:

```
ai-training-monitor/
├── training_monitor.py      # Main application
├── core/
│   ├── monitor.py          # Core monitoring logic
│   ├── analyzer.py         # Pattern detection
│   └── ui/
│       ├── main_window.py  # PyQt6 main window
│       └── graphs.py       # Real-time graph widgets
├── parsers/                # Framework-specific parsers
│   ├── base.py            # Base parser interface
│   ├── ostris.py          # Ostris AI Toolkit
│   ├── kohya.py           # Kohya_ss
│   ├── transformers.py    # HuggingFace
│   └── ...
└── themes/                 # UI themes
    ├── dark.py
    └── light.py
```

## Creating Custom Parsers

Add support for your training framework:

```python
# parsers/custom.py
from parsers.base import BaseParser

class CustomParser(BaseParser):
    """Parser for Custom Training Framework"""

    name = "custom"
    patterns = {
        'loss': r'loss[:\s]*([\d.e+-]+)',
        'lr': r'learning_rate[:\s]*([\d.e+-]+)',
        'epoch': r'epoch[:\s]*(\d+)',
    }

    def parse_line(self, line: str) -> dict:
        """Extract metrics from log line"""
        metrics = {}
        for metric, pattern in self.patterns.items():
            match = re.search(pattern, line)
            if match:
                metrics[metric] = float(match.group(1))
        return metrics
```

## Configuration

Create `config.yaml` to customize the monitor:

```yaml
# Display settings
update_interval: 1000  # milliseconds
max_points: 5000      # points to keep in memory
theme: dark           # dark/light

# Graph settings
graphs:
  - metric: loss
    color: "#FF6B6B"
    show_average: true
    average_window: 50
  - metric: lr
    color: "#4ECDC4"
    log_scale: true
  - metric: speed
    color: "#95E77E"
    unit: "s/it"

# Alerts
alerts:
  loss_threshold: 0.01  # Alert when loss < threshold
  plateau_steps: 500    # Alert if no improvement
  divergence_factor: 2  # Alert if loss increases 2x
```

## Screenshots

### Main Interface
![Main Interface](docs/main_interface.png)

### Multi-Framework Support
![Framework Comparison](docs/multi_framework.png)

### Pattern Detection
![Pattern Detection](docs/pattern_detection.png)

## Requirements

- Python 3.8+
- PyQt6
- pyqtgraph
- numpy
- PyYAML

## Development

### Running Tests

```bash
pytest tests/
```

### Building Executable

```bash
# Windows
pyinstaller training_monitor.spec

# Linux/Mac
python -m PyInstaller training_monitor.spec
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Adding Framework Support

1. Create parser in `parsers/` directory
2. Register in `parsers/__init__.py`
3. Add tests in `tests/parsers/`
4. Submit PR with example log file

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by Windows Process Explorer
- Built for the AI training community
- Special thanks to Ostris AI Toolkit users

## Roadmap

- [ ] GPU metrics integration (nvidia-smi)
- [ ] Remote monitoring via network
- [ ] Training comparison mode
- [ ] Checkpoint quality predictions
- [ ] Auto-stop integration
- [ ] Mobile companion app
- [ ] Cloud metrics upload (W&B, TensorBoard)

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/ai-training-monitor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ai-training-monitor/discussions)
- **Discord**: [Join our Discord](https://discord.gg/example)

---

Made with ❤️ for the AI training community