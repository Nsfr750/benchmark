"""
Menu bar and related functionality for the Benchmark application.
Combines the functionality of menu.py and test_menu.py.
"""
import os
import importlib
import logging
import json
import sys
import subprocess
import timeit
import math
import webbrowser
from datetime import datetime

from PySide6.QtWidgets import (
    QMenuBar, QMenu, QStyle, QApplication, QMessageBox, QDialog, QVBoxLayout,
    QScrollArea, QFrame, QWidget, QDialogButtonBox, QFormLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox,
    QProgressBar, QTabWidget, QGroupBox, QHBoxLayout, QTextEdit, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QTextBrowser
)
from PySide6.QtGui import QKeySequence, QIcon, QAction, QActionGroup, QFont, QTextCursor, QPixmap
from PySide6.QtCore import Qt, Signal, QObject, QSize, QThread, QTimer, QSettings

from script.version import APP_NAME, APP_DESCRIPTION, __version__
from script.lang_mgr import get_language_manager, get_text
from script.theme_manager import get_theme_manager
from script.test_script.system_info import get_system_info, save_system_info
from script.test_script.benchmark_tests import BenchmarkSuite
from script.test_script.export_dialog import ExportDialog
from script.logger import logger as log

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

class TestDialog(QDialog):
    """Base dialog for test windows."""
    
    def __init__(self, title, parent=None):
        """Initialize the test dialog."""
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(800, 600)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Add a scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        # Create a widget for the scroll area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add content to the scroll area
        scroll.setWidget(self.content_widget)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        
        # Add widgets to layout
        layout.addWidget(scroll)
        layout.addWidget(button_box)
    
    def add_section(self, title):
        """Add a section to the dialog."""
        # Add a line separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.content_layout.addWidget(line)
        
        # Add section title
        title_label = QLabel(f"<h3>{title}</h3>")
        self.content_layout.addWidget(title_label)
        
        return self.content_layout
    
    def add_form_layout(self, parent):
        """Add a form layout to the given parent widget."""
        form_layout = QFormLayout()
        parent.addLayout(form_layout)
        return form_layout

