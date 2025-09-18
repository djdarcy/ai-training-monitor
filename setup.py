from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-training-monitor",
    version="0.1.0",
    description="Universal AI training monitor with real-time graphs like Process Explorer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AI Training Monitor Contributors",
    author_email="",
    url="https://github.com/yourusername/ai-training-monitor",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.5.0",
        "pyqtgraph>=0.13.3",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "PyYAML>=6.0",
        "watchdog>=3.0.0",
        "python-dateutil>=2.8.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-qt>=4.2.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "export": [
            "matplotlib>=3.7.0",
            "Pillow>=10.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-training-monitor=ai_training_monitor.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
