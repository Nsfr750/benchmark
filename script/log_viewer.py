"""
Log viewer dialog for the Benchmark application.
"""
import os
import sys
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QHBoxLayout, QPushButton,
    QFileDialog, QMessageBox, QApplication, QLabel
)
from PySide6.QtCore import Qt, QFile, QTextStream, QSize
from PySide6.QtGui import QFont, QIcon, QTextCursor
from script.lang_mgr import get_language_manager, get_text

class LogViewer(QDialog):
    """A dialog for viewing application logs."""
    
    def __init__(self, parent=None):
        """Initialize the log viewer dialog."""
        super().__init__(parent)
        self.lang = get_language_manager()
        self.setWindowTitle(get_text('log_viewer.title', 'Log Viewer'))
        self.setMinimumSize(800, 600)
        self.setup_ui()
        self.load_log_file()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Log display
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont('Consolas', 10))
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Refresh button
        self.refresh_btn = QPushButton(get_text('log_viewer.refresh', '&Refresh'))
        self.refresh_btn.clicked.connect(self.load_log_file)
        
        # Clear button
        self.clear_btn = QPushButton(get_text('log_viewer.clear', 'C&lear Logs'))
        self.clear_btn.clicked.connect(self.clear_logs)
        
        # Save button
        self.save_btn = QPushButton(get_text('log_viewer.save_as', '&Save As...'))
        self.save_btn.clicked.connect(self.save_log_as)
        
        # Close button
        self.close_btn = QPushButton(get_text('common.close', '&Close'))
        self.close_btn.clicked.connect(self.accept)
        
        # Add buttons to layout
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.close_btn)
        
        # Add widgets to main layout
        layout.addWidget(self.log_text)
        layout.addLayout(button_layout)
    
    def load_log_file(self):
        """Load the log file contents into the text edit."""
        try:
            log_file = self.get_log_file_path()
            
            if not os.path.exists(log_file):
                self.log_text.setPlainText(get_text('log_viewer.no_logs', 'No log file found.'))
                return
            
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            self.log_text.setPlainText(log_content)
            self.log_text.moveCursor(QTextCursor.End)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                get_text('error.title', 'Error'),
                get_text('log_viewer.load_error', 'Error loading log file: {}').format(str(e))
            )
    
    def clear_logs(self):
        """Clear the log file after user confirmation."""
        reply = QMessageBox.question(
            self,
            get_text('log_viewer.confirm_clear', 'Confirm Clear'),
            get_text('log_viewer.confirm_clear_msg', 'Are you sure you want to clear all logs? This cannot be undone.'),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                log_file = self.get_log_file_path()
                if os.path.exists(log_file):
                    with open(log_file, 'w', encoding='utf-8') as f:
                        f.write('')
                    self.load_log_file()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    get_text('error.title', 'Error'),
                    get_text('log_viewer.clear_error', 'Error clearing logs: {}').format(str(e))
                )
    
    def save_log_as(self):
        """Save the current log content to a file."""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            get_text('log_viewer.save_dialog', 'Save Log As'),
            '',
            'Log Files (*.log);;Text Files (*.txt);;All Files (*)'
        )
        
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
            except Exception as e:
                QMessageBox.critical(
                    self,
                    get_text('error.title', 'Error'),
                    get_text('log_viewer.save_error', 'Error saving log file: {}').format(str(e))
                )
    
    def get_log_file_path(self):
        """Get the path to the current log file."""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        return os.path.join(log_dir, 'benchmark.log')


def view_logs(parent=None):
    """
    Show the log viewer dialog.
    
    Args:
        parent: Parent widget for the dialog
    """
    dialog = LogViewer(parent)
    dialog.exec()


if __name__ == "__main__":
    # For testing the log viewer
    app = QApplication(sys.argv)
    viewer = LogViewer()
    viewer.show()
    sys.exit(app.exec())
