#!/usr/bin/env python3
"""
Benchmark with PySide6 GUI - Clean Start
"""
import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, 
    QPushButton, QMenuBar, QStatusBar
)
from PySide6.QtCore import Qt, QSettings

# Local imports
from script.version import __version__, APP_NAME, APP_DESCRIPTION
from script.logger import logger
from script.lang_mgr import get_language_manager, get_text
from script.menu import create_menu_bar
from script.test_menu import TestMenu
from script.theme_manager import get_theme_manager

log = logger

class BenchmarkApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize language manager
        self.lang = get_language_manager()
        
        # Set window properties
        self.setWindowTitle(f"{APP_NAME} v{__version__}")
        self.setMinimumSize(800, 600)
        
        # Initialize UI
        self.setup_ui()
        
        # Apply theme
        self.theme_manager = get_theme_manager(self)
        if self.theme_manager:
            self.theme_manager.apply_theme()
        
        # Load settings
        self.load_settings()
        
        # Log startup
        log.info(f"{APP_NAME} v{__version__} started")
        log.info(f"Python {sys.version}")
        log.info(f"Working directory: {os.getcwd()}")
    
    def setup_ui(self):
        """Set up the main UI components"""
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.statusBar().showMessage(get_text("app.ready", "Ready"))
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add a welcome label
        welcome_label = QLabel(get_text("app.welcome", f"Welcome to {APP_NAME}"))
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 24px; margin: 20px;")
        layout.addWidget(welcome_label)
        
        # Add a description label
        desc_label = QLabel(APP_DESCRIPTION)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("margin: 0 40px 20px 40px;")
        layout.addWidget(desc_label)
        
        # Add a start benchmark button
        self.start_button = QPushButton(get_text("app.start_benchmark", "Start Benchmark"))
        self.start_button.setMinimumHeight(50)
        self.start_button.clicked.connect(self.on_start_clicked)
        layout.addWidget(self.start_button)
        
        # Add some spacing
        layout.addStretch()
    
    def create_menu_bar(self):
        """Create the application menu bar"""
        # Create the main menu bar
        menu_bar = create_menu_bar(self)
        
        # Add Test menu
        test_menu = TestMenu(self)
        menu_bar.addMenu(test_menu)
        
        self.setMenuBar(menu_bar)
    
    def load_settings(self):
        """Load application settings"""
        settings = QSettings("Nsfr750", "Benchmark")
        self.restoreGeometry(settings.value("geometry"))
        self.restoreState(settings.value("windowState"))
    
    def save_settings(self):
        """Save application settings"""
        settings = QSettings("Nsfr750", "Benchmark")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
    
    def on_start_clicked(self):
        """Handle start benchmark button click"""
        log.info("Start benchmark button clicked")
        self.statusBar().showMessage(get_text("app.starting_benchmark", "Starting benchmark..."))
        # TODO: Implement benchmark start
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.save_settings()
        event.accept()
        
    def show_about(self):
        """Show the About dialog"""
        from PySide6.QtWidgets import QMessageBox
        from script.version import APP_NAME, APP_DESCRIPTION, __version__
        
        about_text = (
            f"<b>{APP_NAME}</b> v{__version__}<br><br>"
            f"{APP_DESCRIPTION}<br><br>"
            "<b>Author:</b> Nsfr750<br>"
            "<b>Email:</b> nsfr750@yandex.com<br>"
            "<b>GitHub:</b> <a href='https://github.com/Nsfr750'>github.com/Nsfr750</a><br>"
            "<b>License:</b> GPLv3<br><br>"
            "© 2025 Nsfr750. All rights reserved."
        )
        
        msg = QMessageBox()
        msg.setWindowTitle(get_text("menu.about", "About"))
        msg.setText(about_text)
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()

def main():
    """Main application entry point"""
    try:
        # Set up the application
        app = QApplication(sys.argv)
        app.setApplicationName("Benchmark")
        app.setApplicationVersion(__version__)
        app.setOrganizationName("Nsfr750")
        
        # Set application style
        app.setStyle('Fusion')
        
        # Create and show main window
        window = BenchmarkApp()
        window.show()
        
        # Start the event loop
        sys.exit(app.exec())
        
    except Exception as e:
        log.error(f"Application error: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
