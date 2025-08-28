"""
Enhanced visualization module for benchmark results.
Provides various visualization options for displaying benchmark data.
"""
from typing import Dict, List, Optional, Tuple, Any
import math
import statistics
from datetime import datetime, timedelta

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QSizePolicy, QFrame, QSplitter, QTableWidget, QTableWidgetItem,
    QHeaderView, QTabWidget, QFormLayout, QGroupBox, QScrollArea
)
from PySide6.QtCore import Qt, QSize, Signal, QDateTime, QTimer
from PySide6.QtCharts import (
    QChart, QChartView, QLineSeries, QSplineSeries, QBarSeries, 
    QBarSet, QBarCategoryAxis, QValueAxis, QDateTimeAxis, QPieSeries,
    QScatterSeries, QPieSlice, QLegend, QBarLegendMarker
)
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QLinearGradient, QGradient
import numpy as np

from script.lang_mgr import get_language_manager
from script.benchmark_history import get_benchmark_history, BenchmarkResult, TestResult
from script.logger import get_logger

logger = get_logger(__name__)

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
        
    def mouseMoveEvent(self, event):
        """Handle mouse move events for hover effects."""
        chart = self.chart()
        pos = self.mapToScene(event.pos())
        chart_pos = chart.mapToValue(pos)
        
        # Find the closest data point
        closest_series = None
        closest_point = None
        min_distance = float('inf')
        
        for series in chart.series():
            for i, point in enumerate(series.pointsVector()):
                dist = math.sqrt((point.x() - chart_pos.x())**2 + (point.y() - chart_pos.y())**2)
                if dist < min_distance and dist < 10:  # 10-pixel threshold
                    min_distance = dist
                    closest_series = series
                    closest_point = (i, point.x(), point.y())
        
        if closest_point and closest_series:
            idx, x, y = closest_point
            self.point_hovered.emit(idx, x, y)
            
            # Highlight the point
            if self._highlighted_point:
                self.scene().removeItem(self._highlighted_point)
            
            self._highlighted_point = self.chart().scene().addEllipse(
                closest_series.at(idx).x() - 5, 
                closest_series.at(idx).y() - 5,
                10, 10, 
                self._highlight_pen
            )
            
            # Show tooltip
            if not self._tooltip:
                self._tooltip = QLabel(self)
                self._tooltip.setStyleSheet("""
                    QLabel {
                        background-color: rgba(255, 255, 255, 220);
                        border: 1px solid #ccc;
                        padding: 5px;
                        border-radius: 3px;
                    }
                """)
                self._tooltip.show()
            
            self._tooltip.setText(f"X: {x:.2f}\nY: {y:.2f}")
            self._tooltip.move(
                min(self.width() - self._tooltip.width() - 10, 
                    max(10, event.pos().x() - self._tooltip.width() // 2)),
                max(10, event.pos().y() - self._tooltip.height() - 10)
            )
        else:
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
        self.setWindowTitle(self.lang.get("visualization.title", "Benchmark Results Visualization"))
        self.setMinimumSize(800, 600)
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Chart controls layout
        controls_layout = QHBoxLayout()
        
        # Chart type selection
        chart_type_layout = QHBoxLayout()
        chart_type_layout.addWidget(QLabel(self.lang.get("visualization.chart_type", "Chart Type:")))
        
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItem(self.lang.get("visualization.chart_type_line", "Line Chart"), "line")
        self.chart_type_combo.addItem(self.lang.get("visualization.chart_type_bar", "Bar Chart"), "bar")
        self.chart_type_combo.addItem(self.lang.get("visualization.chart_type_scatter", "Scatter Plot"), "scatter")
        self.chart_type_combo.currentIndexChanged.connect(self._on_chart_type_changed)
        chart_type_layout.addWidget(self.chart_type_combo)
        
        # Time range selection
        time_range_layout = QHBoxLayout()
        time_range_layout.addWidget(QLabel(self.lang.get("visualization.time_range", "Time Range:")))
        
        self.time_range_combo = QComboBox()
        self.time_range_combo.addItem(self.lang.get("visualization.last_hour", "Last Hour"), "1h")
        self.time_range_combo.addItem(self.lang.get("visualization.today", "Today"), "today")
        self.time_range_combo.addItem(self.lang.get("visualization.last_7_days", "Last 7 Days"), "7d")
        self.time_range_combo.addItem(self.lang.get("visualization.last_30_days", "Last 30 Days"), "30d")
        self.time_range_combo.addItem(self.lang.get("visualization.all_time", "All Time"), "all")
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
        self.tab_widget.addTab(self.summary_tab, self.lang.get("visualization.summary", "Summary"))
        
        # Performance tab
        self.performance_tab = QWidget()
        self.setup_performance_tab()
        self.tab_widget.addTab(self.performance_tab, self.lang.get("visualization.performance", "Performance"))
        
        # Comparison tab
        self.comparison_tab = QWidget()
        self.setup_comparison_tab()
        self.tab_widget.addTab(self.comparison_tab, self.lang.get("visualization.comparison", "Comparison"))
        
        # History tab
        self.history_tab = QWidget()
        self.setup_history_tab()
        self.tab_widget.addTab(self.history_tab, self.lang.get("visualization.history", "History"))
        
        # Set default tab
        self.tab_widget.setCurrentIndex(0)
    
    def setup_summary_tab(self):
        """Set up the summary tab with key metrics."""
        layout = QVBoxLayout(self.summary_tab)
        
        # Add a scroll area for the summary
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Overall score card
        overall_group = QGroupBox(self.lang.get("visualization.overall_score", "Overall Score"))
        overall_layout = QHBoxLayout(overall_group)
        
        self.score_label = QLabel("-")
        self.score_label.setAlignment(Qt.AlignCenter)
        score_font = self.score_label.font()
        score_font.setPointSize(24)
        score_font.setBold(True)
        self.score_label.setFont(score_font)
        
        overall_layout.addWidget(self.score_label)
        scroll_layout.addWidget(overall_group)
        
        # Category scores
        self.category_groups = {}
        for category in ['cpu', 'memory', 'disk']:
            group = QGroupBox(self.lang.get(f"visualization.category_{category}", category.capitalize()))
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
            series.append(x, y)
        
        # Add series to chart
        chart.addSeries(series)
        
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
    
    def _filter_results(self, results):
        """Filter results based on selected time range."""
        time_range = self.time_range_combo.currentData()
        if time_range == "all":
            return results
        
        now = datetime.now()
        filtered = []
        
        for result in results:
            delta = now - result.timestamp
            if time_range == "week" and delta.days <= 7:
                filtered.append(result)
            elif time_range == "month" and delta.days <= 30:
                filtered.append(result)
        
        return filtered or results[-10:]  # Return at least the last 10 results if filtered is empty
    
    def _update_chart_view(self, chart):
        """Update the chart view with the given chart."""
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
        
        # Set the widget as the central widget
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        
        # Replace the current chart view
        old_chart = self.performance_tab.findChild(QChartView)
        if old_chart:
            self.performance_tab.layout().replaceWidget(old_chart, chart_view)
            old_chart.deleteLater()
        else:
            self.performance_tab.layout().addWidget(chart_view)
        
        self._update_chart_view(chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing, False)
        
        # Add the container to the chart view's layout
        self.chart_view.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self.chart_view)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(container)
    
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
        
    # Update history tab if needed
    if hasattr(self, 'update_history_chart'):
        self.update_history_chart()

def apply_theme(self, theme='light'):
    """Apply a color theme to the visualizer."""
    self.current_theme = theme
    if theme == 'dark':
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #e0e0e0;
            }
            QGroupBox {
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
    else:
        self.setStyleSheet("""
            QGroupBox {
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
def update_data(self):
    """Update the visualization with the latest data."""
    self.update_chart()
    def apply_theme(self, theme='light'):
        """Apply a color theme to the visualizer."""
        self.current_theme = theme
        if theme == 'dark':
            self.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                    color: #e0e0e0;
                }
                QGroupBox {
                    border: 1px solid #444;
                    border-radius: 5px;
                    margin-top: 10px;
                    padding-top: 15px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
            """)
        else:
            self.setStyleSheet("""
                QGroupBox {
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    margin-top: 10px;
                    padding-top: 15px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
            """)
    def update_data(self):
        """Update the visualization with the latest data."""
        self.update_chart()
