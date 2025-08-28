"""
Menu bar and related functionality for the Benchmark application.
"""
import os
import importlib
import logging

# Set up logging
log = logging.getLogger(__name__)
from PySide6.QtWidgets import QMenuBar, QMenu, QStyle, QApplication
from PySide6.QtGui import QKeySequence, QIcon, QAction, QActionGroup
from PySide6.QtCore import Qt, Signal, QObject

from script.version import APP_NAME, APP_DESCRIPTION, __version__
from script.lang_mgr import get_language_manager
from script.theme_manager import get_theme_manager
# Import view_log directly since it doesn't cause circular imports
from script import view_log
from script.lang_mgr import LanguageManager
from script.system_info import get_system_info, save_system_info
from script.benchmark_tests import BenchmarkSuite
from script.export_dialog import ExportDialog
from PySide6.QtWidgets import QMessageBox
import json
import os
import sys
import subprocess
import timeit
import math
from datetime import datetime

# Lazy import updates to avoid circular imports
updates = None
def get_updates_module():
    global updates
    if updates is None:
        updates = importlib.import_module('script.updates')
    return updates

# Lazy import settings to avoid circular imports
settings = None
def get_settings_module():
    global settings
    if settings is None:
        settings = importlib.import_module('script.settings')
    return settings

# Lazy import help to avoid circular imports
help = None
def get_help_module():
    global help
    if help is None:
        help = importlib.import_module('script.help')
    return help

# Lazy import sponsor to avoid circular imports
sponsor = None
def get_sponsor_module():
    global sponsor
    if sponsor is None:
        sponsor = importlib.import_module('script.sponsor')
    return sponsor

