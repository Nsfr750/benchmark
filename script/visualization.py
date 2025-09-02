"""
Enhanced visualization module for benchmark results.
Provides various visualization options for displaying benchmark data.
"""
from typing import Dict, List, Optional, Tuple, Any
from .lang_mgr import get_text
from PySide6.QtCore import Qt, QPoint, Signal, QTimer, QDateTime
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QAction
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, 
                             QTabWidget, QListWidget, QListWidgetItem, QMenu, QMessageBox,
                             QSizePolicy, QPushButton, QGridLayout, QGroupBox, QScrollArea)
from PySide6.QtCharts import (QChart, QChartView, QLineSeries, QScatterSeries, QValueAxis, 
                             QBarSet, QBarSeries, QBarCategoryAxis, QPieSeries, QPieSlice)

from script.test_script.benchmark_history import get_benchmark_history, TestResult
from script.lang_mgr import get_language_manager
import math
import statistics
from datetime import datetime, timedelta

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QSizePolicy, QFrame, QSplitter, QTableWidget, QTableWidgetItem,
    QHeaderView, QTabWidget, QFormLayout, QGroupBox, QScrollArea,
    QListWidget, QListWidgetItem, QPushButton, QFileDialog, QMenu, QToolButton
)
from PySide6.QtCore import Qt, QSize, Signal, QDateTime, QTimer, QPoint
from PySide6.QtCharts import (
    QChart, QChartView, QLineSeries, QSplineSeries, QBarSeries, 
    QBarSet, QBarCategoryAxis, QValueAxis, QDateTimeAxis, QPieSeries,
    QScatterSeries, QPieSlice, QLegend, QBarLegendMarker
)
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QLinearGradient, QGradient, QAction, QIcon
import numpy as np

from script.lang_mgr import get_language_manager
from script.test_script.benchmark_history import get_benchmark_history, BenchmarkResult, TestResult
from script.logger import logger

