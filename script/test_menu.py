"""
Simplified test menu for the benchmark application.
"""

from PySide6.QtWidgets import (
    QMenu, QDialog, QVBoxLayout, QScrollArea, QFrame,
    QWidget, QDialogButtonBox, QMessageBox, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox,
    QSpinBox, QDoubleSpinBox, QProgressBar, QTabWidget,
    QGroupBox, QHBoxLayout, QTextEdit, QFileDialog
)
from PySide6.QtGui import QAction, QFont, QTextCursor, QPixmap, QIcon
from PySide6.QtCore import Qt, QSize, QTimer, Signal, QThread, QObject
from script.lang_mgr import get_language_manager, get_text
from script.logger import logger as log

class TestMenu(QMenu):
    """Test menu for the benchmark application."""
    
    def __init__(self, parent=None):
        """Initialize the test menu."""
        super().__init__("&Test", parent)
        self.lang = get_language_manager()
        self.setup_ui()
        self.retranslate_ui()
    
    def setup_ui(self):
        """Set up the test menu UI."""
        # Add test actions here
        self.test_action = QAction("Test Action", self)
        self.test_action.triggered.connect(self.on_test_action)
        self.addAction(self.test_action)
    
    def retranslate_ui(self):
        """Update UI text based on current language."""
        self.test_action.setText(self.lang.get("test_action", "Test Action"))
    
    def on_test_action(self):
        """Handle test action trigger."""
        log.info("Test action triggered")
    
    def setup_ui(self):
        """Set up the test menu UI."""
        # System Information action
        self.system_info_action = QAction(self)
        self.system_info_action.triggered.connect(self.show_system_info)
        self.addAction(self.system_info_action)
        
        # Benchmark Tests action
        self.benchmark_tests_action = QAction(self)
        self.benchmark_tests_action.triggered.connect(self.show_benchmark_tests)
        self.addAction(self.benchmark_tests_action)
        
        # Hardware Monitor action
        self.hw_monitor_action = QAction(self)
        self.hw_monitor_action.triggered.connect(self.show_hardware_monitor)
        self.addAction(self.hw_monitor_action)
        
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
    
    def retranslate_ui(self):
        """Update UI text based on current language."""
        self.setTitle(get_text("test_menu.title", "&Test"))
        self.system_info_action.setText(get_text("test_menu.system_info", "System &Information"))
        self.benchmark_tests_action.setText(get_text("test_menu.benchmark_tests", "&Benchmark Tests"))
        self.hw_monitor_action.setText(get_text("test_menu.hardware_monitor", "&Hardware Monitor"))
        self.export_results_action.setText(get_text("test_menu.export_results", "&Export Results..."))
        self.import_results_action.setText(get_text("test_menu.import_results", "&Import Results..."))
    
    def show_system_info(self):
        """Show system information dialog."""
        from script.system_info import SystemInfoDialog
        dialog = SystemInfoDialog(self.parent())
        dialog.exec()
    
    def show_benchmark_tests(self):
        """Show benchmark tests dialog."""
        from script.benchmark_test import BenchmarkTestDialog
        dialog = BenchmarkTestDialog(self.parent())
        dialog.exec()
    
    def show_hardware_monitor(self):
        """Show hardware monitor dialog."""
        from script.hardware_monitor import HardwareMonitorDialog
        dialog = HardwareMonitorDialog(self.parent())
        dialog.show()
    
    def export_results(self):
        """Export benchmark results to a file."""
        try:
            from script.benchmark_history import get_benchmark_history
            
            # Get the history
            history = get_benchmark_history()
            results = history.get_recent_results(1000)  # Get all results
            
            if not results:
                QMessageBox.information(
                    self.parent(),
                    self.lang.get("export.no_data_title", "No Data"),
                    self.lang.get("export.no_data_msg", "No benchmark results available to export.")
                )
                return
            
            # Get save file name
            default_name = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            file_name, _ = QFileDialog.getSaveFileName(
                self.parent(),
                self.lang.get("export.save_dialog", "Export Benchmark Results"),
                default_name,
                "JSON Files (*.json);;All Files (*)"
            )
            
            if not file_name:
                return  # User cancelled
            
            # Convert results to a list of dicts
            export_data = [{
                'timestamp': r.timestamp,
                'pystones': r.pystones,
                'time_elapsed': r.time_elapsed,
                'iterations': r.iterations,
                'system_info': r.system_info
            } for r in results]
            
            # Save to file
            with open(file_name, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            QMessageBox.information(
                self.parent(),
                self.lang.get("export.success_title", "Export Successful"),
                self.lang.get("export.success_msg", "Benchmark results exported successfully.")
            )
            
        except Exception as e:
            log.error(f"Error exporting results: {e}", exc_info=True)
            QMessageBox.critical(
                self.parent(),
                self.lang.get("error.title", "Error"),
                self.lang.get("export.error_msg", f"Failed to export results: {str(e)}")
            )
    
    def import_results(self):
        """Import benchmark results from a file."""
        try:
            from script.benchmark_history import get_benchmark_history
            
            # Get file to import
            file_name, _ = QFileDialog.getOpenFileName(
                self.parent(),
                self.lang.get("import.open_dialog", "Import Benchmark Results"),
                "",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if not file_name:
                return  # User cancelled
            
            # Load data from file
            with open(file_name, 'r') as f:
                import_data = json.load(f)
            
            # Validate the data
            if not isinstance(import_data, list):
                raise ValueError("Invalid data format: expected a list of results")
            
            # Get the history and import the results
            history = get_benchmark_history()
            imported = 0
            
            for item in import_data:
                try:
                    # Convert old format if needed
                    if 'pystones' not in item or 'time_elapsed' not in item:
                        log.warning(f"Skipping invalid result: {item}")
                        continue
                    
                    # Add to history
                    history.add_result(
                        pystones=item['pystones'],
                        time_elapsed=item['time_elapsed'],
                        iterations=item.get('iterations', 0),
                        system_info=item.get('system_info', {})
                    )
                    imported += 1
                    
                except Exception as e:
                    log.warning(f"Error importing result {item}: {e}")
            
            # Show results
            QMessageBox.information(
                self.parent(),
                self.lang.get("import.complete_title", "Import Complete"),
                self.lang.get(
                    "import.complete_msg", 
                    "Imported {imported} of {total} benchmark results."
                ).format(imported=imported, total=len(import_data))
            )
            
        except Exception as e:
            log.error(f"Error importing results: {e}", exc_info=True)
            QMessageBox.critical(
                self.parent(),
                self.lang.get("error.title", "Error"),
                self.lang.get("import.error_msg", f"Failed to import results: {str(e)}")
            )


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
        # Add a separator if not the first section
        if self.content_layout.count() > 0:
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            self.content_layout.addWidget(line)
        
        # Add section title
        label = QLabel(f"<h3>{title}</h3>")
        self.content_layout.addWidget(label)
        
        # Return a container widget for the section content
        container = QWidget()
        self.content_layout.addWidget(container)
        return container
    
    def add_form_layout(self, parent):
        """Add a form layout to the given parent widget."""
        layout = QFormLayout(parent)
        layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        return layout


if __name__ == "__main__":
    # For testing the dialog
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Test the test menu
    menu = TestMenu()
    menu.show()
    
    sys.exit(app.exec())
