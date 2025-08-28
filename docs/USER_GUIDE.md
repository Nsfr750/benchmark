# Benchmark Application - User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Features](#features)
   - [Running Benchmarks](#running-benchmarks)
   - [Viewing Results](#viewing-results)
   - [Exporting Data](#exporting-data)
   - [Configuration](#configuration)
5. [Advanced Usage](#advanced-usage)
6. [Troubleshooting](#troubleshooting)
7. [FAQs](#faqs)

## Introduction

Welcome to the Benchmark Application! This tool helps you measure and analyze the performance of your system through various benchmark tests. It provides detailed metrics, visualizations, and export capabilities to help you understand your system's performance characteristics.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/benchmark.git
   cd benchmark
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) For hardware monitoring features, install additional dependencies:

   ```bash
   pip install psutil wmi
   ```

## Getting Started

1. Launch the application:

   ```bash
   python main.py
   ```

2. The main window will open with the following sections:
   - **Test Selection**: Choose from available benchmark tests
   - **Configuration**: Adjust test parameters
   - **Results**: View and analyze benchmark results

## Features

### Running Benchmarks

1. Select a benchmark test from the dropdown menu
2. Configure test parameters as needed
3. Click "Start Benchmark" to begin
4. Monitor progress in the status bar
5. View results in the results panel

### Viewing Results

Results are displayed in both tabular and graphical formats:

- **Performance Metrics**: CPU usage, memory usage, execution time
- **Comparison View**: Compare results across multiple test runs
- **History**: Access previous benchmark results

### Exporting Data

You can export benchmark results in multiple formats:

1. Click the "Export" button
2. Choose the desired format (CSV, JSON)
3. Select the location to save the file
4. Click "Save"

### Configuration

Customize the application settings:

1. Click on "Settings" in the menu bar
2. Adjust settings as needed:
   - Theme (Light/Dark)
   - Default export format
   - Update preferences
   - Hardware monitoring settings

## Advanced Usage

### Command Line Interface

Run benchmarks directly from the command line:

```bash
python -m script.CLI_pystone --iterations 1000 --output results.json
```

### Custom Benchmark Scripts

Create your own benchmark scripts by extending the base test class. Refer to the developer documentation for more details.

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   - Ensure all required packages are installed
   - Run `pip install -r requirements.txt`

2. **Hardware Monitoring Not Working**
   - Make sure you have the necessary system permissions
   - Check if your hardware is supported

3. **Performance Issues**
   - Close other resource-intensive applications
   - Run benchmarks with administrator/root privileges if needed

## FAQs

**Q: How accurate are the benchmark results?**
A: Results may vary based on system load and other running applications. For best results, close other applications and run multiple iterations.

**Q: Can I compare results between different systems?**
A: Yes, you can export results from different systems and compare them using the comparison view.

**Q: How do I update the application?**
A: The application includes an automatic update checker. You can also check for updates manually in the Help menu.

**Q: Is my data being collected or shared?**
A: No, all benchmark data is stored locally on your machine and is never shared without your explicit permission.

---

For additional support, please open an issue on our [GitHub repository](https://github.com/yourusername/benchmark/issues).
