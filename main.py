#!/usr/bin/env python3
"""
Benchmark with PySide6 GUI
"""
import sys
import os
import traceback
import webbrowser
from time import perf_counter as clock
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QProgressBar, QSpinBox, QTextEdit,
                             QMessageBox, QMenuBar, QMenu, QStatusBar, QSizePolicy, QGroupBox,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt, QTimer, Signal, QObject, QThread, QRunnable, QThreadPool
from PySide6.QtGui import QAction, QIcon, QTextCursor, QFont

# Setup logger before other local imports
from script import logger
log = logger.logger

# Local imports
from script.version import __version__, APP_NAME, APP_DESCRIPTION
import script.about as about
from script.menu import create_menu_bar
from script.lang_mgr import get_language_manager, get_text
from script.theme_manager import get_theme_manager
from script.test_menu import TestMenu
from script.visualization import BenchmarkVisualizer
from script.benchmark_history import get_benchmark_history

# Log application startup
log.info(f"Starting {APP_NAME} v{__version__}")
log.info(f"Python {sys.version}")
log.info(f"Working directory: {os.getcwd()}")

# Signal class for thread-safe GUI updates
class BenchmarkSignals(QObject):
    progress_updated = Signal(int, int)  # current, total
    finished = Signal(float, float)  # benchtime, stones
    error = Signal(str)  # error message
    stopped = Signal()

# Worker class for running the benchmark in a separate thread
class BenchmarkWorker(QRunnable):
    def __init__(self, loops, benchmark):
        super().__init__()
        self.loops = loops
        self.benchmark = benchmark
        self.signals = BenchmarkSignals()
        self.is_running = True
        log.debug(f"Worker initialized with {loops} loops")
    
    def run(self):
        log.info(f"Starting benchmark with {self.loops} loops")
        start_time = clock()
        
        try:
            def progress_callback(current, total):
                if not self.is_running:
                    log.debug(f"Benchmark stopped at iteration {current}/{total}")
                    return False
                
                if current % 100 == 0 or current == total:  # Log every 100 iterations or at the end
                    log.debug(f"Progress: {current}/{total} iterations")
                    
                self.signals.progress_updated.emit(current, total)
                return True
            
            log.debug("Running benchmark...")
            benchtime, stones = self.benchmark.run_benchmark(
                self.loops,
                progress_callback=progress_callback
            )
            
            elapsed = clock() - start_time
            
            if self.is_running and benchtime is not None and stones is not None:
                log.info(f"Benchmark completed in {elapsed:.2f} seconds. Result: {stones:.2f} pystones/second")
                log.debug(f"Benchmark details: loops={self.loops}, time={benchtime:.2f}s, stones={stones:.2f}")
                self.signals.finished.emit(benchtime, stones)
            elif not self.is_running:
                log.info(f"Benchmark stopped after {elapsed:.2f} seconds")
                self.signals.stopped.emit()
                
        except Exception as e:
            error_msg = f"Error in benchmark: {str(e)}"
            log.error(error_msg, exc_info=True)  # Log full traceback
            self.signals.error.emit(error_msg)
        finally:
            log.debug("Worker execution completed")
    
    def stop(self):
        self.is_running = False
        self.benchmark.should_stop = True

# Original Pystone code with modifications for GUI integration
LOOPS = 50000
[Ident1, Ident2, Ident3, Ident4, Ident5] = range(1, 6)

class Record:
    def __init__(self, PtrComp=None, Discr=0, EnumComp=0, IntComp=0, StringComp=0):
        self.PtrComp = PtrComp
        self.Discr = Discr
        self.EnumComp = EnumComp
        self.IntComp = IntComp
        self.StringComp = StringComp
    
    def __del__(self):
        # Break circular references to help with garbage collection
        self.PtrComp = None
        
    def copy(self):
        return Record(self.PtrComp, self.Discr, self.EnumComp,
                     self.IntComp, self.StringComp)
                     
    def cleanup(self):
        # Explicit cleanup method to break circular references
        if hasattr(self, 'PtrComp') and isinstance(self.PtrComp, Record):
            self.PtrComp.cleanup()
            self.PtrComp = None

