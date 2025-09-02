"""
Test script for the benchmark functionality.
Run this to test the benchmark tests, system info collection, and result export.
"""
import unittest
import sys
import os
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now import local modules
from .benchmark_tests import BenchmarkSuite
from .system_info import get_system_info, save_system_info
from script.test_script.export_results import ResultExporter

def run_benchmark():
    """Run benchmark tests and display results."""
    print("=== Starting Benchmark Suite ===\n")
    
    # Create output directory
    output_dir = "benchmark_results"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Collect system information
    print("Collecting system information...")
    system_info = get_system_info()
    
    # Save system info to file
    sys_info_file = os.path.join(output_dir, f"system_info_{timestamp}.json")
    with open(sys_info_file, 'w', encoding='utf-8') as f:
        json.dump(system_info, f, indent=4, ensure_ascii=False)
    print(f"System information saved to: {sys_info_file}")
    
    # 2. Run benchmark tests
    print("\nRunning benchmark tests...")
    benchmark_suite = BenchmarkSuite()
    results = benchmark_suite.run_all_tests()
    
    # Add system info to results
    for result in results:
        result['system_info'] = system_info
    
    # 3. Export results
    print("\nExporting results...")
    exporter = ResultExporter()
    exported = exporter.export_results(
        results,
        output_dir=output_dir,
        base_filename=f"benchmark_results_{timestamp}",
        formats=['json', 'csv']
    )
    
    print("\n=== Benchmark Complete ===")
    print(f"Results exported to: {output_dir}")
    for fmt, path in exported.items():
        print(f"- {fmt.upper()}: {os.path.basename(path)}")
    
    # Display summary
    print("\nBenchmark Summary:")
    print("-" * 50)
    print(f"{'Test Name':<30} | {'Score':>10} | {'Unit':<10} | {'Iterations'}")
    print("-" * 50)
    for result in results:
        print(f"{result['name']:<30} | {result['score']:>10.2f} | {result['unit']:<10} | {result['iterations']}")
    
    print("\nBenchmark completed successfully!")

if __name__ == "__main__":
    run_benchmark()