class TestMenu(QMenu):
    """Test menu for the benchmark application."""
    
    def __init__(self, parent=None):
        """Initialize the test menu."""
        super().__init__(get_text('test.label', '&Test'), parent)
        self.lang = get_language_manager()
        self.setup_ui()
        self.retranslate_ui()
    
    def setup_ui(self):
        """Set up the test menu UI."""
        # System Information action
        self.system_info_action = QAction(self)
        self.system_info_action.triggered.connect(self.show_system_info)
        self.addAction(self.system_info_action)
        
        # Benchmark Tests action
        self.benchmark_tests_action = QAction(self)
        self.benchmark_tests_action.triggered.connect(self.run_benchmark_tests)
        self.addAction(self.benchmark_tests_action)
        
        # Hardware Monitor action
        self.hardware_monitor_action = QAction(self)
        self.hardware_monitor_action.triggered.connect(self.show_hardware_monitor)
        self.addAction(self.hardware_monitor_action)
        
        # Pystone Test action
        self.pystone_test_action = QAction(self)
        self.pystone_test_action.triggered.connect(self.run_pystone_test)
        self.addAction(self.pystone_test_action)
        
        # Add separator
        self.addSeparator()
        
        # View Logs action
        self.view_logs_action = QAction(self)
        self.view_logs_action.triggered.connect(self.view_logs)
        self.addAction(self.view_logs_action)
        
        # View History action
        self.view_history_action = QAction(self)
        self.view_history_action.triggered.connect(self.view_history)
        self.addAction(self.view_history_action)
        
        # Add separator
        self.addSeparator()
        
        # Export Results action
        self.export_results_action = QAction(self)
        self.export_results_action.triggered.connect(self.export_results)
        self.addAction(self.export_results_action)
        
        # Import Results action
        self.import_results_action = QAction(self)
        self.import_results_action.triggered.connect(self.import_results)
        self.addAction(self.import_results_action)
        
        # Add separator
        self.addSeparator()
        
        # Test Action
        self.test_action = QAction(self)
        self.test_action.triggered.connect(self.test_action_triggered)
        self.addAction(self.test_action)
    
    def retranslate_ui(self):
        """Update the UI text based on the current language."""
        self.setTitle(get_text('test.label', '&Test'))
        
        # Update action texts
        self.system_info_action.setText(get_text('test.system_info', 'System &Information'))
        self.system_info_action.setStatusTip(get_text('test.system_info_tooltip', 'View detailed system information'))
        
        self.benchmark_tests_action.setText(get_text('test.benchmark', '&Benchmark Tests'))
        self.benchmark_tests_action.setStatusTip(get_text('test.benchmark_tooltip', 'Run benchmark tests'))
        
        self.hardware_monitor_action.setText(get_text('test.hardware_monitor', '&Hardware Monitor'))
        self.hardware_monitor_action.setStatusTip(get_text('test.hardware_monitor_tooltip', 'View hardware monitoring information'))
        
        self.view_logs_action.setText(get_text('test.view_logs', 'View &Logs'))
        self.view_logs_action.setStatusTip(get_text('test.view_logs_tooltip', 'View application logs'))
        
        self.view_history_action.setText(get_text('test.view_history', 'View &History'))
        self.view_history_action.setStatusTip(get_text('test.view_history_tooltip', 'View test history'))
        
        self.export_results_action.setText(get_text('test.export_results', '&Export Results...'))
        self.export_results_action.setStatusTip(get_text('test.export_results_tooltip', 'Export test results to a file'))
        
        self.import_results_action.setText(get_text('test.import_results', '&Import Results...'))
        self.import_results_action.setStatusTip(get_text('test.import_results_tooltip', 'Import test results from a file'))
        
        self.pystone_test_action.setText(get_text('test.pystone_test', '&Pystone Benchmark'))
        self.pystone_test_action.setStatusTip(get_text('test.pystone_tooltip', 'Run the Pystone benchmark test'))
        
        self.test_action.setText(get_text('test.test_action', 'Test Action'))
        self.test_action.setStatusTip(get_text('test.test_tooltip', 'Test action for development'))
    
    def show_system_info(self):
        """Show system information dialog."""
        from script.test_script.system_info import SystemInfoDialog
        dialog = SystemInfoDialog(self.parent())
        dialog.exec()
    
    def run_benchmark_tests(self):
        """Run benchmark tests."""
        from script.test_script.benchmark_tests import BenchmarkTestDialog
        dialog = BenchmarkTestDialog(self.parent())
        dialog.exec()
    
    def show_hardware_monitor(self):
        """Show hardware monitor dialog."""
        from script.test_script.hardware_monitor import HardwareMonitorDialog
        dialog = HardwareMonitorDialog(self.parent())
        dialog.show()
    
    def view_logs(self):
        """View application logs."""
        from script.log_viewer import LogViewer
        viewer = LogViewer(self.parent())
        viewer.show()
    
    def view_history(self):
        """View test history."""
        from script.test_script.history_dialog import HistoryDialog
        dialog = HistoryDialog(self.parent())
        dialog.exec()
    
    def export_results(self):
        """Export test results to a file."""
        file_name, _ = QFileDialog.getSaveFileName(
            self.parent(),
            get_text('test.export_dialog', 'Export Results'),
            '',
            'JSON Files (*.json);;All Files (*)'
        )
        
        if file_name:
            try:
                # Get the results to export
                from script.history import get_test_history
                history = get_test_history()
                history.export_to_file(file_name)
                
                QMessageBox.information(
                    self.parent(),
                    get_text('test.export_success', 'Export Successful'),
                    get_text('test.export_success_msg', 'Results exported successfully.')
                )
            except Exception as e:
                log.error(f"Error exporting results: {e}")
                QMessageBox.critical(
                    self.parent(),
                    get_text('test.export_error', 'Export Error'),
                    get_text('test.export_error_msg', 'Failed to export results: {}').format(str(e))
                )
    
    def import_results(self):
        """Import test results from a file."""
        file_name, _ = QFileDialog.getOpenFileName(
            self.parent(),
            get_text('test.import_dialog', 'Import Results'),
            '',
            'JSON Files (*.json);;All Files (*)'
        )
        
        if file_name:
            try:
                # Import the results
                from script.history import get_test_history
                history = get_test_history()
                count = history.import_from_file(file_name)
                
                QMessageBox.information(
                    self.parent(),
                    get_text('test.import_success', 'Import Successful'),
                    get_text('test.import_success_msg', 'Successfully imported {} results.').format(count)
                )
            except Exception as e:
                log.error(f"Error importing results: {e}")
                QMessageBox.critical(
                    self.parent(),
                    get_text('test.import_error', 'Import Error'),
                    get_text('test.import_error_msg', 'Failed to import results: {}').format(str(e))
                )
    
    def run_pystone_test(self):
        """Run the Pystone benchmark test."""
        try:
            from script.test_script.pystone_test import run_pystones_test
            from script.test_script.pystone_dialog import PystoneDialog
            
            # Create and show the Pystone test dialog
            dialog = PystoneDialog(self.parent())
            if dialog.exec_() == QDialog.Accepted:
                # Get the number of loops from the dialog
                loops = dialog.get_loops()
                
                # Run the test
                results = run_pystones_test(loops)
                
                # Show results
                QMessageBox.information(
                    self.parent(),
                    get_text('test.pystone_results', 'Pystone Results'),
                    get_text('test.pystone_results_text', 
                           'Pystone benchmark completed.\n\n' +
                           f"Pystones per second: {results['pystones']:.2f}\n" +
                           f"Time elapsed: {results['time_elapsed']:.2f} seconds\n" +
                           f"Loops: {results['loops']}")
                )
                
        except Exception as e:
            QMessageBox.critical(
                self.parent(),
                get_text('test.error', 'Error'),
                get_text('test.pystone_error', 'Failed to run Pystone test: {}').format(str(e))
            )
    
    def test_action_triggered(self):
        """Handle test action triggered."""
        QMessageBox.information(
            self.parent(),
            get_text('test.test_action', 'Test Action'),
            get_text('test.test_message', 'This is development test action.')
        )

