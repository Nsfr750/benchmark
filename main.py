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
    def show_about(self):
        """Show the about dialog using the about module."""
        about.show_about(self)
    
    def benchmark_completed(self, benchtime, stones):
        """Handle the completion of a benchmark run."""
        try:
            log.info(f"Benchmark completed in {benchtime:.2f} seconds ({stones:.2f} pystones/second)")
            # Update status bar with completion message
            self.status_label.setText(self.lang_manager.get_text('status.completed', 'Benchmark completed') + 
                                   f' - {stones:.2f} pystones/second')
            
            # Store the result
            self.results.append({
                'run': self.current_run,
                'time': benchtime,
                'stones': stones
            })
            
            # Update the results display
            self.update_results_display()
            
            # Prepare for the next run or finish
            self.current_run += 1
            if self.current_run <= self.total_runs:
                # Start the next run
                self.start_benchmark()
            else:
                # All runs completed
                self.status_bar.showMessage("Benchmark completed")
                self.start_button.setEnabled(True)
                self.stop_button.setEnabled(False)
                
                # Calculate and display statistics if we did multiple runs
                if len(self.results) > 1:
                    times = [r['time'] for r in self.results]
                    stones = [r['stones'] for r in self.results]
                    
                    avg_time = sum(times) / len(times)
                    min_time = min(times)
                    max_time = max(times)
                    
                    avg_stones = sum(stones) / len(stones)
                    min_stones = min(stones)
                    max_stones = max(stones)
                    
                    stats = (
                        f"\n--- Statistics (over {len(self.results)} runs) ---\n"
                        f"Average time: {avg_time:.2f}s (min: {min_time:.2f}s, max: {max_time:.2f}s)\n"
                        f"Average performance: {avg_stones:.2f} pystones/sec (min: {min_stones:.2f}, max: {max_stones:.2f})"
                    )
                    
                    self.results_text.append(stats)
                    log.info(f"Benchmark statistics:{stats}")
            
        except Exception as e:
            log.error(f"Error in benchmark_completed: {e}", exc_info=True)
            self.status_bar.showMessage("Error processing benchmark results")
    
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
                    f"{result['time']:8.2f}\t"
                    f"{result['stones']:10.2f}"
                )
                
            # Scroll to the bottom to show the latest results
            self.results_text.verticalScrollBar().setValue(
                self.results_text.verticalScrollBar().maximum()
            )
            
        except Exception as e:
            log.error(f"Error updating results display: {e}", exc_info=True)
        
    def __init__(self):
        super().__init__()
        log.info("Initializing PystoneApp")
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'logo.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            log.debug(f"Application icon set from {icon_path}")
        else:
            log.warning(f"Icon file not found at {icon_path}")
        
        # Initialize language manager
        self.lang_manager = get_language_manager()
        
        # Initialize benchmark state
        self.current_run = 0
        self.total_runs = 1
        self.results = []
        self.benchmark = PystoneBenchmark()
        self.worker = None
        
        # Create a single thread pool for the application
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(1)  # Ensure only one benchmark runs at a time
        
        # Initialize UI
        self.setup_ui()
        self.retranslate_ui()
        
        # Connect signals
        self.signals = BenchmarkSignals()
        self.signals.progress_updated.connect(self.update_progress)
        self.signals.finished.connect(self.benchmark_completed)
        self.signals.error.connect(self.benchmark_error)
        self.signals.stopped.connect(self.benchmark_stopped)
        
        log.info("PystoneApp initialization complete")

    def benchmark_error(self, error_msg):
        """Handle errors that occur during benchmark execution."""
        try:
            log.error(f"Benchmark error: {error_msg}")
            error_text = self.lang_manager.get_text('error.benchmark_failed', 'Benchmark failed: ') + str(error_msg)
            QMessageBox.critical(self, self.lang_manager.get_text('error.title', 'Error'), error_text)
            # Update status bar with error
            self.status_label.setText(self.lang_manager.get_text('status.error', 'Error') + ': ' + str(error_msg))
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(f"Error: {error_msg}")
            
            # Re-enable UI elements
            if hasattr(self, 'start_btn'):
                self.start_btn.setEnabled(True)
            if hasattr(self, 'stop_btn'):
                self.stop_btn.setEnabled(False)
                
            # Show error message to user
            QMessageBox.critical(self, "Benchmark Error", 
                              f"An error occurred during benchmark execution:\n\n{error_msg}")
            
        except Exception as e:
            log.error(f"Error in benchmark_error handler: {str(e)}", exc_info=True)
            
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
        
        # Initialize language manager
        self.lang_manager = get_language_manager()
        
        # Set up the UI with the default language
        self.setup_ui()
        self.retranslate_ui()
        
        # Initialize benchmark
        self.benchmark = PystoneBenchmark()
        self.worker = None
        self.thread_pool = QThreadPool()
        
        # Benchmark state
        self.current_run = 0
        self.total_runs = 1
        self.results = []
        
        # Connect signals
        self.signals = BenchmarkSignals()
        self.signals.progress_updated.connect(self.update_progress)
        self.signals.finished.connect(self.benchmark_completed)
        self.signals.error.connect(self.benchmark_error)
        self.signals.stopped.connect(self.benchmark_stopped)
        log.info("PystoneApp initialization complete")
        
    def retranslate_ui(self):
        """Update all UI elements with current language."""
        self.setWindowTitle(f"{get_text('app.title')} {__version__}")
        self.setWindowIcon(QIcon.fromTheme("utilities-system-monitor"))
        self.resize(600, 450)
        
        # Update UI elements with translations
        if hasattr(self, 'start_button'):
            self.start_button.setText(get_text('app.start_benchmark'))
        if hasattr(self, 'stop_button'):
            self.stop_button.setText(get_text('app.stop_benchmark'))
        if hasattr(self, 'iterations_label'):
            self.iterations_label.setText(get_text('app.iterations'))
        if hasattr(self, 'results_label'):
            self.results_label.setText(get_text('app.benchmark_results'))
        if hasattr(self, 'status_label'):
            self.status_label.setText(get_text('app.status_ready'))
            
    def change_language(self, lang_code):
        """Change the application language.
        
        Args:
            lang_code: Language code (e.g., 'en', 'it')
        """
        if self.lang_manager.load_language(lang_code):
            # Remove existing menu bar
            if hasattr(self, 'menuBar'):
                self.menuBar().setParent(None)
            
            # Recreate menu bar with new language
            self.menuBar = create_menu_bar(self)
            self.setMenuBar(self.menuBar)
            
            # Update UI with new translations
            self.retranslate_ui()
            log.info(f"Language changed to {lang_code}")
        
    def setup_ui(self):
        """Set up the main window UI components."""
        log.debug("Setting up UI components")
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Add version label to status bar
        self.version_label = QLabel(f"v{__version__}")
        self.statusBar.addPermanentWidget(self.version_label)
        
        # Add status label to status bar
        self.status_label = QLabel(self.lang_manager.get_text('status.ready', 'Ready'))
        self.statusBar.addWidget(self.status_label, 1)  # Stretch factor of 1 to take available space
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create and add the menu bar using the menu module
        menubar = create_menu_bar(self)
        self.setMenuBar(menubar)
        
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
        settings_group = QGroupBox("Benchmark Settings")
        settings_layout = QVBoxLayout()
        
        # Add iterations control
        iter_layout = QHBoxLayout()
        iter_label = QLabel("Iterations per run:")
        self.iter_spin = QSpinBox()
        self.iter_spin.setRange(1000, 1000000)
        self.iter_spin.setValue(LOOPS)
        self.iter_spin.setSingleStep(1000)
        iter_layout.addWidget(iter_label)
        iter_layout.addWidget(self.iter_spin)
        
        # Add number of runs control
        runs_label = QLabel("Number of runs:")
        self.runs_spin = QSpinBox()
        self.runs_spin.setRange(1, 100)
        self.runs_spin.setValue(1)
        self.runs_spin.setSingleStep(1)
        iter_layout.addWidget(runs_label)
        iter_layout.addWidget(self.runs_spin)
        iter_layout.addStretch()
        settings_layout.addLayout(iter_layout)
        
        settings_group.setLayout(settings_layout)
        content_layout.addWidget(settings_group)
        
        # Add progress bars
        progress_group = QGroupBox("Progress")
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
        status_group = QGroupBox("Status & Results")
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
        
        self.start_button = QPushButton("Start Benchmark")
        self.start_button.clicked.connect(self.start_benchmark)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_benchmark)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        content_layout.addLayout(button_layout)
        
        # Add results text area
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Courier"))
        content_layout.addWidget(self.results_text)
        
        # Add the content widget to the main layout
        layout.addWidget(content_widget)
        
    def stop_benchmark(self):
        """Stop the currently running benchmark."""
        if hasattr(self, 'worker') and self.worker is not None and hasattr(self.worker, 'is_running') and self.worker.is_running:
            log.info("Stopping benchmark...")
            self.worker.is_running = False
            self.worker.signals.stopped.emit()
            self.status_bar.showMessage("Benchmark stopped by user")
            
            # Reset UI
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            
            # Reset progress
            if hasattr(self, 'progress_bar'):
                self.progress_bar.setValue(0)
    
    def update_progress(self, current, total):
        if total > 0:
            progress = int((current / total) * 100)
            self.run_progress.setValue(progress)
            # Update status bar with progress
            self.status_label.setText(self.lang_manager.get_text('status.running', 'Running') + f'... {progress}%')
            
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
        self.worker = BenchmarkWorker(loops, self.benchmark)
        self.worker.signals.progress_updated.connect(self.update_progress)
        self.worker.signals.finished.connect(self.benchmark_completed)
        self.worker.signals.error.connect(self.benchmark_error)
        
        # Start the worker in the thread pool
        log.debug("Starting worker in thread pool")
        self.thread_pool.start(self.worker)
    
    def run_benchmark(self, loops):
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
        self.worker = BenchmarkWorker(loops, self.benchmark)
        self.worker.signals.progress_updated.connect(self.update_progress)
        self.worker.signals.finished.connect(self.benchmark_completed)
        self.worker.signals.error.connect(self.benchmark_error)
        
        # Start the worker in the thread pool
        log.debug("Starting worker in thread pool")
        self.thread_pool.start(self.worker)
        
    def benchmark_stopped(self):
        try:
            log.info("Benchmark stopped by user")
            # Update status bar when benchmark is stopped
            self.status_label.setText(self.lang_manager.get_text('status.stopped', 'Benchmark stopped by user'))
            
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
                
    def stop_benchmark(self):
        try:
            # Signal the benchmark to stop
            if hasattr(self, 'benchmark') and self.benchmark is not None:
                self.benchmark.should_stop = True
                
            # Stop any running worker
            if hasattr(self, 'worker') and self.worker is not None:
                self.worker.stop()
                self.worker = None
                
            # Calculate statistics if we have results
            if hasattr(self, 'results') and self.results:
                try:
                    # Extract pystones and times from results
                    pystones = [r[1] for r in self.results]  # stones is the second element
                    times = [r[0] for r in self.results]     # benchtime is the first element
                    
                    # Calculate statistics
                    avg_pystones = sum(pystones) / len(pystones)
                    min_pystones = min(pystones)
                    max_pystones = max(pystones)
                    avg_time = sum(times) / len(times)
                    
                    # Create stats text
                    stats_text = (
                        f"Completed {len(self.results)} benchmark(s). "
                        f"Average: {avg_pystones:,.2f} pystones/sec, "
                        f"Min: {min_pystones:,.2f}, "
                        f"Max: {max_pystones:,.2f}, "
                        f"Avg Time: {avg_time:.4f}s"
                    )
                    
                    # Update stats label if it exists
                    if hasattr(self, 'stats_label'):
                        self.stats_label.setText(stats_text)
                    
                    # Show completion message
                    try:
                        from PySide6.QtWidgets import QMessageBox
                        QMessageBox.information(
                            self,
                            "Benchmark Complete",
                            f"Completed {len(self.results)} benchmark runs.\n\n"
                            f"Average: {avg_pystones:,.2f} pystones/sec\n"
                            f"Best: {max_pystones:,.2f} pystones/sec\n"
                            f"Worst: {min_pystones:,.2f} pystones/sec\n"
                            f"Average time: {avg_time:.4f} seconds"
                        )
                    except Exception as msg_box_error:
                        log.error(f"Failed to show completion message: {msg_box_error}")
                    
                except Exception as stats_error:
                    log.error(f"Error calculating statistics: {stats_error}", exc_info=True)
                    if hasattr(self, 'status_bar'):
                        self.status_bar.showMessage("Benchmark stopped with partial results")
            else:
                if hasattr(self, 'status_bar'):
                    self.status_bar.showMessage("Benchmark stopped - no results yet")
            
            # Update UI state
            if hasattr(self, 'start_btn'):
                self.start_btn.setEnabled(True)
            if hasattr(self, 'stop_btn'):
                self.stop_btn.setEnabled(False)
                
        except Exception as e:
            error_msg = f"Error stopping benchmark: {str(e)}"
            log.error(error_msg, exc_info=True)
            
            # Try to update UI to show error
            try:
                if hasattr(self, 'status_bar'):
                    self.status_bar.showMessage("Error stopping benchmark")
                
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(
                    self,
                    "Error",
                    f"An error occurred while stopping the benchmark.\n\n{str(e)}"
                )
            except Exception as ui_error:
                log.error(f"Failed to update UI with error: {ui_error}")
                
            # Ensure UI is in a consistent state
            try:
                if hasattr(self, 'start_btn'):
                    self.start_btn.setEnabled(True)
                if hasattr(self, 'stop_btn'):
                    self.stop_btn.setEnabled(False)
                if hasattr(self, 'progress'):
                    self.progress.setValue(0)
                if hasattr(self, 'status_bar'):
                    self.status_bar.showMessage("Benchmark stopped")
            except Exception as ui_error:
                log.error(f"Failed to reset UI state: {ui_error}")
                self.status_bar.showMessage("Benchmark error")
                
            log.debug("UI reset after benchmark error")
            
        except Exception as e:
            # If we can't show the error dialog, at least log it
            log.critical(f"Critical error in benchmark_error handler: {e}\nOriginal error: {error_msg}", 
                        exc_info=True)
    
    def view_logs(self):
        """Show the log viewer dialog."""
        from script.view_log import show_log_viewer
        show_log_viewer(self)
        
    def closeEvent(self, event):
        # Clean up the worker thread if running
        if hasattr(self, 'worker') and self.worker and self.worker.is_running:
            reply = QMessageBox.question(
                self, 
                self.lang_manager.get_text("messages.confirm_exit", "Confirm Exit"),
                self.lang_manager.get_text("messages.benchmark_running", "A benchmark is currently running. Are you sure you want to exit?"),
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
    
    # Set application style
    app.setStyle('Fusion')
    
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
