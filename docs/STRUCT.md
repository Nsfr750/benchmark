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
├── benchmark_results/                  # Benchmark results
├── config/                             # Configuration files
│   ├── config.json                     # Configuration file
│   └── updates.json                    # Update cache file
├── docs/                               # Documentation
│   ├── API.md                          # API documentation
│   ├── CODE_OF_CONDUCT.md              # Code of Conduct
│   ├── CONTRIBUTING.md                 # Contributing file
│   ├── FAQ.md                          # Frequently Asked Questions
│   ├── PREREQUISITES.md                # Prerequisites file
│   ├── ROADMAP.md                      # Roadmap file
│   ├── STRUCT.md                       # This file
│   └── USER_GUIDE.md                   # User Guide
├── logs/                               # Log files
├── script/                             # Source code
│   ├── test_script/                    # Test scripts
│   │   ├── __init__.py                 # Initialize package
│   │   ├── benchmark_history.py        # Benchmark history
│   │   ├── benchmark_tests.py          # Benchmark tests
│   │   ├── CLI_pystone.py              # CLI Pystone benchmark          
│   │   ├── export_dialog.py            # Export dialog          
│   │   ├── export_results.py           # Export results          
│   │   ├── hardware_monitor.py         # Hardware monitor           
│   │   ├── history_dialog.py           # History dialog           
│   │   ├── pystone_dialog.py           # Pystone dialog           
│   │   ├── pystone_test.py             # Pystone test 
│   │   ├── system_info.py              # System information           
│   │   ├── test_benchmark.py           # Test benchmark
│   │   ├── test_hardware_monitor.py    # Test hardware monitor
│   │   └── test_monitor.py             # Test monitor
│   ├── __init__.py                     # Initialize package
│   ├── about.py                        # About dialog
│   ├── config_manager.py               # Configuration manager
│   ├── help.py                         # Help Dialog
│   ├── lang_mgr.py                     # Language manager
│   ├── logger.py                       # Logging configuration
│   ├── new_menu.py                     # Menu bar functionality
│   ├── settings.py                     # Settings dialog
│   ├── sponsor.py                      # Sponsor dialog
│   ├── theme_manager.py                # Theme Manager
│   ├── translations.py                 # Translations
│   ├── updates.py                      # Update system
│   ├── version.py                      # Version system
│   ├── view_log.py                     # Log viewer
│   └── visualization.py                # Benchmark Visualization
├── tests/                              # Test files
│   ├── test_monitor_manual.py          # Test monitor manual
│   └── TEST_README.md                  # Test README
├── .gitignore                          # Git ignore file
├── CHANGELOG.md                        # Changelog file
├── LICENSE                             # GPLv3 License file
├── main.py                             # Main application
├── README.md                           # This file
├── requirements.txt                    # Requirements file
└── TO_DO.md                            # To do list
```