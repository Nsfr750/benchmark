# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive API documentation in `docs/API.md`
- Project roadmap in `docs/ROADMAP.md`
- Code of Conduct in `docs/CODE_OF_CONDUCT.md`
- Detailed prerequisites and setup guide in `docs/PREREQUISITES.md`
- CODEOWNERS file for better project management
- Support for additional benchmark metrics and visualizations
- Enhanced error handling and user feedback
- Automated test suite for core functionality

### Changed
- Updated dependencies to their latest stable versions
- Improved documentation structure and content
- Enhanced build and deployment process
- Optimized performance for large benchmark datasets
- Refactored core modules for better maintainability

### Fixed
- Resolved issues with benchmark result saving/loading
- Fixed memory leaks in long-running benchmark sessions
- Addressed UI responsiveness issues
- Fixed compatibility issues with specific hardware configurations
- Corrected documentation inaccuracies

## [1.3.0] - 2025-09-02

### Added in 1.3.0

- Enhanced Pystone benchmark integration with progress tracking
- Added comprehensive error handling and user feedback for benchmark operations
- Implemented translation support for all UI elements
- Added detailed system information collection for benchmark context
- Created a unified test menu with categorized benchmark options

### Changed in 1.3.0

- Refactored menu system for better organization and maintainability
- Updated UI with improved error messages and user guidance
- Enhanced benchmark result presentation with additional metrics
- Optimized performance of benchmark execution

### Fixed in 1.3.0

- Fixed translation key errors in benchmark dialogs
- Resolved issues with benchmark result saving and loading
- Fixed UI layout issues in high DPI displays
- Addressed memory management in long-running benchmark sessions

## [1.2.0] - 2025-08-28

### Added in 1.2.0

- GitHub Actions CI/CD pipeline with automated testing and deployment
- Comprehensive hardware monitoring during benchmark tests
  - Real-time CPU and memory usage tracking
  - Disk I/O monitoring
  - Network activity tracking
  - Temperature monitoring (where supported)
- Configuration management system with support for multiple profiles
- User guide documentation in `/docs` directory
- Benchmark result comparison view
- Support for custom benchmark presets
- Enhanced error handling and logging

### Changed in 1.2.0

- Updated dependencies to their latest stable versions
- Improved test coverage and reliability
- Refactored codebase for better maintainability
- Enhanced visualization of benchmark results
- Optimized performance for large datasets

### Fixed in 1.2.0

- Fixed issues with result export functionality
- Resolved memory leaks in long-running tests
- Addressed minor UI/UX issues
- Fixed compatibility issues across different platforms

## [1.1.0] - 2025-08-28

### Added in 1.1.0

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
- Enhanced visualization with interactive tooltips showing detailed metrics
- Added chart export functionality (PNG/SVG)
- Improved data point highlighting on hover
- Context menu for chart interactions
- Support for displaying additional benchmark metrics in tooltips

### Changed in 1.1.0

- Improved error handling for edge cases
- Enhanced logging for better debugging
- Updated requirements with new dependencies (psutil, py-cpuinfo, tqdm)
- Refactored codebase for better maintainability

### Fixed in 1.1.0

- Fixed language file loading in compiled version
- Fixed path resolution for assets in compiled version
- Fixed compatibility issues across different platforms

## [1.0.0] - 2025-08-27

### Added in 1.0.0
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
