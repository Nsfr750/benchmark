"""
Export dialog for the Benchmark application.
Allows users to export benchmark results in different formats.
"""
import os
from pathlib import Path
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QFileDialog, QMessageBox,
                             QFormLayout, QDialogButtonBox)
from PySide6.QtCore import Qt

from script.test_script.export_results import ResultExporter, get_export_formats

class ExportDialog(QDialog):
    """Dialog for exporting benchmark results."""
    
    def __init__(self, parent=None, results=None, default_dir=None):
        """Initialize the export dialog.
        
        Args:
            parent: Parent widget
            results: Benchmark results to export
            default_dir: Default directory for saving files
        """
        super().__init__(parent)
        self.results = results or {}
        self.default_dir = default_dir or os.path.expanduser("~/Downloads")
        self.export_formats = get_export_formats()
        
        self.setWindowTitle("Export Results")
        self.setMinimumWidth(500)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Format selection
        form_layout = QFormLayout()
        
        # Format combo box
        self.format_combo = QComboBox()
        for fmt, desc in self.export_formats.items():
            self.format_combo.addItem(f"{fmt.upper()} - {desc}", fmt)
        form_layout.addRow("Format:", self.format_combo)
        
        # File path selection
        file_layout = QHBoxLayout()
        self.file_edit = QLabel("")
        self.file_edit.setStyleSheet("background-color: white; border: 1px solid #c0c0c0; padding: 2px;")
        self.file_edit.setMinimumHeight(25)
        file_layout.addWidget(self.file_edit, 1)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_file)
        file_layout.addWidget(browse_btn)
        
        form_layout.addRow("Save to:", file_layout)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        
        # Update file path when format changes
        self.format_combo.currentIndexChanged.connect(self._update_file_path)
        self._update_file_path()
    
    def _browse_file(self):
        """Open file dialog to select save location."""
        fmt = self.format_combo.currentData()
        file_types = f"{fmt.upper()} (*.{fmt})"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save As",
            self._get_default_file_path(),
            file_types
        )
        
        if file_path:
            self.file_edit.setText(file_path)
    
    def _update_file_path(self):
        """Update the default file path based on selected format."""
        self.file_edit.setText(self._get_default_file_path())
    
    def _get_default_file_path(self):
        """Get default file path based on selected format."
        
        Returns:
            str: Default file path
        """
        fmt = self.format_combo.currentData()
        timestamp = self.results.get('timestamp', '').replace(':', '-').replace(' ', '_')
        filename = f"benchmark_results_{timestamp}.{fmt}"
        return str(Path(self.default_dir) / filename)
    
    def accept(self):
        """Handle OK button click."""
        file_path = self.file_edit.text().strip()
        if not file_path:
            QMessageBox.warning(self, "Error", "Please specify a file path.")
            return
        
        fmt = self.format_combo.currentData()
        
        try:
            if fmt == 'json':
                success = ResultExporter.export_to_json(self.results, file_path)
            elif fmt == 'csv':
                success = ResultExporter.export_to_csv(self.results, file_path)
            elif fmt == 'txt':
                success = ResultExporter.export_to_text(self.results, file_path)
            else:
                QMessageBox.warning(self, "Error", f"Unsupported format: {fmt}")
                return
            
            if success:
                QMessageBox.information(self, "Success", f"Results exported successfully to:\n{file_path}")
                super().accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to export results.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while exporting:\n{str(e)}")
