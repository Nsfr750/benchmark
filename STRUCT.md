# 📂 Project Structure

```
benchmark/
├── .github/                            # GitHub Actions
│   ├── workflows/                      # GitHub Actions workflows
│   │   └── ci-cd.yml                   # CI/CD pipeline
│   ├── issues/                         # GitHub Issues
│   |   └── templates/                  # GitHub Issues templates
│   └── FUNDING.yml                     # Funding file
├── assets/                             # Assets files
├── config/                             # Configuration files
│   ├── config.json                     # Configuration file
│   └── updates.json                    # Update cache file
├── docs/                               # Documentation
│   ├── images/                         # Documentation images
│   ├── pdf/                            # Documentation PDF
│   └── USER_GUIDE.md                   # User Guide
├── lang/                               # Language files
│   ├── en.json                         # English language file
│   └── it.json                         # Italian language file
├── logs/                               # Log files
├── script/                             # Source code
│   ├── __init__.py                     # Initialize package
│   ├── about.py                        # About dialog
│   ├── benchmark_history.py            # Benchmark history
│   ├── benchmark_tests.py              # Benchmark tests
│   ├── CLI_pystone.py                  # CLI Pystone benchmark
│   ├── config_manager.py               # Configuration manager
│   ├── export_results.py               # Export results
│   ├── hardware_monitor.py             # Hardware monitor
│   ├── help.py                         # Help Dialog
│   ├── history_dialog.py               # History dialog
│   ├── lang_mgr.py                     # Language manager
│   ├── logger.py                       # Logging configuration
│   ├── menu.py                         # Menu bar functionality
│   ├── settings.py                     # Settings dialog
│   ├── sponsor.py                      # Sponsor dialog
│   ├── system_info.py                  # System information
│   ├── test_menu.py                    # Test menu
│   ├── theme_manager.py                # Theme Manager
│   ├── updates.py                      # Update system
│   ├── version.py                      # Version system
│   ├── view_log.py                     # Log viewer
│   └── visualization.py                # Benchmark Visualization
├── tests/                              # Test files
│   ├── test_benchmark.py               # Test benchmark
│   ├── test_hardware_monitor.py        # Test hardware monitor
│   ├── test_monitor_manual.py          # Test monitor manual
│   ├── test_monitor.py                 # Test monitor
│   └── TEST_README.md                  # Test README
├── .gitignore                          # Git ignore file
├── CHANGELOG.md                        # Changelog file
├── CONTRIBUTING.md                     # Contributing file
├── LICENSE                             # GPLv3 License file
├── main.py                             # Main application
├── README.md                           # This file
├── requirements.txt                    # Requirements file
└── TO_DO.md                            # To do list
```