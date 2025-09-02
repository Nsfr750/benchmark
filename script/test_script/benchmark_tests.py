"""
Benchmark tests module for the Benchmark application.
Contains various performance tests to measure system capabilities.
"""
import time
import math
import random
import statistics
import json
import signal
from typing import Dict, List, Tuple, Callable, Any, Optional
from dataclasses import dataclass, asdict
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QProgressBar, QGroupBox, QTreeWidget, QTreeWidgetItem, 
    QHeaderView, QMessageBox, QTabWidget, QWidget, QTextEdit
)
from PySide6.QtCore import Qt, QThread, Signal as QSignal
from script.lang_mgr import get_language_manager, get_text

class TimeoutError(Exception):
    pass

def timeout(seconds=30, error_message='Function call timed out'):
    """Timeout decorator to prevent tests from running indefinitely."""
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)
            
        def wrapper(*args, **kwargs):
            # Set the signal handler and a 30-second alarm
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)  # Disable the alarm
            return result
            
        return wrapper
    return decorator

@dataclass
class BenchmarkResult:
    """Class to store benchmark test results."""
    name: str
    score: float
    unit: str
    iterations: int
    times: List[float]
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result['min'] = min(self.times) if self.times else 0
        result['max'] = max(self.times) if self.times else 0
        result['mean'] = statistics.mean(self.times) if self.times else 0
        result['median'] = statistics.median(self.times) if self.times else 0
        result['stdev'] = statistics.stdev(self.times) if len(self.times) > 1 else 0
        return result