class PystoneBenchmark:
    def __init__(self):
        self.TRUE = 1
        self.FALSE = 0
        self.running = False
        self.should_stop = False
        self.current_loops = 0
        self.total_loops = LOOPS
        log.debug("Initializing PystoneBenchmark")
        self.setup_globals()
        log.debug("PystoneBenchmark initialization complete")

    def setup_globals(self):
        # Clean up existing Record objects to prevent memory leaks
        if hasattr(self, 'PtrGlb') and self.PtrGlb is not None:
            if hasattr(self.PtrGlb, 'cleanup'):
                self.PtrGlb.cleanup()
            self.PtrGlb = None
            
        if hasattr(self, 'PtrGlbNext') and self.PtrGlbNext is not None:
            if hasattr(self.PtrGlbNext, 'cleanup'):
                self.PtrGlbNext.cleanup()
            self.PtrGlbNext = None
            
        # Initialize globals
        self.IntGlob = 0
        self.BoolGlob = self.FALSE
        self.Char1Glob = '\0'
        self.Char2Glob = '\0'
        self.Array1Glob = [0] * 51
        self.Array2Glob = [row[:] for row in [self.Array1Glob] * 51]
        self.PtrGlb = None
        self.PtrGlbNext = None

    def start_benchmark(self):
        try:
            # Get benchmark parameters
            loops = self.iter_spin.value()
            self.total_runs = self.runs_spin.value()
            
            # Reset state
            self.current_run = 0
            self.results = []
            self.results_table.setRowCount(0)  # Clear previous results
            
            # Update UI
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.overall_progress.setValue(0)
            self.run_progress.setValue(0)
            
            # Start the first benchmark run
            self.run_next_benchmark(loops)
            
            log.info(f"Started benchmark with {self.total_runs} runs of {loops} iterations each")
            
        except Exception as e:
            log.error(f"Error starting benchmark: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to start benchmark:\n{str(e)}"
            )
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def run_benchmark(self, loops=LOOPS, progress_callback=None):
        # Ensure clean state
        self.setup_globals()
        self.running = True
        self.should_stop = False
        self.current_loops = 0
        self.total_loops = loops
        
        try:
            starttime = clock()
            # Warm-up loop with periodic checks for stop condition
            warmup_chunk = min(1000, max(1, loops // 100))  # Process in chunks to be more responsive
            for i in range(0, loops, warmup_chunk):
                if self.should_stop:
                    return None, None
                # Do actual work in chunks
                for _ in range(i, min(i + warmup_chunk, loops)):
                    pass  # Just burn cycles
            
            nulltime = clock() - starttime
            self.PtrGlbNext = Record()
            self.PtrGlb = Record()
            self.PtrGlb.PtrComp = self.PtrGlbNext
            self.PtrGlb.Discr = Ident1
            self.PtrGlb.EnumComp = Ident3
            self.PtrGlb.IntComp = 40
            self.PtrGlb.StringComp = "DHRYSTONE PROGRAM, SOME STRING"
            
            String1Loc = "DHRYSTONE PROGRAM, 1'ST STRING"
            self.Array2Glob[8][7] = 10
            
            starttime = clock()
            # Process in chunks to be more responsive to stop requests
            chunk_size = max(1, loops // 100)  # At least 1, at most 1% of total loops
            for i in range(0, loops, chunk_size):
                if self.should_stop:
                    return None, None
                    
                # Process a chunk of iterations
                end_chunk = min(i + chunk_size, loops)
                for j in range(i, end_chunk):
                    self.current_loops = j
                    
                    # Only call progress callback at chunk boundaries for better performance
                    if j == end_chunk - 1 and progress_callback:
                        progress_callback(j + 1, loops)
                
                self.Proc5()
                self.Proc4()
                IntLoc1 = 2
                IntLoc2 = 3
                String2Loc = "DHRYSTONE PROGRAM, 2'ND STRING"
                EnumLoc = Ident2
                self.BoolGlob = not self.Func2(String1Loc, String2Loc)
                
                while IntLoc1 < IntLoc2:
                    IntLoc3 = 5 * IntLoc1 - IntLoc2
                    IntLoc3 = self.Proc7(IntLoc1, IntLoc2)
                    IntLoc1 = IntLoc1 + 1
                    
                self.Proc8(self.Array1Glob, self.Array2Glob, IntLoc1, IntLoc3)
                self.PtrGlb = self.Proc1(self.PtrGlb)
                
                CharIndex = 'A'
                while CharIndex <= self.Char2Glob:
                    if EnumLoc == self.Func1(CharIndex, 'C'):
                        EnumLoc = self.Proc6(Ident1)
                    CharIndex = chr(ord(CharIndex) + 1)
                    
                IntLoc3 = IntLoc2 * IntLoc1
                IntLoc2 = IntLoc3 // IntLoc1
                IntLoc2 = 7 * (IntLoc3 - IntLoc2) - IntLoc1
                IntLoc1 = self.Proc2(IntLoc1)
                
            benchtime = clock() - starttime - nulltime
            
            if benchtime <= 0.0:
                loopsPerBenchtime = 0.0
            else:
                loopsPerBenchtime = (loops / benchtime)
                
            return benchtime, loopsPerBenchtime
            
        finally:
            self.running = False
            if progress_callback:
                progress_callback(loops, loops)  # Ensure progress bar reaches 100%

    # Original Pystone procedures follow...
    def Proc1(self, PtrParIn):
        PtrParIn.PtrComp = NextRecord = self.PtrGlb.copy()
        PtrParIn.IntComp = 5
        NextRecord.IntComp = PtrParIn.IntComp
        NextRecord.PtrComp = PtrParIn.PtrComp
        NextRecord.PtrComp = self.Proc3(NextRecord.PtrComp)
        
        if NextRecord.Discr == Ident1:
            NextRecord.IntComp = 6
            NextRecord.EnumComp = self.Proc6(PtrParIn.EnumComp)
            NextRecord.PtrComp = self.PtrGlb.PtrComp
            NextRecord.IntComp = self.Proc7(NextRecord.IntComp, 10)
        else:
            PtrParIn = NextRecord.copy()
            
        NextRecord.PtrComp = None
        return PtrParIn

    def Proc2(self, IntParIO):
        IntLoc = IntParIO + 10
        while 1:
            if self.Char1Glob == 'A':
                IntLoc = IntLoc - 1
                IntParIO = IntLoc - self.IntGlob
                EnumLoc = Ident1
            if EnumLoc == Ident1:
                break
        return IntParIO

    def Proc3(self, PtrParOut):
        if self.PtrGlb is not None:
            PtrParOut = self.PtrGlb.PtrComp
        else:
            self.IntGlob = 100
        self.PtrGlb.IntComp = self.Proc7(10, self.IntGlob)
        return PtrParOut

    def Proc4(self):
        BoolLoc = self.Char1Glob == 'A'
        BoolLoc = BoolLoc or self.BoolGlob
        self.Char2Glob = 'B'

    def Proc5(self):
        self.Char1Glob = 'A'
        self.BoolGlob = self.FALSE

    def Proc6(self, EnumParIn):
        EnumParOut = EnumParIn
        if not self.Func3(EnumParIn):
            EnumParOut = Ident4
            
        if EnumParIn == Ident1:
            EnumParOut = Ident1
        elif EnumParIn == Ident2:
            if self.IntGlob > 100:
                EnumParOut = Ident1
            else:
                EnumParOut = Ident4
        elif EnumParIn == Ident3:
            EnumParOut = Ident2
        elif EnumParIn == Ident4:
            pass
        elif EnumParIn == Ident5:
            EnumParOut = Ident3
            
        return EnumParOut

    def Proc7(self, IntParI1, IntParI2):
        IntLoc = IntParI1 + 2
        IntParOut = IntParI2 + IntLoc
        return IntParOut

    def Proc8(self, Array1Par, Array2Par, IntParI1, IntParI2):
        IntLoc = IntParI1 + 5
        Array1Par[IntLoc] = IntParI2
        Array1Par[IntLoc+1] = Array1Par[IntLoc]
        Array1Par[IntLoc+30] = IntLoc
        
        for IntIndex in range(IntLoc, IntLoc+2):
            Array2Par[IntLoc][IntIndex] = IntLoc
            
        Array2Par[IntLoc][IntLoc-1] = Array2Par[IntLoc][IntLoc-1] + 1
        Array2Par[IntLoc+20][IntLoc] = Array1Par[IntLoc]
        self.IntGlob = 5

    def Func1(self, CharPar1, CharPar2):
        CharLoc1 = CharPar1
        CharLoc2 = CharLoc1
        if CharLoc2 != CharPar2:
            return Ident1
        else:
            return Ident2

    def Func2(self, StrParI1, StrParI2):
        IntLoc = 1
        while IntLoc <= 1:
            if self.Func1(StrParI1[IntLoc], StrParI2[IntLoc+1]) == Ident1:
                CharLoc = 'A'
                IntLoc = IntLoc + 1
                
        if CharLoc >= 'W' and CharLoc <= 'Z':
            IntLoc = 7
            
        if CharLoc == 'X':
            return self.TRUE
        else:
            if StrParI1 > StrParI2:
                IntLoc = IntLoc + 7
                return self.TRUE
            else:
                return self.FALSE

    def Func3(self, EnumParIn):
        pass

class PystoneApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.retranslate_ui()
        self.setup_connections()
        self.load_settings()
        
        # Initialize history dialog
        self.history_dialog = None
        
        # Apply theme
        theme_manager = get_theme_manager(self)
        if theme_manager:
            theme_manager.apply_theme()
            
    def show_visualization(self):
        """Show the visualization window."""
        if not hasattr(self, 'visualization_window') or not self.visualization_window:
            self.visualization_window = BenchmarkVisualizer()
            self.visualization_window.setWindowTitle(f"{APP_NAME} - {get_text('visualization')}")
            
            # Connect theme changes
            theme_manager = get_theme_manager()
            if theme_manager:
                theme_manager.theme_changed.connect(self.visualization_window.apply_theme)
        
        # Update data before showing
        self.visualization_window.update_benchmark_data()
        self.visualization_window.show()
        self.visualization_window.raise_()
        self.visualization_window.activateWindow()
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save window state
        settings = QSettings()
        settings.setValue("window/geometry", self.saveGeometry())
        settings.setValue("window/state", self.saveState())
        
        # Clean up resources
        if hasattr(self, 'benchmark'):
            self.benchmark.running = False
        
        # Close visualization window if open
        if hasattr(self, 'visualization_window') and self.visualization_window:
            self.visualization_window.close()
        
        event.accept()
        
    def setup_ui(self):
        # Main window setup
        self.setWindowTitle("Benchmark")
        self.setGeometry(100, 100, 800, 600)
        
        # Create menu bar
        self.create_menu()
        
        # Create main content area
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Add benchmark tab
        self.benchmark_tab = QWidget()
        self.setup_benchmark_tab()
        self.tab_widget.addTab(self.benchmark_tab, self.lang.get("tabs.benchmark", "Benchmark"))
        
        # Add visualization tab
        from visualization import BenchmarkVisualizer
        self.visualization_tab = BenchmarkVisualizer()
        self.tab_widget.addTab(self.visualization_tab, self.lang.get("tabs.visualization", "Visualization"))
        
        # Create a container widget for the main content
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 10, 20, 20)
        
        # Add title label
        self.title_label = QLabel(APP_NAME)
        self.title_label.setAlignment(Qt.AlignCenter)
        title_font = self.title_label.font()
        title_font.setPointSize(18)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        content_layout.addWidget(self.title_label)
        
        # Add description label
        self.desc_label = QLabel(APP_DESCRIPTION)
        self.desc_label.setAlignment(Qt.AlignCenter)
        self.desc_label.setWordWrap(True)
        content_layout.addWidget(self.desc_label)
        
        # Add some spacing
        content_layout.addSpacing(20)
        
        # Create settings group
        settings_group = QWidget()
        settings_layout = QFormLayout()
        
        # Add iterations control
        iter_label = QLabel("Iterations per run:")
        self.iter_spin = QSpinBox()
        self.iter_spin.setRange(1000, 1000000)
        self.iter_spin.setValue(LOOPS)
        self.iter_spin.setSingleStep(1000)
        settings_layout.addRow(iter_label, self.iter_spin)
        
        # Add number of runs control
        runs_label = QLabel("Number of runs:")
        self.runs_spin = QSpinBox()
        self.runs_spin.setRange(1, 100)
        self.runs_spin.setValue(1)
        self.runs_spin.setSingleStep(1)
        settings_layout.addRow(runs_label, self.runs_spin)
        
        settings_group.setLayout(settings_layout)
        content_layout.addWidget(settings_group)
        
        # Add progress bars
        progress_group = QWidget()
        progress_layout = QVBoxLayout()
        
        # Overall progress
        self.overall_progress = QProgressBar()
        self.overall_progress.setRange(0, 100)
        self.overall_progress.setValue(0)
        self.overall_progress.setTextVisible(True)
        self.overall_progress.setFormat("Overall: %p%")
        progress_layout.addWidget(QLabel("Overall Progress:"))
        progress_layout.addWidget(self.overall_progress)
        
        # Current run progress
        self.run_progress = QProgressBar()
        self.run_progress.setRange(0, 100)
        self.run_progress.setValue(0)
        self.run_progress.setTextVisible(True)
        self.run_progress.setFormat("Current Run: %p%")
        progress_layout.addWidget(QLabel("Current Run Progress:"))
        progress_layout.addWidget(self.run_progress)
        
        progress_group.setLayout(progress_layout)
        content_layout.addWidget(progress_group)
        
        # Add status and results labels
        status_group = QWidget()
        status_layout = QVBoxLayout()
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignLeft)
        status_layout.addWidget(self.status_label)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Run #", "Pystones/sec", "Time (s)"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        status_layout.addWidget(self.results_table)
        
        # Statistics label
        self.stats_label = QLabel("")
        self.stats_label.setAlignment(Qt.AlignLeft)
        status_layout.addWidget(self.stats_label)
        
        status_group.setLayout(status_layout)
        content_layout.addWidget(status_group)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        self.run_button = QPushButton()
        self.run_button.clicked.connect(self.start_benchmark)
        button_layout.addWidget(self.run_button)
        
        self.visualize_button = QPushButton()
        self.visualize_button.clicked.connect(self.show_visualization)
        button_layout.addWidget(self.visualize_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_benchmark)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        content_layout.addLayout(button_layout)
        
        # Add the content widget to the main layout
        layout.addWidget(content_widget)
        
    def create_menu(self):
        # Create menu bar
        self.menu_bar = create_menu_bar(self)
        self.setMenuBar(self.menu_bar)
        
        # Main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)
        
        # Initialize visualization window
        self.visualization_window = None
        
        # Add Test menu
        self.test_menu = TestMenu(self)
        self.menu_bar.addMenu(self.test_menu)
        
        # View menu
        view_menu = self.menu_bar.addMenu("&View")
        
        # History action
        self.history_action = QAction("History", self)
        self.history_action.triggered.connect(self.show_history)
        view_menu.addAction(self.history_action)
        
        view_menu.addSeparator()
        
        # Theme submenu
        theme_menu = view_menu.addMenu("Theme")
        
        # Add theme actions
        theme_manager = get_theme_manager(self)
        if theme_manager:
            for theme in theme_manager.get_themes():
                action = QAction(theme, self)
                action.triggered.connect(lambda theme=theme: theme_manager.apply_theme(theme))
                theme_menu.addAction(action)
        
        # Help menu
        help_menu = self.menu_bar.addMenu("&Help")
        
        # About action
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Logs action
        logs_action = QAction("View Logs", self)
        logs_action.triggered.connect(self.view_logs)
        help_menu.addAction(logs_action)
        
    def retranslate_ui(self):
        """Update UI text based on current language."""
        _ = get_text
        self.setWindowTitle(_("window_title").format(APP_NAME))
        self.run_button.setText(_("start_benchmark"))
        self.stop_button.setText(_("stop_benchmark"))
        self.visualize_button.setText(_("visualize_results"))
        self.loops_label.setText(_("iterations"))
        self.results_group.setTitle(_("results"))
        
        # Update history action text
        if hasattr(self, 'history_action'):
            self.history_action.setText(_("history.title"))
        
        # Update UI elements with translations
        if hasattr(self, 'start_button'):
            self.start_button.setText(self.lang.get("app.start_benchmark", "Start Benchmark"))
        if hasattr(self, 'stop_button'):
            self.stop_button.setText(self.lang.get("app.stop_benchmark", "Stop"))
        if hasattr(self, 'iterations_label'):
            self.iterations_label.setText(self.lang.get("app.iterations", "Iterations per run:"))
        if hasattr(self, 'results_label'):
            self.results_label.setText(self.lang.get("app.benchmark_results", "Benchmark Results"))
        if hasattr(self, 'status_label'):
            self.status_label.setText(self.lang.get("app.status_ready", "Ready"))
        
    def setup_connections(self):
        # Connect signals
        self.signals = BenchmarkSignals()
        self.signals.progress_updated.connect(self.update_progress)
        self.signals.finished.connect(self.benchmark_completed)
        self.signals.error.connect(self.benchmark_error)
        self.signals.stopped.connect(self.benchmark_stopped)
    
    def load_settings(self):
        # Load settings from QSettings
        settings = QSettings("YourCompany", "Benchmark")
        self.restoreGeometry(settings.value("geometry"))
        self.restoreState(settings.value("windowState"))
    
    def start_benchmark(self):
        """Start the benchmark with the current settings."""
        try:
            # Get benchmark parameters
            loops = self.iter_spin.value()
            self.total_runs = self.runs_spin.value()
            
            # Reset state
            self.current_run = 0
            self.results = []
            self.results_table.setRowCount(0)  # Clear previous results
            
            # Update UI
            self.run_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.overall_progress.setValue(0)
            self.run_progress.setValue(0)
            
            # Start the first benchmark run
            self.run_next_benchmark(loops)
            
            log.info(f"Started benchmark with {self.total_runs} runs of {loops} iterations each")
            
        except Exception as e:
            log.error(f"Error starting benchmark: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to start benchmark:\n{str(e)}"
            )
            self.run_button.setEnabled(True)
            self.stop_button.setEnabled(False)
        
    def run_next_benchmark(self, loops):
        self.current_run += 1
        self.statusBar().showMessage(f"Running benchmark {self.current_run} of {self.total_runs}...")
        self.overall_progress.setValue(int((self.current_run - 1) * 100 / self.total_runs))
        self.run_progress.setValue(0)
        
        # Clean up any existing worker
        if self.worker is not None:
            try:
                self.worker.signals.progress_updated.disconnect()
                self.worker.signals.finished.disconnect()
                self.worker.signals.error.disconnect()
            except:
                pass
            
        # Create a worker thread for the benchmark
        log.debug(f"Creating benchmark worker for run {self.current_run}")
        self.worker = BenchmarkWorker(loops, PystoneBenchmark())
        self.worker.signals.progress_updated.connect(self.update_progress)
        self.worker.signals.finished.connect(self.benchmark_completed)
        self.worker.signals.error.connect(self.benchmark_error)
        
        # Start the worker in the thread pool
        log.debug("Starting worker in thread pool")
        QThreadPool.globalInstance().start(self.worker)
    
    def update_progress(self, current, total):
        if total > 0:
            progress = int((current / total) * 100)
            self.run_progress.setValue(progress)
            # Update status bar with progress
            self.status_label.setText(self.lang.get("app.status_running", "Running") + f'... {progress}%')
            
            # Calculate overall progress across all runs
            if self.total_runs > 1:
                run_progress = (self.current_run - 1) * 100
                current_run_progress = progress / self.total_runs
                overall_progress = int(run_progress + current_run_progress)
                self.overall_progress.setValue(overall_progress)
                
                message = (
                    f"Run {self.current_run} of {self.total_runs}: "
                    f"{current:,} of {total:,} iterations ({progress}%)"
                )
                self.statusBar().showMessage(message)
            else:
                self.statusBar().showMessage(f"Running... {current:,} of {total:,} iterations")
            
            QApplication.processEvents()
    
    def benchmark_completed(self, result):
        """Handle benchmark completion."""
        self.update_ui_after_benchmark()
        self.statusBar().showMessage(
            self.lang.get("app.benchmark_completed", "Benchmark completed in {0:.2f} seconds").format(
                result["time_elapsed"]
            )
        )
        
        # Save to history
        self.save_to_history(result)
        
        # Update results display
        self.update_results_display()
        
        # Prepare for the next run or finish
        self.current_run += 1
        if self.current_run <= self.total_runs:
            # Start the next run
            self.run_next_benchmark(result["loops"])
        else:
            # All runs completed
            self.status_bar.showMessage("Benchmark completed")
            self.run_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            
            # Calculate and display statistics if we did multiple runs
            if len(self.results) > 1:
                times = [r["time_elapsed"] for r in self.results]
                pystones = [r["pystones"] for r in self.results]
                
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)
                
                avg_pystones = sum(pystones) / len(pystones)
                min_pystones = min(pystones)
                max_pystones = max(pystones)
                
                stats = (
                    f"\n--- Statistics (over {len(self.results)} runs) ---\n"
                    f"Average time: {avg_time:.2f}s (min: {min_time:.2f}s, max: {max_time:.2f}s)\n"
                    f"Average performance: {avg_pystones:.2f} pystones/sec (min: {min_pystones:.2f}, max: {max_pystones:.2f})"
                )
                
                self.results_text.append(stats)
                log.info(f"Benchmark statistics:{stats}")
    
    def update_results_display(self):
        """Update the results display with the latest benchmark results."""
        try:
            if not hasattr(self, 'results_text') or not self.results:
                return
                
            # Clear previous results
            self.results_text.clear()
            
            # Add column headers
            self.results_text.append("Run #\tTime (s)\tPystones/sec")
            self.results_text.append("-" * 50)
            
            # Add each result
            for result in self.results:
                self.results_text.append(
                    f"{result['run']:4d}\t"
                    f"{result['time_elapsed']:8.2f}\t"
                    f"{result['pystones']:10.2f}"
                )
                
            # Scroll to the bottom to show the latest results
            self.results_text.verticalScrollBar().setValue(
                self.results_text.verticalScrollBar().maximum()
            )
            
        except Exception as e:
            log.error(f"Error updating results display: {e}", exc_info=True)
        
    def save_to_history(self, result):
        """Save benchmark result to history."""
        try:
            from script.benchmark_history import get_benchmark_history
            from datetime import datetime
            import psutil
            import platform
            
            # Get system information
            cpu_info = {
                'model': platform.processor(),
                'cores': psutil.cpu_count(logical=False) or 1,
                'threads': psutil.cpu_count() or 1
            }
            
            system_info = {
                'system': {
                    'system': platform.system(),
                    'version': platform.version(),
                    'machine': platform.machine()
                },
                'cpu': cpu_info,
                'memory': {
                    'total': psutil.virtual_memory().total,
                    'available': psutil.virtual_memory().available
                }
            }
            
            # Create benchmark result
            history = get_benchmark_history()
            history.add_result(
                pystones=result["pystones"],
                time_elapsed=result["time_elapsed"],
                iterations=result["loops"],
                system_info=system_info
            )
            
        except Exception as e:
            logging.error(f"Error saving to history: {e}")
    
    def show_history(self):
        """Show the benchmark history dialog."""
        if not self.history_dialog:
            self.history_dialog = HistoryDialog(self)
            self.history_dialog.result_selected.connect(self.on_history_result_selected)
        
        self.history_dialog.show()
        self.history_dialog.raise_()
        self.history_dialog.activateWindow()
    
    def on_history_result_selected(self, result):
        """Handle selection of a result from history."""
        # Update UI with the selected result
        self.pystones_label.setText(f"{result.pystones:,.2f}")
        self.time_label.setText(f"{result.time_elapsed:.2f}")
        self.iterations_label.setText(f"{result.iterations:,}")
        
        # Show a message
        self.statusBar().showMessage(
            self.lang.get("history.result_loaded", "Loaded result from {}").format(
                datetime.fromtimestamp(result.timestamp).strftime("%Y-%m-%d %H:%M:%S")
            )
        )
    
    def stop_benchmark(self):
        """Stop the currently running benchmark."""
        if hasattr(self, 'worker') and self.worker is not None and hasattr(self.worker, 'is_running') and self.worker.is_running:
            log.info("Stopping benchmark...")
            self.worker.is_running = False
            self.worker.signals.stopped.emit()
            self.status_bar.showMessage("Benchmark stopped by user")
            
            # Reset UI
            self.run_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            
            # Reset progress
            if hasattr(self, 'progress_bar'):
                self.progress_bar.setValue(0)
    
    def benchmark_stopped(self):
        try:
            log.info("Benchmark stopped by user")
            # Update status bar when benchmark is stopped
            self.status_label.setText(self.lang.get("app.status_stopped", "Benchmark stopped by user"))
            
            # Update UI state
            if hasattr(self, 'start_btn'):
                self.start_btn.setEnabled(True)
            if hasattr(self, 'stop_btn'):
                self.stop_btn.setEnabled(False)
            if hasattr(self, 'progress'):
                self.progress.setValue(0)
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage("Benchmark stopped")
                
            log.debug("Benchmark stopped and UI reset")
            
        except Exception as e:
            error_msg = f"Error in benchmark_stopped: {str(e)}"
            log.error(error_msg, exc_info=True)
            try:
                # Try to show error to user
                if hasattr(self, 'status_bar'):
                    self.status_bar.showMessage("Error stopping benchmark")
            except:
                pass
                
    def closeEvent(self, event):
        # Clean up the worker thread if running
        if hasattr(self, 'worker') and self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self, 
                self.lang.get("messages.confirm_exit", "Confirm Exit"),
                self.lang.get("messages.benchmark_running", "A benchmark is currently running. Are you sure you want to exit?"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.worker.stop()
                event.accept()
            else:
                event.ignore()
                return
        
        # Clean up the update checker
        try:
            from script.updates import get_updates_module
            update_checker = get_updates_module()
            if hasattr(update_checker, 'shutdown'):
                update_checker.shutdown()
        except Exception as e:
            logger.error(f"Error during update checker cleanup: {e}")
        
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Set application style and theme
    app.setStyle('Fusion')
    
    # Initialize and apply theme
    theme_manager = get_theme_manager(app)
    if theme_manager:
        theme_manager.apply_theme()
    
    # Set application information
    app.setApplicationName("Pystone Benchmark")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("Nsfr750")
    
    # Create and show the main window
    window = PystoneApp()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