class BenchmarkChartView(QChartView):
    """Custom chart view with hover effects and tooltips."""
    
    point_hovered = Signal(int, float, float)  # index, x, y
    point_left = Signal()
    
    def __init__(self, chart, parent=None):
        super().__init__(chart, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMouseTracking(True)
        self._tooltip = None
        self._last_point = None
        self._highlighted_point = None
        self._highlight_pen = QPen(Qt.red, 3)
        self._export_menu = None
        
    def mouseMoveEvent(self, event):
        """Handle mouse move events for hover effects with detailed tooltips."""
        chart = self.chart()
        pos = self.mapToScene(event.pos())
        chart_pos = chart.mapToValue(pos)
        
        # Find the closest data point
        closest_series = None
        closest_point = None
        closest_index = -1
        min_distance = float('inf')
        
        for series in chart.series():
            for i, point in enumerate(series.pointsVector()):
                dist = math.sqrt((point.x() - chart_pos.x())**2 + (point.y() - chart_pos.y())**2)
                if dist < min_distance and dist < 10:  # 10-pixel threshold
                    min_distance = dist
                    closest_series = series
                    closest_point = point
                    closest_index = i
        
        if closest_series and closest_point and closest_index >= 0:
            # Get the benchmark result associated with this point
            benchmark_result = None
            if hasattr(closest_series, 'benchmark_results') and closest_index < len(closest_series.benchmark_results):
                benchmark_result = closest_series.benchmark_results[closest_index]
            
            # Get the test name if available
            test_name = closest_series.name() if closest_series.name() else "Test"
            
            # Format the tooltip with detailed metrics
            tooltip_lines = [
                f"<b>{test_name}</b>",
                ""
            ]
            
            # Add timestamp if available
            if hasattr(closest_point, 'x') and isinstance(closest_point.x(), (int, float)):
                timestamp = datetime.fromtimestamp(closest_point.x() / 1000)  # Convert from ms to datetime
                tooltip_lines.append(f"<b>Time:</b> {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Add Y value with appropriate label
            if hasattr(closest_point, 'y') and isinstance(closest_point.y(), (int, float)):
                y_label = "Score"
                if hasattr(self.parent(), 'y_axis_combo'):
                    y_label = self.parent().y_axis_combo.currentText()
                tooltip_lines.append(f"<b>{y_label}:</b> {closest_point.y():.2f}")
            
            # Add additional metrics from benchmark result if available
            if benchmark_result:
                if hasattr(benchmark_result, 'pystones'):
                    tooltip_lines.append(f"<b>Pystones/s:</b> {benchmark_result.pystones:,.2f}")
                if hasattr(benchmark_result, 'time_elapsed'):
                    tooltip_lines.append(f"<b>Time Elapsed:</b> {benchmark_result.time_elapsed:.2f} s")
                if hasattr(benchmark_result, 'iterations'):
                    tooltip_lines.append(f"<b>Iterations:</b> {benchmark_result.iterations:,}")
                if hasattr(benchmark_result, 'cpu_info') and benchmark_result.cpu_info:
                    tooltip_lines.append(f"<b>CPU:</b> {benchmark_result.cpu_info}")
            
            # Create or update tooltip
            if not self._tooltip:
                self._tooltip = QLabel(self, flags=Qt.ToolTip | Qt.FramelessWindowHint)
                self._tooltip.setStyleSheet("""
                    QLabel {
                        background-color: rgba(255, 255, 255, 240);
                        border: 1px solid #ccc;
                        padding: 8px;
                        border-radius: 4px;
                        font-size: 11px;
                    }
                """)
                self._tooltip.setAttribute(Qt.WA_ShowWithoutActivating)
            
            # Set tooltip text with HTML formatting
            self._tooltip.setText("<br>".join(tooltip_lines))
            self._tooltip.adjustSize()
            
            # Position tooltip near the cursor but don't go off screen
            pos_x = event.pos().x() + 15
            pos_y = event.pos().y() - self._tooltip.height() - 10
            
            # Adjust if tooltip would go off the right edge
            if pos_x + self._tooltip.width() > self.width() - 10:
                pos_x = event.pos().x() - self._tooltip.width() - 15
            
            # Adjust if tooltip would go off the top
            if pos_y < 10:
                pos_y = event.pos().y() + 20
            
            self._tooltip.move(pos_x, pos_y)
            self._tooltip.show()
            
            # Highlight the data point
            if not self._highlighted_point:
                self._highlighted_point = self.scene().addEllipse(
                    closest_point.x() - 4, -closest_point.y() - 4, 8, 8,
                    self._highlight_pen,
                    QBrush(Qt.red)
                )
            else:
                self._highlighted_point.setRect(
                    closest_point.x() - 4, -closest_point.y() - 4, 8, 8
                )
        else:
            # Hide tooltip and clear highlight when not hovering over a point
            self.point_left.emit()
            if self._tooltip:
                self._tooltip.hide()
            if self._highlighted_point:
                self.scene().removeItem(self._highlighted_point)
                self._highlighted_point = None
        
        super().mouseMoveEvent(event)


class BenchmarkVisualizer(QWidget):
    """Widget for visualizing benchmark results with multiple chart types."""
    
    def __init__(self, parent=None):
        """Initialize the visualizer."""
        super().__init__(parent)
        self.lang = get_language_manager()
        self.current_chart = None
        self.current_theme = 'light'
        self.setWindowTitle(get_text("visualization.title", "Benchmark Results Visualization"))
        self.setMinimumSize(800, 600)
        self.setup_ui()
        self.apply_theme()
    
    def setup_summary_tab(self):
        """Set up the summary tab with benchmark statistics."""
        self.summary_tab = QWidget()
        layout = QVBoxLayout(self.summary_tab)
        
        # Create a scroll area for the summary tab
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Overall score section
        overall_group = QGroupBox(get_text("visualization.overall_score", "Overall Score"))
        overall_layout = QVBoxLayout(overall_group)
        
        # Score label
        self.score_label = QLabel("N/A")
        score_font = self.score_label.font()
        score_font.setPointSize(24)
        score_font.setBold(True)
        self.score_label.setFont(score_font)
        self.score_label.setAlignment(Qt.AlignCenter)
        overall_layout.addWidget(self.score_label)
        
        # Score description
        score_desc = QLabel(get_text("visualization.overall_score_desc", "Based on all benchmark results"))
        score_desc.setAlignment(Qt.AlignCenter)
        overall_layout.addWidget(score_desc)
        
        scroll_layout.addWidget(overall_group)
        
        # Add some spacing
        scroll_layout.addSpacing(20)
        
        # Add scroll area to layout
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        return self.summary_tab
        
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Chart controls layout
        controls_layout = QHBoxLayout()
        
        # Chart type selection
        chart_type_group = QGroupBox(get_text("visualization.chart_type", "Chart Type"))
        chart_type_layout = QHBoxLayout(chart_type_group)
        chart_type_layout.addWidget(QLabel(get_text("visualization.chart_type", "Chart Type:")))
        
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItem(get_text("visualization.chart_type_line", "Line Chart"), "line")
        self.chart_type_combo.addItem(get_text("visualization.chart_type_bar", "Bar Chart"), "bar")
        self.chart_type_combo.addItem(get_text("visualization.chart_type_scatter", "Scatter Plot"), "scatter")
        self.chart_type_combo.currentIndexChanged.connect(self._on_chart_type_changed)
        chart_type_layout.addWidget(self.chart_type_combo)
        
        # Time range selection
        time_range_layout = QHBoxLayout()
        time_range_layout.addWidget(QLabel(get_text("visualization.time_range", "Time Range:")))
        
        self.time_range_combo = QComboBox()
        self.time_range_combo.addItem(get_text("visualization.last_hour", "Last Hour"), "1h")
        self.time_range_combo.addItem(get_text("visualization.today", "Today"), "today")
        self.time_range_combo.addItem(get_text("visualization.last_7_days", "Last 7 Days"), "7d")
        self.time_range_combo.addItem(get_text("visualization.last_30_days", "Last 30 Days"), "30d")
        self.time_range_combo.addItem(get_text("visualization.all_time", "All Time"), "all")
        self.time_range_combo.currentIndexChanged.connect(self._on_time_range_changed)
        time_range_layout.addWidget(self.time_range_combo)
        
        # Add to controls layout
        controls_layout.addLayout(chart_type_layout)
        controls_layout.addSpacing(20)
        controls_layout.addLayout(time_range_layout)
        controls_layout.addStretch()
        
        main_layout.addLayout(controls_layout)
        
        # Create tab widget for different visualizations
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Summary tab
        self.summary_tab = QWidget()
        self.setup_summary_tab()
        self.tab_widget.addTab(self.summary_tab, get_text("visualization.summary", "Summary"))
        
        # Performance tab
        self.performance_tab = QWidget()
        self.setup_performance_tab()
        self.tab_widget.addTab(self.performance_tab, get_text("visualization.performance", "Performance"))
        
        # Comparison tab
        self.comparison_tab = QWidget()
        self.setup_comparison_tab()
        self.tab_widget.addTab(self.comparison_tab, get_text("visualization.comparison", "Comparison"))
        
        # History tab
        self.history_tab = QWidget()
        self.setup_history_tab()
        self.tab_widget.addTab(self.history_tab, get_text("visualization.history", "History"))
        
        # Set default tab
        self.tab_widget.setCurrentIndex(0)
        
        # Initialize comparison data
        self.selected_runs = []
        self.comparison_series = {}
        
    def setup_performance_tab(self):
        """Set up the performance tab with benchmark results visualization."""
        layout = QVBoxLayout(self.performance_tab)
        
        # Create chart view
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        
        # Add chart view to layout
        layout.addWidget(self.chart_view)
        
        # Initialize with empty chart
        self.chart = QChart()
        self.chart.setTitle(get_text("visualization.performance_chart_title", "Benchmark Results"))
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)
        
        self.chart_view.setChart(self.chart)
        
        # Add some sample data (to be replaced with actual benchmark data)
        self._add_sample_data()
    
    def _add_sample_data(self):
        """Add sample data to the chart (for testing)."""
        series = QLineSeries()
        series.setName("Sample Data")
        
        # Add some sample points
        series.append(0, 0)
        series.append(1, 5)
        series.append(2, 3)
        series.append(3, 7)
        series.append(4, 6)
        
        self.chart.addSeries(series)
        
        # Create axes
        axis_x = QValueAxis()
        axis_x.setTitleText(get_text("visualization.x_axis", "Run #"))
        axis_x.setLabelFormat("%d")
        self.chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setTitleText(get_text("visualization.y_axis", "Score"))
        axis_y.setLabelFormat("%.1f")
        self.chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
    
    def setup_comparison_tab(self):
        """Set up the comparison tab for comparing multiple benchmark runs."""
        layout = QVBoxLayout(self.comparison_tab)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Controls layout
        controls_layout = QHBoxLayout()
        
        # Run selection
        self.run_list = QListWidget()
        self.run_list.setSelectionMode(QListWidget.MultiSelection)
        self.run_list.itemSelectionChanged.connect(self._on_run_selection_changed)
        
        # Buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(5)
        
        self.refresh_button = QPushButton(get_text("visualization.refresh", "Refresh"))
        self.refresh_button.clicked.connect(self._refresh_run_list)
        
        self.compare_button = QPushButton(get_text("visualization.compare", "Compare"))
        self.compare_button.setEnabled(False)
        self.compare_button.clicked.connect(self._update_comparison_chart)
        
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.compare_button)
        button_layout.addStretch()
        
        # Add widgets to controls layout
        controls_layout.addWidget(QLabel(get_text("visualization.select_runs", "Select Runs:")))
        controls_layout.addWidget(self.run_list, 1)
        controls_layout.addLayout(button_layout)
        
        # Chart view
        self.comparison_chart = QChart()
        self.comparison_chart.setTitle(self.lang.get("visualization.comparison_chart_title", "Benchmark Comparison"))
        self.comparison_chart.setAnimationOptions(QChart.SeriesAnimations)
        
        self.comparison_chart_view = BenchmarkChartView(self.comparison_chart)
        self.comparison_chart_view.setRenderHint(QPainter.Antialiasing)
        
        # Add to main layout
        layout.addLayout(controls_layout)
        layout.addWidget(self.comparison_chart_view, 1)
        
        # Initial load of runs
        self._refresh_run_list()
    
    def _refresh_run_list(self):
        """Refresh the list of available benchmark runs."""
        self.run_list.clear()
        history = get_benchmark_history()
        
        if not history:
            self.run_list.addItem(self.lang.get("visualization.no_benchmark_data", "No benchmark data available"))
            return
            
        # Sort by timestamp, newest first
        history.sort(key=lambda x: x.timestamp, reverse=True)
        
        for i, result in enumerate(history):
            timestamp = result.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            score = sum(r.score for r in result.test_results) / len(result.test_results) if result.test_results else 0
            item = QListWidgetItem(f"{timestamp} - Score: {score:.1f}")
            item.setData(Qt.UserRole, i)  # Store index in history
            self.run_list.addItem(item)
    
    def _on_run_selection_changed(self):
        """Handle selection changes in the run list."""
        selected_items = self.run_list.selectedItems()
        self.compare_button.setEnabled(len(selected_items) > 1)
        
        # Store selected run indices
        self.selected_runs = [item.data(Qt.UserRole) for item in selected_items]
    
    def _show_export_menu(self, position: QPoint):
        """Show the export menu for the chart."""
        if not hasattr(self, 'chart_view') or not self.chart_view.chart():
            return
            
        menu = QMenu(self)
        
        # Add export actions
        export_png = QAction(self.lang.get("visualization.export_png", "Export as PNG..."), self)
        export_png.triggered.connect(lambda: self._export_chart('PNG'))
        
        export_svg = QAction(self.lang.get("visualization.export_svg", "Export as SVG..."), self)
        export_svg.triggered.connect(lambda: self._export_chart('SVG'))
        
        menu.addAction(export_png)
        menu.addAction(export_svg)
        
        # Show the menu at the cursor position
        menu.exec(self.chart_view.mapToGlobal(position))
    
    def _export_chart(self, format: str):
        """Export the current chart to a file.
        
        Args:
            format: The export format ('PNG' or 'SVG')
        """
        if not hasattr(self, 'chart_view') or not self.chart_view.chart():
            return
            
        # Get default filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"benchmark_{timestamp}"
        
        # Set up file dialog
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        
        if format == 'PNG':
            file_filter = self.lang.get("visualization.png_files", "PNG Images (*.png)")
            default_path = f"{default_name}.png"
        else:  # SVG
            file_filter = self.lang.get("visualization.svg_files", "SVG Files (*.svg)")
            default_path = f"{default_name}.svg"
        
        # Show save dialog
        file_path, _ = file_dialog.getSaveFileName(
            self,
            self.lang.get("visualization.export_chart", "Export Chart"),
            default_path,
            file_filter
        )
        
        if not file_path:
            return  # User cancelled
            
        # Create a QPixmap from the chart view
        pixmap = self.chart_view.grab()
        
        try:
            if format == 'PNG':
                if not file_path.lower().endswith('.png'):
                    file_path += '.png'
                pixmap.save(file_path, 'PNG')
            else:  # SVG
                if not file_path.lower().endswith('.svg'):
                    file_path += '.svg'
                
                # Create a QSvgGenerator for SVG export
                from PySide6.QtSvg import QSvgGenerator
                from PySide6.QtGui import QPainter as QSvgPainter
                
                generator = QSvgGenerator()
                generator.setFileName(file_path)
                generator.setSize(pixmap.size())
                generator.setViewBox(pixmap.rect())
                
                painter = QSvgPainter(generator)
                self.chart_view.render(painter)
                painter.end()
                
        except Exception as e:
            logger.error(f"Failed to export chart: {str(e)}")
            error_msg = self.lang.get(
                "visualization.export_error", 
                "Failed to export chart: {error}"
            ).format(error=str(e))
            
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                self.lang.get("visualization.export_error_title", "Export Error"),
                error_msg
            )
    
    def _update_comparison_chart(self):
        """Update the comparison chart with selected runs."""
        if not self.selected_runs or len(self.selected_runs) < 2:
            return
            
        history = get_benchmark_history()
        if not history:
            return
            
        # Sort history by timestamp for consistent indexing
        history.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Clear existing series
        self.comparison_chart.removeAllSeries()
        self.comparison_series.clear()
        
        # Create a bar series for each selected run
        bar_series = QBarSeries()
        categories = []
        
        # Get all unique test names across all selected runs
        all_test_names = set()
        for idx in self.selected_runs:
            if 0 <= idx < len(history):
                all_test_names.update(t.name for t in history[idx].test_results)
        
        test_names = sorted(all_test_names)
        categories = test_names
        
        # For each selected run, create a bar set
        for idx in self.selected_runs:
            if 0 <= idx < len(history):
                result = history[idx]
                timestamp = result.timestamp.strftime("%Y-%m-%d %H:%M")
                bar_set = QBarSet(timestamp)
                
                # Create a mapping of test name to score for this run
                test_scores = {t.name: t.score for t in result.test_results}
                
                # Add scores in the order of test_names, or 0 if test not in this run
                for test_name in test_names:
                    bar_set.append(test_scores.get(test_name, 0))
                
                bar_series.append(bar_set)
        
        # Add series to chart
        self.comparison_chart.addSeries(bar_series)
        
        # Set up axes
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        
        axis_y = QValueAxis()
        axis_y.setTitleText(self.lang.get("visualization.score", "Score"))
        
        self.comparison_chart.addAxis(axis_x, Qt.AlignBottom)
        self.comparison_chart.addAxis(axis_y, Qt.AlignLeft)
        
        bar_series.attachAxis(axis_x)
        bar_series.attachAxis(axis_y)
        
        # Update legend
        self.comparison_chart.legend().setVisible(True)
        self.comparison_chart.legend().setAlignment(Qt.AlignBottom)
        
        # Apply theme
        self._apply_theme_to_chart(self.comparison_chart)
        
        # Update view
        self.comparison_chart_view.update()
    
        # Create a bar series for each selected run
        bar_series = QBarSeries()
        categories = []
        
        # Set up score label font
        score_font = self.font()
        score_font.setPointSize(24)
        score_font.setBold(True)
        self.score_label = QLabel()
        self.score_label.setFont(score_font)
        
        overall_layout.addWidget(self.score_label)
        scroll_layout.addWidget(overall_group)
        
        # Category scores
        self.category_groups = {}
        for category in ['cpu', 'memory', 'disk']:
            group = QGroupBox(get_text(f"visualization.category_{category}", category.capitalize()))
            group_layout = QVBoxLayout(group)
            
            # Score bar
            score_bar = QFrame()
            score_bar.setFrameShape(QFrame.StyledPanel)
            score_bar.setStyleSheet("""
                QFrame {
                    background-color: #e0e0e0;
                    border-radius: 5px;
                }
                QFrame#scoreBar {
                    background-color: #4CAF50;
                    border-radius: 5px;
                }
            """)
            score_bar.setFixedHeight(20)
            
            # Score label
            score_label = QLabel("-")
            score_label.setAlignment(Qt.AlignCenter)
            
            # Progress bar (custom)
            progress_container = QWidget()
            progress_layout = QHBoxLayout(progress_container)
            progress_layout.setContentsMargins(0, 0, 0, 0)
            
            self.progress_bar = QFrame()
            self.progress_bar.setObjectName("scoreBar")
            self.progress_bar.setStyleSheet("""
                #scoreBar {
                    background-color: #4CAF50;
                    border-radius: 5px;
                }
            """)
            self.progress_bar.setFixedHeight(20)
            self.progress_bar.setFixedWidth(0)
            
            progress_layout.addWidget(self.progress_bar)
            progress_layout.addStretch()
            
            group_layout.addWidget(score_label)
            group_layout.addWidget(progress_container)
            
            # Store references
            self.category_groups[category] = {
                'group': group,
                'score_label': score_label,
                'progress_bar': self.progress_bar
            }
            
            scroll_layout.addWidget(group)
        
        # Add stretch to push everything to the top
        scroll_layout.addStretch()
        
        # Set the scroll widget
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
    def update_performance_chart(self):
        """Update the performance chart based on current settings."""
        # Get benchmark history
        history = get_benchmark_history()
        if not history:
            self._show_no_data_message()
            return
            
        # Get test results from the most recent benchmark
        latest_result = history[-1]
        if not latest_result.test_results:
            self._show_no_data_message()
            return
            
        # Update chart based on current selection
        self._update_chart_from_selection()
        
    def _on_chart_type_changed(self):
        """Handle chart type selection change."""
        self._update_chart_from_selection()
        
    def _filter_results(self, results):
        """Filter results based on selected time range."""
        if not results:
            return []
            
        time_range = self.time_range_combo.currentData()
        now = datetime.now()
        
        if time_range == "1h":
            cutoff = now - timedelta(hours=1)
            return [r for r in results if r.timestamp >= cutoff]
        elif time_range == "today":
            cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return [r for r in results if r.timestamp >= cutoff]
        elif time_range == "7d":
            cutoff = now - timedelta(days=7)
            return [r for r in results if r.timestamp >= cutoff]
        elif time_range == "30d":
            cutoff = now - timedelta(days=30)
            return [r for r in results if r.timestamp >= cutoff]
        else:  # all time
            return results
            
    def _on_time_range_changed(self):
        """Handle time range selection change."""
        self.update_benchmark_data()
        
    def _update_chart_from_selection(self):
        """Update chart based on current selection."""
        # Get benchmark history
        history = get_benchmark_history()
        if not history or not history[-1].test_results:
            self._show_no_data_message()
            return
            
        # Get the latest test results
        latest_result = history[-1]
        tests = latest_result.test_results
        
        # Sort tests by name for consistent display
        tests.sort(key=lambda x: x.name)
        
        # Get chart type and update the chart
        chart_type = self.chart_type_combo.currentData()
        if chart_type == "line":
            self.show_line_chart()
        elif chart_type == "bar":
            self.show_bar_chart()
        elif chart_type == "scatter":
            self.show_scatter_plot()
    
    def _create_bar_chart(self, tests: List[TestResult], title: str):
        """Create a bar chart from test results."""
        chart = QChart()
        chart.setTitle(title)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Create a bar series
        series = QBarSeries()
        
        # Create a bar set for each test
        for test in tests:
            bar_set = QBarSet(test.name)
            bar_set.append(test.score)
            series.append(bar_set)
        
        chart.addSeries(series)
        
        # Create axes
        categories = [test.name for test in tests]
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        
        axis_y = QValueAxis()
        axis_y.setTitleText("Score")
        
        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)
        
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        
        # Update the chart view
        self._update_chart_view(chart)
    
    def _create_line_chart(self, tests: List[TestResult], title: str):
        """Create a line chart from test results."""
        chart = QChart()
        chart.setTitle(title)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Create a line series for each test
        for test in tests:
            series = QLineSeries()
            series.setName(test.name)
            
            # Add data points (just one point per test for now)
            series.append(0, test.score)
            
            chart.addSeries(series)
        
        # Create axes
        axis_x = QValueAxis()
        axis_x.setTitleText("Test")
        axis_x.setRange(0, 1)
        axis_x.setTickCount(1)
        
        axis_y = QValueAxis()
        axis_y.setTitleText("Score")
        
        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)
        
        for series in chart.series():
            series.attachAxis(axis_x)
            series.attachAxis(axis_y)
        
        # Update the chart view
        self._update_chart_view(chart)
    
    def _update_chart_view(self, chart: QChart):
        """Update the chart view with the new chart."""
        # Create a new chart view with the chart
        chart_view = BenchmarkChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        
        # Replace the old chart view in the layout
        old_chart = self.performance_tab.findChild(QChartView)
        if old_chart:
            self.performance_tab.layout().replaceWidget(old_chart, chart_view)
            old_chart.deleteLater()
        else:
            self.performance_tab.layout().addWidget(chart_view)
        
        # Store reference to current chart view
        self.chart_view = chart_view
        
        # Store benchmark results with the series for tooltips
        from script.benchmark_history import get_benchmark_history
        history = get_benchmark_history()
        if history and len(history) > 0:
            for series in chart.series():
                # Get the series index to match with benchmark results
                series_index = chart.series().index(series)
                if series_index < len(history):
                    # Store the benchmark result with the series for tooltips
                    series.benchmark_results = [history[series_index]]
        
        # Set up context menu for export
        chart_view.setContextMenuPolicy(Qt.CustomContextMenu)
        chart_view.customContextMenuRequested.connect(self._show_export_menu)
        
        # Add data to series
        y_axis = self.y_axis_combo.currentData()
        for result in results:
            x = result.timestamp.timestamp() * 1000  # Convert to milliseconds
            if y_axis == "pystones":
                y = result.pystones
            elif y_axis == "time":
                y = result.time_elapsed
            else:  # iterations
                y = result.iterations
            series.append(x, y)
        
        # Add series to chart
        chart.addSeries(series)
        
        # Set up axes
        axis_x = QDateTimeAxis()
        axis_x.setFormat("MMM d, yyyy\nhh:mm")
        axis_x.setTitleText(self.lang.get("visualization.date_time", "Date/Time"))
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setTitleText(self.y_axis_combo.currentText())
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        # Update chart view
        self._update_chart_view(chart)
    
    def show_bar_chart(self):
        """Display benchmark results as a bar chart."""
        from script.benchmark_history import get_benchmark_history
        from PySide6.QtCharts import QBarSet, QBarSeries, QBarCategoryAxis
        
        # Get data from history
        history = get_benchmark_history()
        results = self._filter_results(history.get_recent_results(20))  # Limit to last 20 for readability
        
        if not results:
            self._show_no_data_message()
            return
        
        # Create chart
        chart = QChart()
        chart.setTitle(self.lang.get("visualization.bar_chart_title", "Benchmark Results"))
        chart.legend().setVisible(True)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Create bar set
        bar_set = QBarSet(self.y_axis_combo.currentText())
        
        # Add data to bar set
        y_axis = self.y_axis_combo.currentData()
        categories = []
        
        for result in results:
            if y_axis == "pystones":
                value = result.pystones
            elif y_axis == "time":
                value = result.time_elapsed
            else:  # iterations
                value = result.iterations
            
            bar_set.append(value)
            categories.append(result.timestamp.strftime("%m/%d\n%H:%M"))
        
        # Create series and add bar set
        series = QBarSeries()
        series.append(bar_set)
        chart.addSeries(series)
        
        # Store benchmark results with the series for tooltips
        from script.benchmark_history import get_benchmark_history
        history = get_benchmark_history()
        if history and len(history) > 0:
            series.benchmark_results = history[-1].test_results  # Use the most recent benchmark results
        
        # Set up axes
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        axis_x.setTitleText(self.lang.get("visualization.date_time", "Date/Time"))
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setTitleText(self.y_axis_combo.currentText())
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        # Update chart view
        self._update_chart_view(chart)
    
    def show_scatter_plot(self):
        """Display benchmark results as a scatter plot."""
        from script.benchmark_history import get_benchmark_history
        from PySide6.QtCharts import QScatterSeries
        
        # Get data from history
        history = get_benchmark_history()
        results = self._filter_results(history.get_recent_results(100))
        
        if not results:
            self._show_no_data_message()
            return
        
        # Create chart
        chart = QChart()
        chart.setTitle(self.lang.get("visualization.scatter_plot_title", "Benchmark Results Distribution"))
        chart.legend().setVisible(True)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Create bar set
        bar_set = QBarSet(self.y_axis_combo.currentText())
        
        # Add data to bar set
        y_axis = self.y_axis_combo.currentData()
        categories = []
            
        for result in results:
            if y_axis == "pystones":
                value = result.pystones
            elif y_axis == "time":
                value = result.time_elapsed
            else:  # iterations
                value = result.iterations
        
            bar_set.append(value)
            categories.append(result.timestamp.strftime("%m/%d\n%H:%M"))
            
        # Create series and add bar set
        series = QBarSeries()
        series.append(bar_set)
        chart.addSeries(series)
            
        # Store benchmark results with the series for tooltips
        from script.benchmark_history import get_benchmark_history
        history = get_benchmark_history()
        if history and len(history) > 0:
            series.benchmark_results = history[-1].test_results  # Use the most recent benchmark results
            
        # Set up axes
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        axis_x.setTitleText(self.lang.get("visualization.date_time", "Date/Time"))
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
            
        axis_y = QValueAxis()
        axis_y.setTitleText(self.y_axis_combo.currentText())
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
            
        # Update chart view
        self._update_chart_view(chart)
    
