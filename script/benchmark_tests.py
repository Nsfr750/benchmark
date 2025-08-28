"""
Benchmark tests module for the Benchmark application.
Contains various performance tests to measure system capabilities.
"""
import time
import math
import random
import statistics
import json
from typing import Dict, List, Tuple, Callable, Any
from dataclasses import dataclass, asdict

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
            for _ in range(n):
                x = 3.14159 * 2.71828
                x = math.sqrt(x)
                x = math.sin(x) + math.cos(x)
                x = math.exp(math.log(x + 1))
            return x
            
        return self.run_test(
            math_operations,
            name="CPU Math Operations",
            iterations=iterations,
            metadata={"test_type": "cpu", "operations": "arithmetic, sqrt, trig, exp, log"}
        )
    
    def test_cpu_sorting(self, iterations: int = 3) -> BenchmarkResult:
        """Test sorting performance."""
        data = self._test_data['large_list'].copy()
        
        def sort_operations():
            return sorted(data * 10)
            
        return self.run_test(
            sort_operations,
            name="CPU Sorting",
            iterations=iterations,
            metadata={"test_type": "cpu", "data_size": len(data) * 10}
        )
    
    # Memory Tests
    def test_memory_allocation(self, iterations: int = 5) -> BenchmarkResult:
        """Test memory allocation and access speed."""
        size = 1000000
        
        def memory_operations():
            # Allocate and process a large list
            data = [i * 2 for i in range(size)]
            # Process the data
            return sum(x % 17 for x in data)
            
        return self.run_test(
            memory_operations,
            name="Memory Allocation & Access",
            iterations=iterations,
            metadata={"test_type": "memory", "data_size": size}
        )
    
    # Disk I/O Tests
    def test_disk_io(self, test_file: str = "benchmark_temp_file.bin", iterations: int = 3) -> BenchmarkResult:
        """Test disk I/O performance."""
        import os
        import tempfile
        
        # Use a temporary file that will be automatically cleaned up
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            test_file = tmp_file.name
        
        data_size = 10 * 1024 * 1024  # 10MB
        data = os.urandom(data_size)
        
        def write_test():
            with open(test_file, 'wb') as f:
                f.write(data)
            
        def read_test():
            with open(test_file, 'rb') as f:
                return len(f.read())
        
        # Run write test
        write_result = self.run_test(
            write_test,
            name="Disk Write Speed",
            iterations=iterations,
            metadata={"test_type": "disk", "operation": "write", "data_size": data_size}
        )
        
        # Run read test
        read_result = self.run_test(
            read_test,
            name="Disk Read Speed",
            iterations=iterations,
            metadata={"test_type": "disk", "operation": "read", "data_size": data_size}
        )
        
        # Clean up
        try:
            os.remove(test_file)
        except:
            pass
        
        # Calculate combined score (MB/s)
        total_time = statistics.mean(write_result.times) + statistics.mean(read_result.times)
        combined_score = (2 * data_size / (1024 * 1024)) / total_time if total_time > 0 else 0
        
        combined_result = BenchmarkResult(
            name="Disk I/O Speed",
            score=combined_score,
            unit="MB/s",
            iterations=iterations,
            times=write_result.times + read_result.times,
            metadata={
                "test_type": "disk",
                "data_size": data_size,
                "write_speed": f"{data_size / (1024 * 1024 * statistics.mean(write_result.times)):.2f} MB/s" if write_result.times else "N/A",
                "read_speed": f"{data_size / (1024 * 1024 * statistics.mean(read_result.times)):.2f} MB/s" if read_result.times else "N/A"
            }
        )
        
        self.results.append(combined_result)
        return combined_result
    
    # Run all available tests
    def run_all_tests(self) -> List[Dict[str, Any]]:
        """Run all available benchmark tests."""
        self.results = []  # Reset previous results
        
        # Run CPU tests
        self.test_cpu_math()
        self.test_cpu_sorting()
        
        # Run memory tests
        self.test_memory_allocation()
        
        # Run disk I/O test (last as it's the slowest)
        self.test_disk_io()
        
        return [result.to_dict() for result in self.results]
    
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