class BenchmarkSuite:
    """Benchmark suite for running performance tests."""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self._test_data = {
            'small_list': list(range(1000)),
            'medium_list': list(range(10000)),
            'large_list': list(range(100000)),
            'small_matrix': [[random.random() for _ in range(100)] for _ in range(100)],
            'medium_matrix': [[random.random() for _ in range(100)] for _ in range(1000)],
            'large_matrix': [[random.random() for _ in range(1000)] for _ in range(1000)],
        }
    
    def run_test(self, func: Callable, name: str, iterations: int = 5, **kwargs) -> BenchmarkResult:
        """Run a benchmark test and store the results."""
        times = []
        # Remove metadata from kwargs if the function doesn't accept it
        if 'metadata' in kwargs and 'metadata' not in func.__code__.co_varnames:
            metadata = kwargs.pop('metadata')
        else:
            metadata = kwargs.get('metadata', {})
            
        for _ in range(iterations):
            start_time = time.perf_counter()
            # Only pass kwargs that the function accepts
            accepted_kwargs = {k: v for k, v in kwargs.items() if k in func.__code__.co_varnames}
            result = func(**accepted_kwargs)
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        # Calculate score (operations per second)
        avg_time = statistics.mean(times) if times else 0
        score = 1 / avg_time if avg_time > 0 else float('inf')
        
        benchmark_result = BenchmarkResult(
            name=name,
            score=score,
            unit='ops/s',
            iterations=iterations,
            times=times,
            metadata=kwargs.get('metadata', {})
        )
        
        self.results.append(benchmark_result)
        return benchmark_result
    
    # CPU Tests
    def test_cpu_math(self, iterations: int = 5) -> BenchmarkResult:
        """Test CPU performance with mathematical operations."""
        def math_operations(n=1000000):
            result = 0
            for i in range(n):
                x = 3.14159 * 2.71828
                x = math.sqrt(x)
                x = math.sin(x) + math.cos(x)
                x = math.exp(math.log(x + 1))
                result += x  # Ensure the operation isn't optimized away
            return result
            
        return self.run_test(
            math_operations,
            name="CPU Math Operations",
            iterations=iterations,
            metadata={"test_type": "cpu", "operations": "arithmetic, sqrt, trig, exp, log"}
        )
    
    def test_cpu_integer_math(self, iterations: int = 5) -> BenchmarkResult:
        """Test CPU performance with integer arithmetic."""
        def int_math_operations(n=2000000):
            result = 0
            for i in range(1, n + 1):
                result = (result + i) * i % 1000000007
                result ^= (result << 13) & 0xFFFFFFFF
                result ^= (result >> 17) & 0xFFFFFFFF
                result ^= (result << 5) & 0xFFFFFFFF
            return result
            
        return self.run_test(
            int_math_operations,
            name="CPU Integer Math",
            iterations=iterations,
            metadata={"test_type": "cpu", "operations": "integer arithmetic, bitwise"}
        )
    
    @timeout(seconds=30)  # 30 second timeout for the sorting test
    def sort_operations(self, array_size=1000, num_iterations=5):
        """Perform sorting operations to test CPU performance."""
        try:
            data = [random.random() for _ in range(array_size)]
            
            start_time = time.time()
            for _ in range(num_iterations):
                data2 = data.copy()
                # Simple bubble sort (inefficient on purpose)
                for i in range(len(data2)):
                    for j in range(0, len(data2)-i-1):
                        if data2[j] > data2[j+1]:
                            data2[j], data2[j+1] = data2[j+1], data2[j]
            
            end_time = time.time()
            return end_time - start_time
        except TimeoutError:
            print("\nSorting test timed out after 30 seconds. Using a smaller dataset...")
            # Fallback to a smaller dataset if the test times out
            return self.sort_operations(array_size=500, num_iterations=2)
    
    def test_cpu_sorting(self, iterations: int = 3) -> BenchmarkResult:
        """Test sorting performance with different algorithms."""
        def sort_operations():
            # Use a smaller dataset for the test
            test_size = 1000
            test_data = [random.random() for _ in range(test_size)]
            
            # Test built-in sort
            start_time = time.time()
            sorted1 = sorted(test_data)
            builtin_sort_time = time.time() - start_time
            
            # Test bubble sort (from sort_operations method)
            bubble_sort_time = self.sort_operations(array_size=test_size, num_iterations=1)
            
            # Return the total time
            return builtin_sort_time + bubble_sort_time
            
        return self.run_test(
            sort_operations,
            name="CPU Sorting Algorithms",
            iterations=iterations,
            metadata={
                "test_type": "cpu", 
                "data_size": test_size,
                "algorithms": ["Timsort", "Bubble Sort", "Quicksort"]
            }
        )
        
    def test_cpu_compression(self, iterations: int = 3) -> BenchmarkResult:
        """Test CPU performance with compression algorithms."""
        import zlib
        import bz2
        
        data = b'x' * (10 * 1024 * 1024)  # 10MB of data
        
        def compression_operations():
            # Test different compression levels
            zlib_compressed = zlib.compress(data, level=9)
            bz2_compressed = bz2.compress(data, compresslevel=9)
            
            # Decompress to ensure data integrity
            zlib_decompressed = zlib.decompress(zlib_compressed)
            bz2_decompressed = bz2.decompress(bz2_compressed)
            
            return len(zlib_compressed) + len(bz2_compressed)
            
        return self.run_test(
            compression_operations,
            name="CPU Compression",
            iterations=iterations,
            metadata={
                "test_type": "cpu", 
                "data_size": len(data),
                "algorithms": ["zlib", "bz2"]
            }
        )
    
    # Memory Tests
    def test_memory_allocation(self, iterations: int = 5) -> BenchmarkResult:
        """Test memory allocation and access patterns."""
        size = 1000000
        
        def memory_operations():
            # Test different allocation patterns
            
            # Sequential access
            seq_data = [i * 2 for i in range(size)]
            seq_sum = sum(x % 17 for x in seq_data)
            
            # Random access
            random_indices = random.sample(range(size), min(100000, size))
            random_sum = sum(seq_data[i] for i in random_indices)
            
            # Memory copy
            copy_data = seq_data.copy()
            copy_sum = sum(x for x in copy_data[::100])
            
            # Memory-intensive operations
            matrix = [[(i * j) % 100 for j in range(100)] for i in range(1000)]
            matrix_sum = sum(sum(row) for row in matrix)
            
            return seq_sum + random_sum + copy_sum + matrix_sum
            
        return self.run_test(
            memory_operations,
            name="Memory Access Patterns",
            iterations=iterations,
            metadata={
                "test_type": "memory", 
                "data_size": size,
                "patterns": ["sequential", "random", "copy", "matrix"]
            }
        )
        
    def test_memory_bandwidth(self, iterations: int = 3) -> BenchmarkResult:
        """Test memory bandwidth with different access patterns."""
        size = 10 * 1024 * 1024  # 10MB
        block_size = 1024  # 1KB blocks
        
        def memory_bandwidth_operations():
            # Create a large array
            data = bytearray(size)
            total = 0
            
            # Sequential write
            for i in range(0, size, block_size):
                data[i:i+block_size] = bytes([i % 256] * block_size)
            
            # Random read
            for _ in range(size // block_size):
                idx = random.randint(0, size - block_size)
                total += sum(data[idx:idx+block_size])
            
            # Sequential read
            total += sum(byte for byte in data[::block_size])
            
            return total
            
        return self.run_test(
            memory_bandwidth_operations,
            name="Memory Bandwidth",
            iterations=iterations,
            metadata={
                "test_type": "memory",
                "data_size": size,
                "block_size": block_size,
                "operations": ["sequential_write", "random_read", "sequential_read"]
            }
        )
        
    def test_cache_effects(self, iterations: int = 3) -> BenchmarkResult:
        """Test CPU cache effects with different access patterns."""
        # Test different array sizes that will fit in different cache levels
        sizes = [
            (1024, "L1"),      # ~1KB - L1 cache
            (32768, "L2"),     # ~32KB - L2 cache
            (1048576, "L3"),   # ~1MB - L3 cache
            (16777216, "RAM")  # ~16MB - Main memory
        ]
        
        def cache_test_operations():
            total = 0
            for size, level in sizes:
                # Create array and access it sequentially (cache-friendly)
                arr = [i % 256 for i in range(size)]
                seq_sum = sum(arr)
                
                # Access with a large stride (cache-unfriendly)
                stride = max(1, size // 16)
                stride_sum = sum(arr[i] for i in range(0, size, stride))
                
                total += seq_sum + stride_sum
                
            return total
            
        return self.run_test(
            cache_test_operations,
            name="CPU Cache Effects",
            iterations=iterations,
            metadata={
                "test_type": "cpu_memory",
                "cache_levels": [size[1] for size in sizes],
                "access_patterns": ["sequential", "strided"]
            }
        )
    
    # Disk I/O Tests
    def test_disk_io(self, test_file: str = "benchmark_temp_file.bin", iterations: int = 3) -> BenchmarkResult:
        """Test disk I/O performance with different access patterns."""
        import os
        import tempfile
        import shutil
        
        # Create a temporary directory for our tests
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Test different file sizes and access patterns
            test_cases = [
                (1 * 1024 * 1024, "1MB"),       # 1MB file
                (10 * 1024 * 1024, "10MB"),     # 10MB file
                (100 * 1024 * 1024, "100MB"),   # 100MB file
            ]
            
            results = []
            
            for file_size, size_label in test_cases:
                test_file = os.path.join(temp_dir, f"benchmark_{size_label}.bin")
                data = os.urandom(file_size)
                
                # Sequential write test
                def sequential_write():
                    with open(test_file, 'wb') as f:
                        f.write(data)
                
                # Random write test
                def random_write():
                    with open(test_file, 'wb+') as f:
                        # Write in random order
                        block_size = 4096  # Typical filesystem block size
                        blocks = [(i, data[i*block_size:(i+1)*block_size]) 
                                for i in range((len(data) + block_size - 1) // block_size)]
                        random.shuffle(blocks)
                        
                        for i, block in blocks:
                            f.seek(i * block_size)
                            f.write(block)
                
                # Sequential read test
                def sequential_read():
                    with open(test_file, 'rb') as f:
                        return len(f.read())
                
                # Random read test
                def random_read():
                    with open(test_file, 'rb') as f:
                        file_size = os.path.getsize(test_file)
                        block_size = 4096
                        total = 0
                        for _ in range(file_size // block_size):
                            pos = random.randint(0, (file_size - block_size) // block_size) * block_size
                            f.seek(pos)
                            total += len(f.read(block_size))
                        return total
                
                # Run tests for this file size
                for test_name, test_func in [
                    (f"Sequential Write ({size_label})", sequential_write),
                    (f"Random Write ({size_label})", random_write),
                    (f"Sequential Read ({size_label})", sequential_read),
                    (f"Random Read ({size_label})", random_read)
                ]:
                    result = self.run_test(
                        test_func,
                        name=test_name,
                        iterations=iterations,
                        metadata={
                            "test_type": "disk",
                            "operation": test_name.split()[0].lower(),
                            "file_size": file_size,
                            "size_label": size_label
                        }
                    )
                    results.append(result)
                
                # Clean up test file
                try:
                    os.remove(test_file)
                except:
                    pass
            
            # Calculate overall disk score
            total_time = sum(statistics.mean(r.times) for r in results if r.times)
            total_data = sum(r.metadata.get('file_size', 0) for r in results if 'file_size' in r.metadata)
            
            if total_time > 0 and total_data > 0:
                overall_speed = (total_data / (1024 * 1024)) / total_time  # MB/s
            else:
                overall_speed = 0
            
            # Create a combined result
            combined_metadata = {
                "test_type": "disk",
                "operations": [r.name for r in results],
                "total_data_processed_mb": total_data / (1024 * 1024),
                "average_speed_mb_s": overall_speed
            }
            
            # Add individual speeds to metadata
            for r in results:
                if r.times and 'file_size' in r.metadata:
                    file_size_mb = r.metadata['file_size'] / (1024 * 1024)
                    avg_time = statistics.mean(r.times)
                    if avg_time > 0:
                        combined_metadata[f"{r.name.lower().replace(' ', '_')}_speed"] = \
                            f"{file_size_mb / avg_time:.2f} MB/s"
            
            combined_result = BenchmarkResult(
                name="Disk I/O Performance",
                score=overall_speed,
                unit="MB/s",
                iterations=iterations,
                times=[t for r in results for t in r.times],
                metadata=combined_metadata
            )
            
            self.results.append(combined_result)
            return combined_result
            
        finally:
            # Clean up temporary directory
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
    
    # Run all available tests
    def run_all_tests(self, test_categories: list = None) -> List[Dict[str, Any]]:
        """
        Run all available benchmark tests or specific categories.
        
        Args:
            test_categories: List of categories to test. If None, run all tests.
                            Possible values: 'cpu', 'memory', 'disk'
        """
        self.results = []  # Reset previous results
        
        # If no specific categories provided, run all tests
        if test_categories is None:
            test_categories = ['cpu', 'memory', 'disk']
        
        # Run CPU tests
        if 'cpu' in test_categories:
            self.test_cpu_math()
            self.test_cpu_integer_math()
            self.test_cpu_sorting()
            self.test_cpu_compression()
        
        # Run memory tests
        if 'memory' in test_categories:
            self.test_memory_allocation()
            self.test_memory_bandwidth()
            self.test_cache_effects()
        
        # Run disk I/O tests
        if 'disk' in test_categories:
            self.test_disk_io()
        
        # Convert results to dictionaries for serialization
        return [r.to_dict() for r in self.results]
    
    def get_test_categories(self) -> Dict[str, list]:
        """Get available test categories and their tests."""
        return {
            'cpu': [
                'test_cpu_math',
                'test_cpu_integer_math',
                'test_cpu_sorting',
                'test_cpu_compression'
            ],
            'memory': [
                'test_memory_allocation',
                'test_memory_bandwidth',
                'test_cache_effects'
            ],
            'disk': [
                'test_disk_io'
            ]
        }
    
    def export_results(self, file_path: str, format: str = 'json') -> bool:
        """Export benchmark results to a file.
        
        Args:
            file_path: Path to save the results
            format: Output format ('json' or 'csv')
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            results = [result.to_dict() for result in self.results]
            
            if format.lower() == 'json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        'benchmark_results': results,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }, f, indent=4, ensure_ascii=False)
            else:  # CSV format
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    if results:
                        # Get all possible fieldnames from all results
                        fieldnames = set()
                        for result in results:
                            fieldnames.update(result.keys())
                            if 'metadata' in result and isinstance(result['metadata'], dict):
                                for key in result['metadata']:
                                    fieldnames.add(f'metadata_{key}')
                        
                        # Define field order
                        ordered_fields = ['name', 'score', 'unit', 'iterations', 'min', 'max', 'mean', 'median', 'stdev']
                        remaining_fields = sorted(f for f in fieldnames if f not in ordered_fields and not f.startswith('metadata_'))
                        metadata_fields = sorted(f for f in fieldnames if f.startswith('metadata_'))
                        fieldnames = ordered_fields + remaining_fields + metadata_fields
                        
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        
                        for result in results:
                            row = result.copy()
                            metadata = row.pop('metadata', {})
                            
                            # Add metadata fields
                            if isinstance(metadata, dict):
                                for key, value in metadata.items():
                                    row[f'metadata_{key}'] = value
                            
                            writer.writerow(row)
            
            return True
            
        except Exception as e:
            print(f"Error exporting results: {e}")
            return False


class BenchmarkWorker(QThread):
    """Worker thread for running benchmark tests."""
    progress_updated = QSignal(int, str)  # progress percentage, status message
    test_completed = QSignal(dict)  # test results
    finished_all = QSignal()  # emitted when all tests are done
    
    def __init__(self, test_categories=None, parent=None):
        super().__init__(parent)
        self.test_categories = test_categories
        self.suite = BenchmarkSuite()
        self.is_running = True
    
    def run(self):
        """Run the benchmark tests in a separate thread."""
        try:
            self.progress_updated.emit(0, get_text("benchmark_tests.starting_tests", "Starting benchmark tests..."))
            
            # Get the list of tests to run
            if not self.test_categories:
                test_categories = [cat["id"] for cat in self.suite.get_test_categories()]
            else:
                test_categories = self.test_categories
            
            total_tests = len(test_categories)
            
            for i, category in enumerate(test_categories):
                if not self.is_running:
                    break
                    
                self.progress_updated.emit(
                    int((i / total_tests) * 100), 
                    get_text("benchmark_tests.running_test", f"Running {category} tests...")
                )
                
                # Run the test category
                self.suite.run_all_tests([category])
                
                # Emit results for this test category
                for result in self.suite.results:
                    if result.name.startswith(category):
                        self.test_completed.emit({
                            'name': result.name,
                            'score': result.score,
                            'unit': result.unit,
                            'iterations': result.iterations,
                            'metadata': result.metadata or {}
                        })
            
            self.progress_updated.emit(100, get_text("benchmark_tests.completed", "Benchmark tests completed"))
            self.finished_all.emit()
            
        except Exception as e:
            self.progress_updated.emit(0, f"Error: {str(e)}")
    
    def stop(self):
        """Stop the benchmark tests."""
        self.is_running = False


class BenchmarkTestDialog(QDialog):
    """Dialog for running and viewing benchmark tests."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = get_language_manager()
        self.worker = None
        self.setup_ui()
        self.retranslate_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle(get_text("benchmark_tests.title", "Benchmark Tests"))
        self.setMinimumSize(800, 600)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Test selection
        self.test_group = QGroupBox()
        test_layout = QVBoxLayout()
        
        # Test categories tree
        self.categories_tree = QTreeWidget()
        self.categories_tree.setHeaderLabels([get_text("benchmark_tests.test_category", "Test Category"), 
                                           get_text("benchmark_tests.status", "Status")])
        self.categories_tree.setSelectionMode(QTreeWidget.MultiSelection)
        
        # Add test categories
        suite = BenchmarkSuite()
        categories = suite.get_test_categories()
        
        # Map category IDs to display names
        category_names = {
            'cpu': get_text('benchmark_tests.cpu', 'CPU Tests'),
            'memory': get_text('benchmark_tests.memory', 'Memory Tests'),
            'disk': get_text('benchmark_tests.disk', 'Disk Tests')
        }
        
        for category_id, tests in categories.items():
            item = QTreeWidgetItem([category_names.get(category_id, category_id), ""])
            item.setData(0, Qt.UserRole, category_id)
            item.setCheckState(0, Qt.Checked)
            self.categories_tree.addTopLevelItem(item)
            
            # Add individual tests as child items
            for test in tests:
                test_item = QTreeWidgetItem([get_text(f'benchmark_tests.{test}', test), ""])
                test_item.setData(0, Qt.UserRole, test)
                test_item.setCheckState(0, Qt.Checked)
                item.addChild(test_item)
        
        self.categories_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        
        # Results area
        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.status_label = QLabel()
        
        # Buttons
        button_layout = QHBoxLayout()
        self.run_button = QPushButton()
        self.run_button.clicked.connect(self.run_tests)
        
        self.stop_button = QPushButton(get_text("common.stop", "Stop"))
        self.stop_button.clicked.connect(self.stop_tests)
        self.stop_button.setEnabled(False)
        
        self.close_button = QPushButton(get_text("common.close", "Close"))
        self.close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        # Assemble the UI
        test_layout.addWidget(self.categories_tree)
        self.test_group.setLayout(test_layout)
        
        layout.addWidget(self.test_group)
        layout.addWidget(QLabel(get_text("benchmark_tests.results", "Results:")))
        layout.addWidget(self.results_area)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addLayout(button_layout)
    
    def retranslate_ui(self):
        """Update UI text based on current language."""
        self.setWindowTitle(get_text("benchmark_tests.title", "Benchmark Tests"))
        self.test_group.setTitle(get_text("benchmark_tests.test_categories", "Test Categories"))
        self.run_button.setText(get_text("benchmark_tests.run_tests", "Run Selected Tests"))
    
    def run_tests(self):
        """Start running the selected benchmark tests."""
        # Get selected test categories
        selected_categories = []
        for i in range(self.categories_tree.topLevelItemCount()):
            item = self.categories_tree.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                selected_categories.append(item.data(0, Qt.UserRole))
        
        if not selected_categories:
            QMessageBox.warning(
                self,
                get_text("common.warning", "Warning"),
                get_text("benchmark_tests.no_tests_selected", "Please select at least one test category to run.")
            )
            return
        
        # Clear previous results
        self.results_area.clear()
        self.progress_bar.setValue(0)
        self.status_label.setText(get_text("benchmark_tests.starting_tests", "Starting benchmark tests..."))
        
        # Disable UI elements during test
        self.run_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.categories_tree.setEnabled(False)
        
        # Create and start worker thread
        self.worker = BenchmarkWorker(selected_categories)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.test_completed.connect(self.add_test_result)
        self.worker.finished_all.connect(self.tests_finished)
        self.worker.start()
    
    def stop_tests(self):
        """Stop the currently running benchmark tests."""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
            self.status_label.setText(get_text("benchmark_tests.stopped", "Tests stopped by user."))
            self.tests_finished()
    
    def update_progress(self, progress, status):
        """Update the progress bar and status label."""
        self.progress_bar.setValue(progress)
        self.status_label.setText(status)
    
    def add_test_result(self, result):
        """Add a test result to the results area."""
        text = f"{result['name']}: {result['score']:.2f} {result['unit']} " \
               f"({result['iterations']} {get_text('benchmark_tests.iterations', 'iterations')})\n"
        self.results_area.moveCursor(self.results_area.textCursor().End)
        self.results_area.insertPlainText(text)
        self.results_area.ensureCursorVisible()
    
    def tests_finished(self):
        """Clean up after tests are finished."""
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.categories_tree.setEnabled(True)
        
        if self.worker and self.worker.isRunning():
            self.worker.wait()
        
        self.worker = None
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        event.accept()