def show_scatter_plot(self):
    """Display benchmark results as a scatter plot."""
    from script.benchmark_history import get_benchmark_history
    from PySide6.QtCharts import QScatterSeries, QDateTimeAxis, QValueAxis
        
    # Get data from history
    history = get_benchmark_history()
    results = self._filter_results(history.get_recent_results(100))
    
    if not results:
        self._show_no_data_message()
        return
        
    # Create chart
    chart = QChart()
    chart.setTitle(self.lang.get("visualization.scatter_plot_title", "Benchmark Results Distribution"))
    chart.legend().setVisible(True)
    chart.setAnimationOptions(QChart.SeriesAnimations)
        
    # Create series
    series = QScatterSeries()
    series.setName(self.y_axis_combo.currentText())
    series.setMarkerSize(10.0)
        
    # Add data to series
    y_axis = self.y_axis_combo.currentData()
    for result in results:
        x = result.timestamp.timestamp() * 1000  # Convert to milliseconds
        if y_axis == "pystones":
            y = result.pystones
        elif y_axis == "time":
            y = result.time_elapsed
        else:  # iterations
            y = result.iterations
        
        # Add point to series
        series.append(x, y)
        
    # Add series to chart
    chart.addSeries(series)
        
    # Store benchmark results with the series for tooltips
    if hasattr(history, 'get_recent_results'):
        series.benchmark_results = history.get_recent_results(1)  # Get most recent result
        
    # Set up axes
    axis_x = QDateTimeAxis()
    axis_x.setFormat("MMM d, yyyy")
    axis_x.setTitleText(self.lang.get("visualization.date_time", "Date/Time"))
    chart.addAxis(axis_x, Qt.AlignBottom)
    series.attachAxis(axis_x)
        
    axis_y = QValueAxis()
    axis_y.setTitleText(self.y_axis_combo.currentText())
    chart.addAxis(axis_y, Qt.AlignLeft)
    series.attachAxis(axis_y)
        
    # Update chart view
    self._update_chart_view(chart)

