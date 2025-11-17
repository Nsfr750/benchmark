"""
Pystone benchmark test dialog.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton,
    QHBoxLayout, QTextEdit, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, QThread, Signal, QObject
from .CLI_pystone import pystones
import time


class PystoneWorker(QObject):
    """Worker thread for running the Pystone benchmark."""
    
    finished = Signal(float, float)  # benchtime, stones
    progress = Signal(int, float, float)  # current, total, progress
    
    def __init__(self, loops=50000):
        super().__init__()
        self.loops = loops
        self.is_running = True
        
    def run(self):
        """Run the benchmark."""
        try:
            start_time = time.time()
            
            # Run the benchmark
            benchtime, stones = pystones(self.loops)
            
            # Calculate elapsed time
            elapsed = time.time() - start_time
            
            if self.is_running:
                self.finished.emit(benchtime, stones)
                
        except Exception as e:
            print(f"Error in Pystone benchmark: {e}")
            self.finished.emit(0, 0)
    
    def stop(self):
        """Stop the benchmark."""
        self.is_running = False


class PystoneDialog(QDialog):
    """Dialog for running and displaying Pystone benchmark results."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pystone Benchmark")
        self.setMinimumSize(500, 400)
        self.setup_ui()
        
        # Initialize worker thread
        self.worker = None
        self.thread = None
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Status label
        self.status_label = QLabel("Ready to run benchmark...")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Results display
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setLineWrapMode(QTextEdit.NoWrap)
        layout.addWidget(self.results_text, 1)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.run_button = QPushButton("Run Benchmark")
        self.run_button.clicked.connect(self.run_benchmark)
        button_layout.addWidget(self.run_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def get_loops(self) -> int:
        """Get the number of loops for the benchmark.
        
        Returns:
            int: Number of loops to run the benchmark for
        """
        return 50000  # Default value, can be modified to get from UI if needed
        
    def run_benchmark(self):
        """Run the Pystone benchmark."""
        self.run_button.setEnabled(False)
        self.status_label.setText("Running benchmark...")
        self.progress_bar.setValue(0)
        self.results_text.clear()
        
        # Create and start worker thread
        self.worker = PystoneWorker(loops=50000)
        self.thread = QThread()
        
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_benchmark_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.thread.start()
    
    def on_benchmark_finished(self, benchtime, stones):
        """Handle benchmark completion."""
        self.run_button.setEnabled(True)
        self.progress_bar.setValue(100)
        
        if benchtime > 0 and stones > 0:
            self.status_label.setText("Benchmark completed successfully!")
            self.results_text.append(f"Pystone Benchmark Results\n{'='*30}\n")
            self.results_text.append(f"Version: 1.1")
            self.results_text.append(f"Time for 50000 passes: {benchtime:.2f} seconds")
            self.results_text.append(f"This machine benchmarks at {stones:,.2f} pystones/second")
        else:
            self.status_label.setText("Benchmark failed!")
            self.results_text.append("An error occurred during the benchmark.")
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.worker:
            self.worker.stop()
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        event.accept()
