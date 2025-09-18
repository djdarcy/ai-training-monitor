# Contributing to AI Training Monitor

Thank you for your interest in contributing to AI Training Monitor! This document provides guidelines for contributing to the project.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Style Guidelines](#style-guidelines)
- [Commit Guidelines](#commit-guidelines)
- [Community](#community)

## Code of Conduct

By participating in this project, you agree to be respectful and constructive in all interactions. We welcome contributors of all experience levels and backgrounds.

## Getting Started

1. Check out the [open issues](https://github.com/djdarcy/ai-training-monitor/issues) to see what needs help
2. Look for issues labeled `good first issue` for beginner-friendly tasks
3. Read through existing [pull requests](https://github.com/djdarcy/ai-training-monitor/pulls) to avoid duplicate work
4. Join the discussion in [issue #6](https://github.com/djdarcy/ai-training-monitor/issues/6) for community feedback

## How Can I Contribute?

### Reporting Bugs

Found a bug? Please help us fix it!

Before creating a bug report:
- Check the [existing issues](https://github.com/djdarcy/ai-training-monitor/issues?q=is%3Aissue+label%3Abug) to avoid duplicates
- Gather information about the problem
- Try to reproduce the issue

When reporting a bug, please include:
- Python version and OS
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Error messages or screenshots
- Log files (if applicable)

[**Submit a Bug Report**](https://github.com/djdarcy/ai-training-monitor/issues/new?labels=bug&title=BUG%3A+)

### Suggesting Enhancements

Have an idea for a new feature? We'd love to hear it!

Before suggesting an enhancement:
- Check the [roadmap in README](README.md#roadmap) for planned features
- Search [existing feature requests](https://github.com/djdarcy/ai-training-monitor/issues?q=is%3Aissue+label%3Aenhancement)
- Consider if it fits the project scope

When suggesting an enhancement:
- Provide a clear use case
- Explain why existing features don't solve the problem
- Include mockups or examples if applicable

[**Submit a Feature Request**](https://github.com/djdarcy/ai-training-monitor/issues/new?labels=enhancement&title=FEATURE%3A+)

### Contributing Code

#### Parser Development

Want to add support for a new training framework? Check out:
- Base parser interface: `ai_training_monitor/parsers/base.py`
- Example implementation: `ai_training_monitor/parsers/ostris.py`
- [Parser support issue](https://github.com/djdarcy/ai-training-monitor/issues/3)

#### Bug Fixes

Known issues that need help:
- [OmniGraph Y-axis scaling](https://github.com/djdarcy/ai-training-monitor/issues/1)
- [GPU RAM tracking](https://github.com/djdarcy/ai-training-monitor/issues/7)
- [Epoch tracking](https://github.com/djdarcy/ai-training-monitor/issues/8)
- [Graph range on reload](https://github.com/djdarcy/ai-training-monitor/issues/9)

### Documentation

Help improve our documentation:
- Add usage examples
- Create video tutorials
- Improve installation instructions
- Add screenshots to README

See [documentation issue](https://github.com/djdarcy/ai-training-monitor/issues/4)

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- PyQt6 dependencies (varies by OS)

### Setup Instructions

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/ai-training-monitor.git
   cd ai-training-monitor
   ```

3. Create a new branch from `dev`:
   ```bash
   git checkout dev
   git checkout -b feature/your-feature-name
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

5. Set up git hooks for version management:
   ```bash
   ./scripts/install-hooks.sh
   ```

6. Make your changes and test:
   ```bash
   python -m ai_training_monitor --version
   python tests/one-offs/test_omni_axis.py
   ```

### Testing

- Run the application: `python -m ai_training_monitor`
- Test imports: `python -c "from ai_training_monitor.core.monitor import TrainingMonitor"`
- Run test scripts in `tests/one-offs/`

## Style Guidelines

### Python Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and small
- Use type hints where appropriate

### UI Guidelines

- Maintain dark theme compatibility
- Ensure graphs remain readable at different sizes
- Test with various screen resolutions
- Keep UI responsive during updates

## Commit Guidelines

### Commit Messages

Follow this format:
```
Short description (50 chars or less)

Longer explanation if needed. Wrap at 72 characters.
Explain what and why, not how.

- Bullet points for multiple changes
- Keep related changes in same commit
- Separate unrelated changes

Fixes #issue_number
```

### Version Management

The project uses automated version tracking. When you commit:
- Version is automatically updated by git hooks
- Format: `VERSION_BRANCH_BUILD-YYYYMMDD-COMMITHASH`
- Don't manually edit `version.py`

## Pull Request Process

1. Ensure your branch is up to date with `dev`:
   ```bash
   git checkout dev
   git pull upstream dev
   git checkout your-branch
   git rebase dev
   ```

2. Test your changes thoroughly

3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a Pull Request:
   - Target the `dev` branch (not `main`)
   - Reference any related issues
   - Provide clear description of changes
   - Include screenshots for UI changes

5. Address review feedback promptly

## Community

### Getting Help

- Check the [README](README.md) for basic usage
- Search [existing issues](https://github.com/djdarcy/ai-training-monitor/issues)
- Ask questions in [discussions](https://github.com/djdarcy/ai-training-monitor/issues/6)

### Project Links

- [GitHub Repository](https://github.com/djdarcy/ai-training-monitor)
- [Issues](https://github.com/djdarcy/ai-training-monitor/issues)
- [Pull Requests](https://github.com/djdarcy/ai-training-monitor/pulls)
- [Alpha Release Roadmap](https://github.com/djdarcy/ai-training-monitor/issues/5)

### Support the Project

If you find this project useful:
- ⭐ Star the repository
- 📣 Share with others who might benefit
- ☕ [Buy me a coffee](https://www.buymeacoffee.com/djdarcy)

## Thank You!

Every contribution helps make AI Training Monitor better. Whether it's reporting bugs, suggesting features, improving documentation, or writing code - we appreciate your help!

---

Questions? Feel free to open an [issue](https://github.com/djdarcy/ai-training-monitor/issues/new) or join the [discussion](https://github.com/djdarcy/ai-training-monitor/issues/6).