def _show_no_data_message(self):
    """Display a message when no data is available."""
    chart = QChart()
    chart.setTitle("No data available")
    
    # Create a simple text item
    no_data_label = QLabel("No benchmark data available")
    no_data_label.setAlignment(Qt.AlignCenter)
    
    # Create a widget to hold the label
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.addWidget(no_data_label)
    
    # Create a chart view
    chart_view = QChartView(chart)
    chart_view.setRenderHint(QPainter.Antialiasing)
    
    # Replace the current chart view
    old_chart = self.performance_tab.findChild(QChartView)
    if old_chart:
        self.performance_tab.layout().replaceWidget(old_chart, chart_view)
        old_chart.deleteLater()
    else:
        self.performance_tab.layout().addWidget(chart_view)
    
    # Store reference to current chart view
    self.chart_view = chart_view
    
    # Set up context menu for export
    chart_view.setContextMenuPolicy(Qt.CustomContextMenu)
    chart_view.customContextMenuRequested.connect(self._show_export_menu)
    
    # Configure chart view
    chart_view.setRenderHint(QPainter.Antialiasing, False)
    chart_view.setStyleSheet("background: transparent;")
    
    # Add the container to the chart view's layout
    layout = QVBoxLayout(chart_view)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(container)
    
    # Store the chart view reference
    self.chart_view = chart_view
    
    def update_summary(self, results: List[BenchmarkResult]):
        """Update the summary tab with the latest results."""
        if not results:
            return
            
        # Get the most recent result
        latest_result = max(results, key=lambda r: r.timestamp)
        
        # Update overall score
        if hasattr(latest_result, 'results'):
            # Calculate an overall score (simple average for now)
            scores = [r.score for r in latest_result.results if hasattr(r, 'score') and r.score > 0]
            if scores:
                overall_score = sum(scores) / len(scores)
                self.score_label.setText(f"{overall_score:.1f}")
        
        # Update category scores if category_groups exists
        if hasattr(self, 'category_groups'):
            for category in self.category_groups:
                category_tests = [r for r in latest_result.results 
                                if hasattr(r, 'metadata') and r.metadata.get('test_type') == category]
                
                if not category_tests:
                    continue
                    
                # Calculate average score for this category
                scores = [t.score for t in category_tests if hasattr(t, 'score') and t.score > 0]
                if not scores:
                    continue
                    
                avg_score = sum(scores) / len(scores)
                max_score = max(scores) * 1.2  # Add some headroom
                
                # Update UI
                group = self.category_groups[category]
                unit = category_tests[0].unit if hasattr(category_tests[0], 'unit') else ''
                group['score_label'].setText(f"{avg_score:.1f} {unit}")
                
                # Animate progress bar
                width = int((avg_score / max_score) * 200) if max_score > 0 else 0
                QTimer.singleShot(100, lambda w=width, b=group['progress_bar']: 
                                b.setFixedWidth(min(w, 200)))

    def update_summary(self, results):
        """Update the summary tab with the latest results."""
        if not results:
            return
            
        # Get the most recent result
        latest_result = max(results, key=lambda r: r.timestamp)
            
        # Update overall score
        if hasattr(latest_result, 'results'):
            # Calculate an overall score (simple average for now)
            scores = [r.score for r in latest_result.results if hasattr(r, 'score') and r.score > 0]
            if scores:
                overall_score = sum(scores) / len(scores)
                self.score_label.setText(f"{overall_score:.1f}")
            
        # Update category scores if category_groups exists
        if hasattr(self, 'category_groups'):
            for category in self.category_groups:
                category_tests = [r for r in latest_result.results 
                                if hasattr(r, 'metadata') and r.metadata.get('test_type') == category]
                    
                if not category_tests:
                    continue
                        
                # Calculate average score for this category
                scores = [t.score for t in category_tests if hasattr(t, 'score') and t.score > 0]
                if not scores:
                    continue
                        
                avg_score = sum(scores) / len(scores)
                max_score = max(scores) * 1.2  # Add some headroom
                    
                # Update UI
                group = self.category_groups[category]
                unit = category_tests[0].unit if hasattr(category_tests[0], 'unit') else ''
                group['score_label'].setText(f"{avg_score:.1f} {unit}")
                    
                # Animate progress bar
                width = int((avg_score / max_score) * 200) if max_score > 0 else 0
                QTimer.singleShot(100, lambda w=width, b=group['progress_bar']: 
                                b.setFixedWidth(min(w, 200)))

    def update_benchmark_data(self):
        """Update all visualizations with the latest benchmark data."""
        history = get_benchmark_history()
        if not history:
            self._show_no_data_message()
            return
                
        # Filter results based on time range
        filtered_history = self._filter_results(history)
            
        if not filtered_history:
            self._show_no_data_message()
            return
                
        # Update summary with filtered results
        self.update_summary(filtered_history)
            
        # Update performance chart with latest result from filtered set
        self.update_performance_chart()

    def apply_theme(self, theme='light'):
        """Apply the specified theme to the visualization.
        
        Args:
            theme: The theme to apply ('light' or 'dark')
        """
        self.current_theme = theme
        
        # Apply theme to all charts
        if hasattr(self, 'chart_view') and self.chart_view.chart():
            self._apply_theme_to_chart(self.chart_view.chart())
        if hasattr(self, 'comparison_chart'):
            self._apply_theme_to_chart(self.comparison_chart)
            
        # Update UI colors based on theme
        if theme == 'dark':
            self.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QTabWidget::pane {
                    border: 1px solid #3a3a3a;
                    background: #2b2b2b;
                }
                QTabBar::tab {
                    background: #3a3a3a;
                    color: #ffffff;
                    padding: 5px 10px;
                    border: 1px solid #3a3a3a;
                }
                QTabBar::tab:selected {
                    background: #1e1e1e;
                    border-bottom-color: #1e1e1e;
                }
                QListWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border: 1px solid #3a3a3a;
                }
                QPushButton {
                    background-color: #3a3a3a;
                    color: #ffffff;
                    border: 1px solid #4a4a4a;
                    padding: 5px 10px;
                }
                QPushButton:disabled {
                    background-color: #2a2a2a;
                    color: #666666;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #f0f0f0;
                    color: #000000;
                }
                QTabWidget::pane {
                    border: 1px solid #c0c0c0;
                    background: #f0f0f0;
                }
                QTabBar::tab {
                    background: #e0e0e0;
                    color: #000000;
                    padding: 5px 10px;
                    border: 1px solid #c0c0c0;
                }
                QTabBar::tab:selected {
                    background: #ffffff;
                    border-bottom-color: #ffffff;
                }
                QListWidget {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #c0c0c0;
                }
                QPushButton {
                    background-color: #f0f0f0;
                    color: #000000;
                    border: 1px solid #c0c0c0;
                    padding: 5px 10px;
                }
                QPushButton:disabled {
                    background-color: #e0e0e0;
                    color: #808080;
                }
            """)

    def update_data(self):
        """Update the visualization with the latest benchmark data."""
        self.update_benchmark_data()

    def _apply_theme_to_chart(self, chart):
        """Apply the current theme to a chart."""
        if self.current_theme == 'dark':
            chart.setTheme(QChart.ChartThemeDark)
        else:
            chart.setTheme(QChart.ChartThemeLight)
            
        # Apply custom colors for better visibility
        for i, series in enumerate(chart.series()):
            if isinstance(series, QBarSeries):
                for j, bar_set in enumerate(series.barSets()):
                    # Use different colors for each bar set
                    color = QColor(65 + (j * 50) % 190, 105 + (j * 100) % 150, 225 + (j * 25) % 30)
                    bar_set.setColor(color)
                    bar_set.setBorderColor(color.darker(150))
            elif isinstance(series, (QLineSeries, QSplineSeries, QScatterSeries)):
                # Use different colors for each line/scatter series
                color = QColor(65 + (i * 50) % 190, 105 + (i * 100) % 150, 225 + (i * 25) % 30)
                series.setColor(color)
                series.setBorderColor(color.darker(150))
                
        # Update axes
        for axis in chart.axes():
            if isinstance(axis, (QValueAxis, QDateTimeAxis)):
                if self.current_theme == 'dark':
                    axis.setLabelsColor(Qt.white)
                    axis.setTitleBrush(Qt.white)
                    axis.setGridLineColor(QColor(100, 100, 100))
                else:
                    axis.setLabelsColor(Qt.black)
                    axis.setTitleBrush(Qt.black)
                    axis.setGridLineColor(QColor(200, 200, 200))
