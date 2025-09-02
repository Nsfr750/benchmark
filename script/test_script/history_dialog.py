"""
Dialog for displaying benchmark history.
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QHeaderView, QMessageBox,
                             QAbstractItemView, QLabel, QComboBox, QDateEdit, QSizePolicy)
from PySide6.QtCore import Qt, QDate, Signal, QTimer
from PySide6.QtGui import QBrush, QColor, QFont
from datetime import datetime, timedelta
import logging
from typing import List, Optional, Tuple

from .benchmark_history import BenchmarkResult, get_benchmark_history
from script.lang_mgr import get_language_manager, get_text

log = logging.getLogger(__name__)

class HistoryDialog(QDialog):
    """Dialog for displaying and managing benchmark history."""
    
    # Signal emitted when a result is selected for comparison
    result_selected = Signal(BenchmarkResult)
    
    def __init__(self, parent=None):
        """Initialize the history dialog."""
        super().__init__(parent)
        self.lang = get_language_manager()
        self.history = get_benchmark_history()
        self.selected_result: Optional[BenchmarkResult] = None
        self.setWindowTitle(get_text('history.title', 'Benchmark History'))
        self.setMinimumSize(800, 500)
        
        self.setup_ui()
        self.retranslate_ui()
        self.load_history()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        # Date range filter
        self.date_filter_label = QLabel()
        self.date_filter_combo = QComboBox()
        self.date_filter_combo.addItems([
            get_text('history.filter_all', 'All time'),
            get_text('history.filter_today', 'Today'),
            get_text('history.filter_week', 'Last 7 days'),
            get_text('history.filter_month', 'Last 30 days'),
            get_text('history.filter_custom', 'Custom range...')
        ])
        self.date_filter_combo.currentIndexChanged.connect(self.on_date_filter_changed)
        
        # Custom date range controls (initially hidden)
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1))
        self.start_date_edit.dateChanged.connect(self.on_custom_date_changed)
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setMaximumDate(QDate.currentDate())
        self.end_date_edit.dateChanged.connect(self.on_custom_date_changed)
        
        # Add widgets to filter layout
        filter_layout.addWidget(self.date_filter_label)
        filter_layout.addWidget(self.date_filter_combo)
        filter_layout.addWidget(self.start_date_edit)
        filter_layout.addWidget(QLabel("to"))
        filter_layout.addWidget(self.end_date_edit)
        filter_layout.addStretch()
        
        # Initially hide custom date range controls
        self.start_date_edit.hide()
        self.end_date_edit.hide()
        
        # Results table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.verticalHeader().setVisible(False)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.compare_button = QPushButton()
        self.compare_button.setEnabled(False)
        self.compare_button.clicked.connect(self.on_compare_clicked)
        
        self.delete_button = QPushButton()
        self.delete_button.clicked.connect(self.on_delete_clicked)
        
        self.close_button = QPushButton(get_text('common.close', 'Close'))
        self.close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.compare_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        # Stats label
        self.stats_label = QLabel()
        self.stats_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Add widgets to main layout
        layout.addLayout(filter_layout)
        layout.addWidget(self.table)
        layout.addWidget(self.stats_label)
        layout.addLayout(button_layout)
        
        # Set column widths
        self.table.setColumnWidth(0, 150)  # Date
        self.table.setColumnWidth(1, 100)  # Pystones
        self.table.setColumnWidth(2, 100)  # Time
        self.table.setColumnWidth(3, 80)   # Iterations
        self.table.setColumnWidth(4, 120)  # CPU
        self.table.horizontalHeader().setStretchLastSection(True)  # System
    
    def retranslate_ui(self):
        """Update UI text based on current language."""
        self.setWindowTitle(get_text('history.title', 'Benchmark History'))
        self.date_filter_label.setText(get_text('history.filter', 'Filter:'))
        self.compare_button.setText(get_text('history.compare', 'Compare Selected'))
        self.delete_button.setText(get_text('history.delete', 'Delete Selected'))
        
        # Set column headers
        headers = [
            get_text('history.column_date', 'Date/Time'),
            get_text('history.column_pystones', 'Pystones/s'),
            get_text('history.column_time', 'Time (s)'),
            get_text('history.column_iterations', 'Iterations'),
            get_text('history.column_cpu', 'CPU'),
            get_text('history.column_system', 'System')
        ]
        self.table.setHorizontalHeaderLabels(headers)
    
    def load_history(self, start_date: Optional[float] = None, end_date: Optional[float] = None):
        """Load benchmark history into the table."""
        self.table.setRowCount(0)
        
        # Get results based on date range
        if start_date is not None and end_date is not None:
            results = self.history.get_results_by_date_range(start_date, end_date)
        else:
            results = self.history.get_recent_results(100)  # Limit to 100 most recent
        
        # Sort by date (newest first)
        results.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Populate table
        self.table.setRowCount(len(results))
        for row, result in enumerate(results):
            # Date/Time
            dt = datetime.fromtimestamp(result.timestamp)
            date_item = QTableWidgetItem(dt.strftime('%Y-%m-%d %H:%M:%S'))
            date_item.setData(Qt.UserRole, result)  # Store the full result object
            
            # Pystones
            pystones_item = QTableWidgetItem(f"{result.pystones:,.2f}")
            pystones_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Time
            time_item = QTableWidgetItem(f"{result.time_elapsed:.2f}")
            time_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Iterations
            iter_item = QTableWidgetItem(f"{result.iterations:,}")
            iter_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # CPU info
            cpu_info = result.system_info.get('cpu', {})
            cpu_text = f"{cpu_info.get('model', 'N/A')} ({cpu_info.get('cores', '?')} cores)"
            cpu_item = QTableWidgetItem(cpu_text)
            
            # System info
            system_info = result.system_info
            os_name = system_info.get('system', {}).get('system', 'N/A')
            os_version = system_info.get('system', {}).get('version', '')
            system_text = f"{os_name} {os_version}".strip()
            system_item = QTableWidgetItem(system_text)
            
            # Add items to table
            self.table.setItem(row, 0, date_item)
            self.table.setItem(row, 1, pystones_item)
            self.table.setItem(row, 2, time_item)
            self.table.setItem(row, 3, iter_item)
            self.table.setItem(row, 4, cpu_item)
            self.table.setItem(row, 5, system_item)
        
        # Update stats
        self.update_stats_label(len(results))
    
    def update_stats_label(self, count: int):
        """Update the statistics label with the number of results."""
        self.stats_label.setText(
            get_text('history.results_count', 'Showing {count} results').format(count=count)
        )
    
    def on_date_filter_changed(self, index: int):
        """Handle date filter selection change."""
        now = datetime.now()
        
        # Show/hide custom date range controls
        show_custom = (index == 4)  # Custom range is the last item
        self.start_date_edit.setVisible(show_custom)
        self.end_date_edit.setVisible(show_custom)
        
        # Set date range based on selection
        if index == 0:  # All time
            self.load_history()
        elif index == 1:  # Today
            start_of_day = datetime(now.year, now.month, now.day).timestamp()
            self.load_history(start_of_day, now.timestamp())
        elif index == 2:  # Last 7 days
            week_ago = now - timedelta(days=7)
            self.load_history(week_ago.timestamp(), now.timestamp())
        elif index == 3:  # Last 30 days
            month_ago = now - timedelta(days=30)
            self.load_history(month_ago.timestamp(), now.timestamp())
        # Custom range is handled by the date edit signals
    
    def on_custom_date_changed(self, _):
        """Handle custom date range changes."""
        if self.date_filter_combo.currentIndex() == 4:  # Custom range selected
            start_date = self.start_date_edit.dateTime().toSecsSinceEpoch()
            end_date = self.end_date_edit.dateTime().addDays(1).toSecsSinceEpoch() - 1  # End of day
            self.load_history(start_date, end_date)
    
    def on_selection_changed(self):
        """Handle row selection changes."""
        selected = self.table.selectedItems()
        self.compare_button.setEnabled(len(selected) > 0)
        self.delete_button.setEnabled(len(selected) > 0)
        
        if selected:
            # Get the first selected row
            row = selected[0].row()
            date_item = self.table.item(row, 0)
            self.selected_result = date_item.data(Qt.UserRole)
        else:
            self.selected_result = None
    
    def on_compare_clicked(self):
        """Handle compare button click."""
        if self.selected_result:
            self.result_selected.emit(self.selected_result)
            self.accept()
    
    def on_delete_clicked(self):
        """Handle delete button click."""
        if not self.selected_result:
            return
            
        # Ask for confirmation
        confirm = QMessageBox.question(
            self,
            get_text('history.delete_title', 'Confirm Deletion'),
            get_text('history.delete_confirm', 'Are you sure you want to delete the selected benchmark result?'),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                # Remove the selected result from history
                self.history._results = [r for r in self.history._results 
                                      if r.timestamp != self.selected_result.timestamp]
                self.history._save_history()
                
                # Reload the table
                self.load_history()
                
                QMessageBox.information(
                    self,
                    get_text('history.deleted', 'Deleted'),
                    get_text('history.delete_success', 'The benchmark result has been deleted.')
                )
            except Exception as e:
                log.error(f"Error deleting benchmark result: {e}")
                QMessageBox.critical(
                    self,
                    get_text('error.title', 'Error'),
                    get_text('history.delete_error', 'Failed to delete the benchmark result.')
                )
    
    def sizeHint(self):
        """Return a reasonable default size for the dialog."""
        return super().sizeHint().expandedTo(self.minimumSizeHint())
