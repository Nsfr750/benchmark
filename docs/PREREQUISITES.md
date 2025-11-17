# Prerequisites

This document outlines the system and software requirements needed to run, develop, and contribute to the Benchmark Application.

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11 (64-bit)
- **Processor**: 64-bit processor with 2+ cores
- **Memory**: 4GB RAM
- **Storage**: 500MB available space
- **Display**: 1024x768 resolution

### Recommended Requirements
- **Operating System**: Windows 10/11 (64-bit)
- **Processor**: 64-bit quad-core processor
- **Memory**: 8GB RAM or more
- **Storage**: 1GB available space (SSD recommended)
- **Display**: 1920x1080 resolution or higher

## Software Dependencies

### Runtime Dependencies
- **Python**: 3.8 or higher
- **Pip**: Latest version
- **Git**: For version control

### Python Packages
Core dependencies (automatically installed with the application):
```
numpy>=1.20.0
pandas>=1.3.0
psutil>=5.9.0
py-cpuinfo>=8.0.0
pywin32>=300; sys_platform == 'win32'
PyQt5>=5.15.0
matplotlib>=3.4.0
```

### Development Dependencies
Additional dependencies for development:
```
pytest>=6.2.5
pytest-cov>=2.12.0
black>=21.12b0
flake8>=4.0.0
mypy>=0.910
sphinx>=4.2.0
sphinx-rtd-theme>=1.0.0
```

## Development Environment Setup

### Windows Setup
1. Install Python 3.8+ from [python.org](https://www.python.org/downloads/windows/)
2. Install Git from [git-scm.com](https://git-scm.com/download/win)
3. Clone the repository:
   ```
   git clone https://github.com/Nsfr750/benchmark.git
   cd benchmark
   ```
4. Create and activate a virtual environment:
   ```
   python -m venv venv
   .\venv\Scripts\activate
   ```
5. Install development dependencies:
   ```
   pip install -r requirements-dev.txt
   ```

### Building from Source
1. Install build tools:
   ```
   pip install build
   ```
2. Build the package:
   ```
   python -m build
   ```
3. Install the built package:
   ```
   pip install dist/benchmark-*.whl
   ```

## Configuration

### Environment Variables
- `BENCHMARK_CONFIG_PATH`: Path to custom configuration file
- `BENCHMARK_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `BENCHMARK_CACHE_DIR`: Directory to store cache files

### Configuration Files
- `config/config.json`: Main configuration file
- `config/logging.conf`: Logging configuration

## Troubleshooting

### Common Issues
1. **Missing Dependencies**
   - Run `pip install -r requirements.txt`
   - Ensure all system dependencies are installed

2. **Permission Issues**
   - Run the application as administrator if required
   - Check file permissions in the installation directory

3. **Performance Issues**
   - Close other applications while running benchmarks
   - Check for background processes consuming resources