def create_menu_bar(parent):
    """Create and return the application menu bar."""
    def change_language(lang_code, menubar):
        """Change the application language."""
        lang_manager = get_language_manager()
        if lang_manager.set_language(lang_code):
            # Save the language preference
            settings = QSettings("Nsfr750", "Benchmark")
            settings.setValue("language", lang_code)
            
            # Get the main window
            main_window = menubar.parent()
            
            # Rebuild the UI
            main_window.setup_ui()
            
            # Update window title
            main_window.setWindowTitle(f"{APP_NAME} v{__version__}")
        else:
            QMessageBox.warning(
                menubar.parent(),
                get_text('error.title', 'Error'),
                get_text('error.language_change', 'Failed to change language')
            )
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
    export_action.triggered.connect(lambda: parent.export_results())
    file_menu.addAction(export_action)
    
    file_menu.addSeparator()
    
    # Exit action with icon
    exit_action = QAction(
        style.standardIcon(QStyle.SP_DialogCancelButton),
        parent.tr("E&xit"),
        parent
    )
    exit_action.setShortcut(QKeySequence.Quit)
    exit_action.triggered.connect(parent.close)
    file_menu.addAction(exit_action)
    
    # Edit menu
    edit_menu = menubar.addMenu(parent.tr("&Edit"))
    
    # Undo action
    undo_action = QAction(
        style.standardIcon(QStyle.SP_ArrowBack),
        parent.tr("&Undo"),
        parent
    )
    undo_action.setShortcut(QKeySequence.Undo)
    edit_menu.addAction(undo_action)
    
    # Redo action
    redo_action = QAction(
        style.standardIcon(QStyle.SP_ArrowForward),
        parent.tr("&Redo"),
        parent
    )
    redo_action.setShortcut(QKeySequence.Redo)
    edit_menu.addAction(redo_action)
    
    edit_menu.addSeparator()
    
    # Cut action
    cut_action = QAction(
        style.standardIcon(QStyle.SP_DialogResetButton),
        parent.tr("Cu&t"),
        parent
    )
    cut_action.setShortcut(QKeySequence.Cut)
    edit_menu.addAction(cut_action)
    
    # Copy action
    copy_action = QAction(
        style.standardIcon(QStyle.SP_DialogSaveButton),
        parent.tr("&Copy"),
        parent
    )
    copy_action.setShortcut(QKeySequence.Copy)
    edit_menu.addAction(copy_action)
    
    # Paste action
    paste_action = QAction(
        style.standardIcon(QStyle.SP_DialogOpenButton),
        parent.tr("&Paste"),
        parent
    )
    paste_action.setShortcut(QKeySequence.Paste)
    edit_menu.addAction(paste_action)
    
    # View menu
    view_menu = menubar.addMenu(parent.tr("&View"))
    
    # Zoom In action
    zoom_in_action = QAction(
        style.standardIcon(QStyle.SP_TitleBarShadeButton),
        parent.tr("Zoom &In"),
        parent
    )
    zoom_in_action.setShortcut(QKeySequence.ZoomIn)
    view_menu.addAction(zoom_in_action)
    
    # Zoom Out action
    zoom_out_action = QAction(
        style.standardIcon(QStyle.SP_TitleBarUnshadeButton),
        parent.tr("Zoom &Out"),
        parent
    )
    zoom_out_action.setShortcut(QKeySequence.ZoomOut)
    view_menu.addAction(zoom_out_action)
    
    view_menu.addSeparator()
    
    # Full Screen action
    full_screen_action = QAction(
        style.standardIcon(QStyle.SP_TitleBarMaxButton),
        parent.tr("&Full Screen"),
        parent
    )
    full_screen_action.setShortcut(QKeySequence.FullScreen)
    full_screen_action.triggered.connect(parent.toggle_fullscreen)
    view_menu.addAction(full_screen_action)
    
    # Tools menu
    tools_menu = menubar.addMenu(parent.tr("&Tools"))
    
    # Options action
    options_action = QAction(
        style.standardIcon(QStyle.SP_ComputerIcon),
        parent.tr("&Options..."),
        parent
    )
    options_action.triggered.connect(parent.show_options)
    tools_menu.addAction(options_action)
    
    # System Log action
    system_log_action = QAction(
        style.standardIcon(QStyle.SP_FileDialogDetailedView),
        parent.tr("S&ystem Log"),
        parent
    )
    system_log_action.triggered.connect(parent.view_logs)
    tools_menu.addAction(system_log_action)
    
    tools_menu.addSeparator()
    
    # Update action
    update_action = QAction(
        style.standardIcon(QStyle.SP_BrowserReload),
        parent.tr("Check for &Updates..."),
        parent
    )
    update_action.triggered.connect(lambda: get_updates_module().check_for_updates(parent))
    tools_menu.addAction(update_action)
    
    # Language menu
    language_menu = QMenu(get_text('menu.language', '&Language'), menubar)
    
    # Create a QActionGroup to make language selection exclusive
    language_group = QActionGroup(menubar)
    language_group.setExclusive(True)
    
    # Get available languages
    lang_manager = get_language_manager()
    current_lang = lang_manager.get_current_language()
    
    # Add language actions
    for lang_code in lang_manager.get_available_languages():
        lang_name = {
            'en': 'English',
            'it': 'Italiano'
        }.get(lang_code, lang_code.upper())
        
        action = QAction(lang_name, menubar, checkable=True)
        action.setData(lang_code)
        action.setChecked(lang_code == current_lang)
        action.triggered.connect(lambda checked, code=lang_code: 
                               change_language(code, menubar))
        language_menu.addAction(action)
        language_group.addAction(action)
    
    menubar.addMenu(language_menu)
    
    # Add a separator before Help menu
    menubar.addSeparator()
    
    # Help menu
    help_menu = menubar.addMenu(parent.tr("&Help"))
    
    # Help Contents action
    help_action = QAction(
        style.standardIcon(QStyle.SP_MessageBoxQuestion),
        parent.tr("&Help Contents"),
        parent
    )
    help_action.triggered.connect(lambda: get_help_module().show_help(parent))
    help_action.setShortcut(QKeySequence.HelpContents)
    help_menu.addAction(help_action)
    
    # Add separator
    help_menu.addSeparator()
    
    # About action with icon
    about_action = QAction(
        style.standardIcon(QStyle.SP_MessageBoxInformation),
        parent.tr(f"&About {APP_NAME}"),
        parent
    )
    from script.about import show_about
    about_action.triggered.connect(lambda: show_about(parent))
    help_menu.addAction(about_action)
    
    # Add separator
    help_menu.addSeparator()
    
    # Documentation action
    docs_action = QAction(
        style.standardIcon(QStyle.SP_FileDialogContentsView),
        parent.tr("&Documentation"),
        parent
    )
    docs_action.triggered.connect(lambda: webbrowser.open("https://github.com/Nsfr750/benchmark/wiki"))
    help_menu.addAction(docs_action)
    
    # Add separator
    help_menu.addSeparator()
    
    # Support Development action with QR code
    support_action = QAction(
        style.standardIcon(QStyle.SP_FileDialogDetailedView),
        parent.tr("&Support Development..."),
        parent
    )
    support_action.triggered.connect(lambda: get_sponsor_module().show_sponsor_dialog(parent))
    help_menu.addAction(support_action)
    
    return menubar

