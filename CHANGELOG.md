# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- New visualization tab with interactive charts for benchmark results
- Support for line charts, bar charts, and scatter plots
- Time-based filtering of benchmark results (All time, last 7 days, last 30 days)
- Multiple Y-axis options (Pystones/s, Time Elapsed, Iterations)
- Internationalization support for all visualization components
- Added Test menu with the following features:
  - System Information viewer
  - Benchmark Tests launcher
  - Hardware Monitor
  - Export/Import benchmark results
- Benchmark history feature with persistent storage
- History dialog to view, filter, and manage past benchmark results
- Ability to compare current results with historical data
- System information tracking for each benchmark run
- Date-based filtering of history (today, last 7 days, last 30 days, custom range)
- Export/import functionality for benchmark history
- Dark/Light theme support with system preference detection
- Theme selection in the View menu
- Persistent theme preferences across application restarts

## [1.1.0] - 2025-08-28

### Added

- Comprehensive system information collection (CPU, memory, disk, OS details)
- Advanced benchmark tests including:
  - CPU performance (math operations, sorting)
  - Memory allocation and access
  - Disk I/O performance
- Result export functionality (JSON and CSV formats)
- Command-line test runner
- Detailed benchmark statistics (min, max, mean, median, standard deviation)
- Support for multiple test iterations
- Error handling and fallback mechanisms

### Changed

- Improved error handling for edge cases
- Enhanced logging for better debugging
- Updated requirements with new dependencies (psutil, py-cpuinfo, tqdm)
- Refactored codebase for better maintainability

### Fixed

- Fixed language file loading in compiled version
- Fixed path resolution for assets in compiled version
- Fixed compatibility issues across different platforms

## [1.0.0] - 2025-08-27

### Added
- Initial project setup
- Basic PySide6 GUI interface
- Pystone benchmark implementation
- Multi-language support (English and Italian)
- Logging system
- Update checker
- Settings dialog

### Changed
- Improved error handling and user feedback
- Optimized benchmark execution
- Enhanced UI/UX

### Fixed
- Invalid cache file handling in update system
- Minor UI layout issues
- Language switching improvements

## [1.0.0] - 2025-08-28

### Added
- Initial public release
- Complete documentation
- Basic testing suite
- Build and packaging scripts

## [0.1.0] - 2025-08-01

### Added
- Project initialization
- Basic benchmark functionality
- Initial UI design