def create_menu_bar(parent):
    """Create and return the application menu bar."""
    menubar = QMenuBar(parent)
    
    # Get the application style for standard icons
    style = parent.style()
    
    # Get translations
    lang = get_language_manager()
    
    # File menu
    file_menu = menubar.addMenu(parent.tr("&File"))
    
    # Export Results action
    export_action = QAction(
        style.standardIcon(QStyle.SP_DialogSaveButton),
        parent.tr("&Export Results..."),
        parent
    )
    export_action.triggered.connect(lambda: self._export_results(parent))
    file_menu.addAction(export_action)
    
    file_menu.addSeparator()
    
    # Exit action with icon
    exit_action = QAction(
        style.standardIcon(QStyle.SP_DialogCancelButton),  # Icon
        "E&xit",  # Text
        parent
    )
    exit_action.setShortcut(QKeySequence.Quit)
    exit_action.triggered.connect(parent.close)
    file_menu.addAction(exit_action)
    
    # View menu
    view_menu = menubar.addMenu(lang.get('menu_view', '&View'))
    
    # Add theme selection submenu
    theme_menu = view_menu.addMenu(lang.get('menu_theme', '&Theme'))
    
    # Get theme manager
    theme_manager = get_theme_manager(QApplication.instance())
    current_theme = theme_manager.get_current_theme() if theme_manager else 'light'
    
    # Add theme actions
    theme_group = QActionGroup(parent)
    theme_group.setExclusive(True)
    
    # Add light theme action
    light_action = theme_menu.addAction(lang.get('theme_light', '&Light'))
    light_action.setCheckable(True)
    light_action.setChecked(current_theme == 'light')
    light_action.setData('light')
    light_action.triggered.connect(lambda: theme_manager.apply_theme('light'))
    theme_group.addAction(light_action)
    
    # Add dark theme action
    dark_action = theme_menu.addAction(lang.get('theme_dark', '&Dark'))
    dark_action.setCheckable(True)
    dark_action.setChecked(current_theme == 'dark')
    dark_action.setData('dark')
    dark_action.triggered.connect(lambda: theme_manager.apply_theme('dark'))
    theme_group.addAction(dark_action)
    
    view_menu.addSeparator()
    
    # Language menu
    language_menu = view_menu.addMenu(lang.get('menu_language', '&Language'))
    
    # Create an action group
    language_group = QActionGroup(parent)
    language_group.setExclusive(True)
    
    # Add language actions from available translations
    lang_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lang')
    if os.path.exists(lang_dir):
        # Create a temporary instance of LanguageManager to get language names
        temp_lang_manager = LanguageManager()
        for lang_file in sorted(os.listdir(lang_dir)):  # Sort languages alphabetically
            if lang_file.endswith('.json'):
                lang_code = os.path.splitext(lang_file)[0]
                # Get language name from the language manager
                lang_name = temp_lang_manager.get_language_name(lang_code)
                if lang_name:
                    action = QAction(lang_name, parent, checkable=True)
                    action.setData(lang_code)
                    # Check if this is the current language
                    if hasattr(parent, 'lang_manager') and parent.lang_manager.get_current_language() == lang_code:
                        action.setChecked(True)
                    # Use a lambda with a default argument to capture the current lang_code
                    action.triggered.connect(lambda checked, code=lang_code: parent.change_language(code))
                    language_group.addAction(action)
                    language_menu.addAction(action)
    
    # Tools menu
    tools_menu = menubar.addMenu(parent.tr("&Tools"))
    
    # Settings action with icon
    settings_text = lang.get_text('menu.settings', '&Settings...')
    settings_action = QAction(
        style.standardIcon(QStyle.SP_ComputerIcon),  # You might want to use a better icon
        settings_text,
        parent
    )
    settings_action.setStatusTip(lang.get_text('menu.settings_tooltip', 'Configure application settings'))
    settings_action.triggered.connect(lambda: get_settings_module().show_settings(parent))
    tools_menu.addAction(settings_action)

    # View Logs action with shortcut and icon
    view_logs_action = QAction(
        style.standardIcon(QStyle.SP_FileDialogListView),  # Icon
        lang.get_text('menu.view_logs', 'View &Logs'),  # Text
        parent
    )
    view_logs_action.setShortcut("Ctrl+L")
    view_logs_action.setStatusTip(lang.get_text('menu.view_logs_tooltip', 'View application logs (Ctrl+L)'))
    view_logs_action.triggered.connect(lambda: view_log.show_log_viewer(parent))
    tools_menu.addAction(view_logs_action)

     # Add a separator
    tools_menu.addSeparator()

    # Check for Updates action
    update_text = lang.get_text('menu.check_for_updates', 'Check for &Updates...')
    update_action = QAction(
        style.standardIcon(QStyle.SP_BrowserReload),  # Using refresh icon for updates
        update_text,
        parent
    )
    update_action.setStatusTip(lang.get_text('menu.check_for_updates_tooltip', 'Check for the latest version'))
    update_action.triggered.connect(lambda: get_updates_module().check_for_updates(parent))
    tools_menu.addAction(update_action)

    # Add a separator before Test menu
    menubar.addSeparator()
    
    # Test menu
    test_menu = menubar.addMenu(lang.get_text("test.label", "Test"))
    
    # System Information Test
    system_info_action = QAction(
        lang.get_text("test.system_info", "System Information"),
        parent
    )
    system_info_action.setStatusTip(lang.get_text("test.system_info_tooltip", "Run system information tests"))
    system_info_action.triggered.connect(lambda: run_system_info_test(parent, lang))
    test_menu.addAction(system_info_action)
    
    # Benchmark Test
    benchmark_action = QAction(
        lang.get_text("test.benchmark", "Run Benchmark"),
        parent
    )
    benchmark_action.setStatusTip(lang.get_text("test.benchmark_tooltip", "Run benchmark tests"))
    benchmark_action.triggered.connect(lambda: run_benchmark_test(parent, lang))
    test_menu.addAction(benchmark_action)
    
    # View Logs
    view_logs_action = QAction(
        lang.get_text("test.view_logs", "View Logs"),
        parent
    )
    view_logs_action.setStatusTip(lang.get_text("test.view_logs_tooltip", "View application logs"))
    view_logs_action.triggered.connect(lambda: view_logs(parent, lang))
    test_menu.addAction(view_logs_action)
    
    # Help menu
    help_text = lang.get_text('menu.help', default='&Help')
    help_menu = menubar.addMenu(help_text)
    
    # Help Contents action
    help_action = QAction(
        style.standardIcon(QStyle.SP_MessageBoxQuestion),  # Icon
        lang.get_text('menu.help_contents', '&Help Contents'),  # Text
        parent
    )
    help_action.triggered.connect(lambda: get_help_module().show_help(parent))
    help_action.setShortcut(QKeySequence.HelpContents)
    help_action.setMenuRole(QAction.NoRole)  # Changed to NoRole to avoid platform-specific menu handling
    help_menu.addAction(help_action)
    
    # About action with icon
    about_text = lang.get_text('menu.about', default=f'&About {APP_NAME} {__version__}')
    about_action = QAction(
        style.standardIcon(QStyle.SP_MessageBoxInformation),  # Icon
        about_text,  # Text
        parent
    )
    about_action.triggered.connect(parent.show_about)
    help_menu.addAction(about_action)
    
    # Add separator
    help_menu.addSeparator()
    
    # Support Development action with QR code
    support_action = QAction(
        style.standardIcon(QStyle.SP_DialogHelpButton),  # Using help icon as placeholder
        lang.get_text('menu.support', '&Support Development...'),
        parent
    )
    support_action.triggered.connect(lambda: get_sponsor_module().show_sponsor_dialog(parent))
    help_menu.addAction(support_action)
    
    return menubar