def run_system_info_test(parent, lang):
    """Run system information test and display results."""
    try:
        log.info("Running system information test")
        system_info = get_system_info()
        
        # Create a dialog to display the results
        dialog = QDialog(parent)
        dialog.setWindowTitle(lang.get_text('test.system_info', 'System Information'))
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Add a text browser to display the results
        text_browser = QTextBrowser()
        text_browser.setFont(QFont('Courier New', 10))
        
        # Format the system information as JSON with indentation
        system_info_json = json.dumps(system_info, indent=4, sort_keys=True)
        text_browser.setPlainText(system_info_json)
        
        # Add a button to save the results to a file
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Close)
        button_box.accepted.connect(lambda: save_system_info_to_file(system_info, parent))
        button_box.rejected.connect(dialog.reject)
        
        # Add widgets to layout
        layout.addWidget(text_browser)
        layout.addWidget(button_box)
        
        # Show the dialog
        dialog.exec()
        
    except Exception as e:
        log.error(f"Error running system information test: {e}")
        QMessageBox.critical(
            parent,
            lang.get_text('test.error', 'Error'),
            lang.get_text('test.system_info_error', 'Failed to get system information: {}').format(str(e))
        )

def run_benchmark_test(parent, lang):
    """Run benchmark tests and show results."""
    try:
        log.info("Running benchmark test")
        
        # Create a progress dialog
        progress = QProgressDialog(
            lang.get_text('test.benchmark_running', 'Running benchmark, please wait...'),
            lang.get_text('common.cancel', 'Cancel'),
            0, 100,
            parent
        )
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        
        # Create a benchmark suite
        suite = BenchmarkSuite()
        
        # Run the benchmark
        results = suite.run(progress_callback=progress.setValue)
        
        # Check if the benchmark was canceled
        if progress.wasCanceled():
            log.info("Benchmark test canceled by user")
            return
        
        # Create a dialog to display the results
        dialog = QDialog(parent)
        dialog.setWindowTitle(lang.get_text('test.benchmark_results', 'Benchmark Results'))
        dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Add a table to display the results
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels([
            lang.get_text('test.test_name', 'Test'),
            lang.get_text('test.score', 'Score'),
            lang.get_text('test.unit', 'Unit')
        ])
        
        # Add the results to the table
        table.setRowCount(len(results))
        for i, (name, result) in enumerate(results.items()):
            table.setItem(i, 0, QTableWidgetItem(name))
            table.setItem(i, 1, QTableWidgetItem(f"{result['score']:.2f}"))
            table.setItem(i, 2, QTableWidgetItem(result.get('unit', '')))
        
        # Resize columns to fit content
        table.resizeColumnsToContents()
        
        # Add a button to save the results to a file
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Close)
        button_box.accepted.connect(lambda: save_benchmark_results(results, parent))
        button_box.rejected.connect(dialog.reject)
        
        # Add widgets to layout
        layout.addWidget(table)
        layout.addWidget(button_box)
        
        # Show the dialog
        dialog.exec()
        
    except Exception as e:
        log.error(f"Error running benchmark test: {e}")
        QMessageBox.critical(
            parent,
            lang.get_text('test.error', 'Error'),
            lang.get_text('test.benchmark_error', 'Failed to run benchmark: {}').format(str(e))
        )

