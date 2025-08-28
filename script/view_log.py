"""
Log viewer for the Benchmark application.
"""
import os
from pathlib import Path
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTextEdit, QHBoxLayout,
                             QPushButton, QFileDialog, QMessageBox, QComboBox,
                             QLabel, QHBoxLayout, QComboBox)
from PySide6.QtCore import Qt, QFile, QTextStream
from script import logger
from script.lang_mgr import get_language_manager

class LogViewer(QDialog):
    """A dialog for viewing application logs."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("View Logs")
        self.setMinimumSize(800, 600)
        
        self.log_dir = Path("logs")
        self.current_log_file = None
        
        self.setup_ui()
        self.refresh_log_list()
        
        # Load the most recent log by default
        if self.log_combo.count() > 0:
            self.load_log_file(self.log_combo.currentText())
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Top buttons layout
        button_layout = QHBoxLayout()
        
        # Log file selection
        self.log_combo = QComboBox()
        self.log_combo.currentTextChanged.connect(self.load_log_file)
        button_layout.addWidget(self.log_combo)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_log_list)
        button_layout.addWidget(refresh_btn)
        
        # Clear logs button
        clear_btn = QPushButton("Clear Logs")
        clear_btn.clicked.connect(self.clear_logs)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
        # Filter layout
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by level:"))
        
        # Log level filter
        self.level_combo = QComboBox()
        self.level_combo.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_combo.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.level_combo)
        
        # Search input
        self.search_input = QTextEdit()
        self.search_input.setMaximumHeight(30)
        self.search_input.setPlaceholderText("Search in logs...")
        self.search_input.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.search_input, 1)  # Make search input expandable
        
        layout.addLayout(filter_layout)
        
        # Log content display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFontFamily("Courier New")
        self.log_display.setLineWrapMode(QTextEdit.NoWrap)
        
        # Store original log content for filtering
        self.original_log_content = ""
        
        # Button layout for the bottom of the window
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # Push button to the right
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        # Add widgets to main layout
        layout.addWidget(self.log_display)
        layout.addLayout(button_layout)
    
    def refresh_log_list(self):
        """Refresh the list of available log files."""
        current = self.log_combo.currentText()
        self.log_combo.clear()
        
        log_files = []
        if self.log_dir.exists():
            log_files = sorted(
                self.log_dir.glob("*.log"),
                key=os.path.getmtime,
                reverse=True
            )
            
            for log_file in log_files:
                self.log_combo.addItem(log_file.name)
        
        # Try to restore the previous selection
        if current in [self.log_combo.itemText(i) for i in range(self.log_combo.count())]:
            self.log_combo.setCurrentText(current)
        elif self.log_combo.count() > 0:
            self.log_combo.setCurrentIndex(0)
    
    def on_log_selected(self, log_file):
        """Handle log file selection."""
        if not log_file:
            return
        self.load_log_file(log_file)
    
    def load_log_file(self, log_file_name):
        """Load and display the selected log file."""
        if not log_file_name:
            return
            
        log_file = self.log_dir / log_file_name
        if not log_file.exists():
            return
            
        self.current_log_file = log_file
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.original_log_content = content
                self.apply_filters()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not read log file: {e}")
    
    def apply_filters(self):
        """Apply the current filters to the log content."""
        if not hasattr(self, 'original_log_content') or not self.original_log_content:
            return
            
        level_filter = self.level_combo.currentText()
        search_text = self.search_input.toPlainText().lower()
        
        # Split content into lines and filter
        lines = self.original_log_content.split('\n')
        filtered_lines = []
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
                
            # Extract log level from the line (format: 'YYYY-MM-DD HH:MM:SS - LoggerName - LEVEL - Message')
            line_upper = line.upper()
            log_level = None
            
            # Find the log level in the line
            for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                if f' - {level} - ' in line_upper:
                    log_level = level
                    break
            
            # Apply level filter
            if level_filter != "ALL" and (not log_level or log_level != level_filter):
                continue
                
            # Apply search text filter
            if search_text and search_text.lower() not in line.lower():
                continue
                
            filtered_lines.append(line)
        
        # Update the display
        self.log_display.setPlainText('\n'.join(filtered_lines))
        self.log_display.verticalScrollBar().setValue(
            self.log_display.verticalScrollBar().maximum()
        )
    
    def clear_logs(self):
        """Clear all log files after confirmation."""
        reply = QMessageBox.question(
            self,
            'Clear Logs',
            'Are you sure you want to clear all log files?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if logger.clear_logs():
                self.refresh_log_list()
                self.log_display.clear()
                QMessageBox.information(
                    self,
                    "Success",
                    "All log files have been cleared."
                )

def show_log_viewer(parent=None):
    """Show the log viewer dialog."""
    dialog = LogViewer(parent)
    dialog.exec_()

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    viewer = LogViewer()
    viewer.show()
    sys.exit(app.exec_())