def run_system_info_test(parent, lang):
    """Run system information test and display results."""
    try:
        log.info("Running system information test")
        from script.benchmark_tests import get_system_info
        system_info = get_system_info()
        os.makedirs('benchmark_results', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'benchmark_results/system_info_{timestamp}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(system_info, f, indent=4, ensure_ascii=False)
        
        # Show success message
        QMessageBox.information(
            parent,
            lang.get_text("test.system_info_title", "System Information"),
            lang.get_text(
                "test.system_info_success", 
                "System information saved to {filename}"
            ).format(filename=filename)
        )
        return system_info
    except Exception as e:
        log.error(f"Error in system info test: {str(e)}", exc_info=True)
        QMessageBox.critical(
            parent,
            lang.get_text("test.error", "Error"),
            lang.get_text(
                "test.system_info_error", 
                "Failed to get system information: {error}"
            ).format(error=str(e))
        )
        raise


def run_benchmark_test(parent, lang):
    """Run benchmark tests and show results."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs('benchmark_results', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Define a simple benchmark function
        def benchmark():
            # A simple CPU-bound operation
            for _ in range(1000):
                [math.sqrt(x) for x in range(1000)]
        
        # Run benchmark using timeit
        number_of_runs = 1000
        total_time = timeit.timeit(benchmark, number=number_of_runs)
        time_per_run = total_time / number_of_runs
        
        # Calculate a performance score (higher is better)
        # This is an arbitrary score for comparison purposes
        performance_score = 1.0 / time_per_run if time_per_run > 0 else 0
        
        # Create result dictionary
        result = {
            'performance_score': performance_score,
            'time_per_run_seconds': time_per_run,
            'total_time_seconds': total_time,
            'number_of_runs': number_of_runs,
            'timestamp': timestamp,
            'python_version': sys.version
        }
        
        # Save results
        filename = f'benchmark_results/benchmark_{timestamp}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        
        # Show results
        QMessageBox.information(
            parent,
            lang.get_text("test.benchmark_title", "Benchmark Results"),
            lang.get_text(
                "test.benchmark_success", 
                "Benchmark completed successfully!\n\n"
                "Performance score: {score:,.2f} (higher is better)\n"
                "Time per run: {time:.6f} seconds\n"
                "Total time: {total_time:.2f} seconds over {runs:,} runs\n\n"
                "Results saved to: {filename}"
            ).format(
                score=result['performance_score'],
                time=result['time_per_run_seconds'],
                total_time=result['total_time_seconds'],
                runs=result['number_of_runs'],
                filename=filename
            )
        )
    except Exception as e:
        QMessageBox.critical(
            parent,
            lang.get_text("test.error", "Error"),
            lang.get_text(
                "test.benchmark_error", 
                "Failed to run benchmark: {error}"
            ).format(error=str(e))
        )


def view_logs(parent, lang):
    """Open the application log file in the default text editor."""
    try:
        log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'benchmark.log')
        if os.path.exists(log_file):
            if sys.platform == 'win32':
                os.startfile(log_file)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', log_file])
            else:
                subprocess.Popen(['xdg-open', log_file])
        else:
            QMessageBox.information(
                parent,
                lang.get_text("test.logs_title", "Log File"),
                lang.get_text("test.logs_not_found", "Log file not found at: {}").format(log_file)
            )
    except Exception as e:
        QMessageBox.critical(
            parent,
            lang.get_text("test.error", "Error"),
            lang.get_text("test.logs_error", "Failed to open log file: {error}").format(error=str(e))
        )