def view_logs(parent, lang):
    """Open the log viewer dialog to display application logs."""
    try:
        from script.view_log import show_log_viewer
        show_log_viewer(parent)
    except Exception as e:
        QMessageBox.critical(
            parent,
            lang.get_text('test.error', 'Error'),
            f"Failed to open log viewer: {str(e)}"
        )

def save_system_info_to_file(system_info, parent):
    """Save system information to a file."""
    file_name, _ = QFileDialog.getSaveFileName(
        parent,
        'Save System Information',
        '',
        'JSON Files (*.json);;All Files (*)'
    )
    
    if file_name:
        try:
            with open(file_name, 'w') as f:
                json.dump(system_info, f, indent=4)
            
            QMessageBox.information(
                parent,
                'Success',
                f'System information saved to {file_name}'
            )
        except Exception as e:
            QMessageBox.critical(
                parent,
                'Error',
                f'Failed to save system information: {str(e)}'
            )

def save_benchmark_results(results, parent):
    """Save benchmark results to a file."""
    file_name, _ = QFileDialog.getSaveFileName(
        parent,
        'Save Benchmark Results',
        '',
        'JSON Files (*.json);;All Files (*)'
    )
    
    if file_name:
        try:
            # Convert the results to a serializable format
            serializable_results = {}
            for name, result in results.items():
                serializable_results[name] = {
                    'score': result['score'],
                    'unit': result.get('unit', ''),
                    'times': result.get('times', [])
                }
            
            with open(file_name, 'w') as f:
                json.dump(serializable_results, f, indent=4)
            
            QMessageBox.information(
                parent,
                'Success',
                f'Benchmark results saved to {file_name}'
            )
        except Exception as e:
            QMessageBox.critical(
                parent,
                'Error',
                f'Failed to save benchmark results: {str(e)}'
            )

if __name__ == "__main__":
    # For testing the menu
    app = QApplication(sys.argv)
    
    # Set the application style
    app.setStyle('Fusion')
    
    # Create a main window
    window = QMainWindow()
    window.setWindowTitle('Test Menu')
    window.setGeometry(100, 100, 800, 600)
    
    # Create the menu bar
    menu_bar = create_menu_bar(window)
    window.setMenuBar(menu_bar)
    
    # Show the window
    window.show()
    
    # Run the application
    sys.exit(app.exec())
