"""
Pystone benchmark test implementation.
"""

import time
from typing import Dict, Any, Optional
from .CLI_pystone import pystones
from .system_info import get_system_info


def run_pystones_test(loops: int = 50000) -> Dict[str, Any]:
    """
    Run the Pystone benchmark test.
    
    Args:
        loops: Number of loops to run the benchmark for
        
    Returns:
        Dict containing benchmark results including:
        - pystones: Pystones per second
        - time_elapsed: Time taken for the benchmark in seconds
        - loops: Number of loops executed
        - system_info: System information at time of test
    """
    start_time = time.time()
    
    try:
        # Run the benchmark
        benchtime, stones = pystones(loops)
        
        # Calculate elapsed time
        elapsed = time.time() - start_time
        
        # Get system info
        system_info = get_system_info()
        
        return {
            'pystones': stones,
            'time_elapsed': elapsed,
            'benchtime': benchtime,
            'loops': loops,
            'system_info': system_info,
            'success': True,
            'error': None
        }
        
    except Exception as e:
        return {
            'pystones': 0,
            'time_elapsed': 0,
            'benchtime': 0,
            'loops': loops,
            'system_info': {},
            'success': False,
            'error': str(e)
        }


def format_pystones_result(result: Dict[str, Any]) -> str:
    """
    Format the Pystones benchmark results as a human-readable string.
    
    Args:
        result: Dictionary containing benchmark results from run_pystones_test()
        
    Returns:
        Formatted string with benchmark results
    """
    if not result['success']:
        return f"Benchmark failed: {result['error']}"
        
    return (
        f"Pystone Benchmark Results\n"
        f"{'='*30}\n"
        f"Version: 1.1\n"
        f"Loops: {result['loops']:,}\n"
        f"Time for {result['loops']:,} passes: {result['benchtime']:.2f} seconds\n"
        f"This machine benchmarks at {result['pystones']:,.2f} pystones/second\n"
        f"Total time elapsed: {result['time_elapsed']:.2f} seconds"
    )


if __name__ == "__main__":
    # Run the benchmark if executed directly
    print("Running Pystone benchmark...")
    result = run_pystones_test()
    print(format_pystones_result(result))
