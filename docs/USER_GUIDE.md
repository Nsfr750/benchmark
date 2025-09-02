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
   - [Hardware Monitoring](#hardware-monitoring)
   - [Pystone Benchmark](#pystone-benchmark)
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
   git clone https://github.com/Nsfr750/benchmark.git
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

1. Select the type of benchmark from the Test menu
2. Configure the test parameters (duration, iterations, etc.)
3. Click "Run Benchmark" to start the test
4. Monitor real-time progress with the progress bar
5. View detailed results upon completion

### Viewing Results

Benchmark results are displayed in a comprehensive format with:

- Test name, timestamp, and duration
- Performance metrics (scores, operations per second, etc.)
- System information (CPU, memory, OS details)
- Interactive charts and visualizations
- Historical comparison with previous runs

### Pystone Benchmark

The Pystone benchmark is now available with enhanced features:

- Progress tracking during test execution
- Configurable number of iterations
- Detailed performance metrics
- Comparison with previous runs
- Exportable results

### Hardware Monitoring

Real-time hardware monitoring is available during benchmark execution:

- CPU usage and temperature
- Memory usage
- Disk I/O statistics
- Network activity
- System load

### Exporting Data

Export benchmark results for further analysis:

1. Click "Export Results" from the File menu
2. Choose from available formats:
   - CSV (for spreadsheet analysis)
   - JSON (for programmatic processing)
   - PNG/SVG (for charts and visualizations)
3. Select a destination folder
4. Click "Save" to export

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
python main.py --benchmark=pystone --iterations=50000 --output=results.json
```

Available options:
- `--benchmark`: Specify benchmark to run (default: all)
- `--iterations`: Number of iterations (default: from config)
- `--output`: Save results to file
- `--quiet`: Run in non-interactive mode
- `--version`: Show version information

### Custom Benchmark Scripts

You can create and run custom benchmark scripts by placing them in the `benchmarks` directory. The application will automatically detect and load them at startup.

### Benchmark Configuration

Customize benchmark behavior through the configuration file (`config/config.json`):

```json
{
  "benchmark": {
    "default_iterations": 10000,
    "enable_hardware_monitoring": true,
    "save_results_automatically": true,
    "result_history_size": 50
  },
  "ui": {
    "theme": "dark",
    "language": "en",
    "font_size": 10
  }
}
```

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
