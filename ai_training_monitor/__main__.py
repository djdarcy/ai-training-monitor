"""
Entry point for AI Training Monitor
"""
import sys
import argparse
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication

from .core.ui.main_window import TrainingMonitorWindow
from .version import __version__, get_version_dict


def setup_logging(verbose: bool = False):
    """Set up logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="AI Training Monitor - Real-time visualization for AI/ML training",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Monitor Ostris AI Toolkit training
  python -m ai_training_monitor /path/to/output/folder

  # Specify framework explicitly
  python -m ai_training_monitor --framework ostris /path/to/log.txt

  # Start with specific update interval
  python -m ai_training_monitor --interval 500 /path/to/log
        """
    )

    parser.add_argument(
        'path',
        nargs='?',
        help='Path to log file or training output directory'
    )

    parser.add_argument(
        '--framework', '-f',
        choices=['auto', 'ostris', 'kohya', 'huggingface', 'pytorch'],
        default='auto',
        help='Training framework (default: auto-detect)'
    )

    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=1000,
        help='Update interval in milliseconds (default: 1000)'
    )

    parser.add_argument(
        '--theme', '-t',
        choices=['dark', 'light'],
        default='dark',
        help='UI theme (default: dark)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--version', '-V',
        action='store_true',
        help='Show version information and exit'
    )

    args = parser.parse_args()

    # Handle version display
    if args.version:
        version_info = get_version_dict()
        print(f"AI Training Monitor {version_info['base']}")
        print(f"Version: {__version__}")
        print(f"Branch: {version_info['branch']}")
        print(f"Build: {version_info['build']}")
        print(f"Date: {version_info['date']}")
        print(f"Commit: {version_info['commit']}")
        sys.exit(0)

    # Set up logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("AI Training Monitor")
    app.setOrganizationName("AI Training Monitor")

    # Create main window
    window = TrainingMonitorWindow()

    # Pre-populate if path provided
    if args.path:
        window.log_path_edit.setText(args.path)

        # Set framework if specified
        if args.framework != 'auto':
            index = window.framework_combo.findText(args.framework.capitalize())
            if index >= 0:
                window.framework_combo.setCurrentIndex(index)

    # Set update interval
    window.update_spin.setValue(args.interval)

    # Show window
    window.show()

    logger.info("AI Training Monitor started")

    # Run application
    sys.exit(app.exec())


if __name__ == '__main__':
    main()