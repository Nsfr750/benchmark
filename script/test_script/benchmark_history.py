"""
Benchmark history management for the Benchmark application.
"""
import os
import json
import logging
import statistics
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict, field

log = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Class to represent a single test result."""
    name: str
    score: float
    unit: str
    times: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def min_time(self) -> float:
        """Get minimum time across all runs."""
        return min(self.times) if self.times else 0.0
        
    @property
    def max_time(self) -> float:
        """Get maximum time across all runs."""
        return max(self.times) if self.times else 0.0
        
    @property
    def avg_time(self) -> float:
        """Get average time across all runs."""
        return statistics.mean(self.times) if self.times else 0.0
        
    @property
    def median_time(self) -> float:
        """Get median time across all runs."""
        return statistics.median(self.times) if self.times else 0.0
        
    @property
    def stdev(self) -> float:
        """Get standard deviation of times."""
        return statistics.stdev(self.times) if len(self.times) > 1 else 0.0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'score': self.score,
            'unit': self.unit,
            'times': self.times,
            'metadata': self.metadata,
            'stats': {
                'min': self.min_time,
                'max': self.max_time,
                'mean': self.avg_time,
                'median': self.median_time,
                'stdev': self.stdev
            }
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestResult':
        """Create from dictionary."""
        return cls(
            name=data['name'],
            score=data['score'],
            unit=data['unit'],
            times=data['times'],
            metadata=data.get('metadata', {})
        )

class BenchmarkResult:
    """Class to represent a complete benchmark result set."""
    
    def __init__(self, 
                 timestamp: float = None,
                 system_info: Optional[Dict[str, Any]] = None,
                 results: Optional[List[TestResult]] = None):
        """
        Initialize a benchmark result set.
        
        Args:
            timestamp: Unix timestamp when the benchmark was run
            system_info: System information at the time of benchmark
            results: List of test results
        """
        self.timestamp = timestamp or datetime.now().timestamp()
        self.system_info = system_info or {}
        self.results: List[TestResult] = results or []
        
    def add_result(self, result: TestResult) -> None:
        """Add a test result to this benchmark run."""
        self.results.append(result)
        
    def get_result(self, name: str) -> Optional[TestResult]:
        """Get a test result by name."""
        for result in self.results:
            if result.name == name:
                return result
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the benchmark result to a dictionary."""
        return {
            'timestamp': self.timestamp,
            'system_info': self.system_info,
            'results': [r.to_dict() for r in self.results]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BenchmarkResult':
        """Create a BenchmarkResult from a dictionary."""
        return cls(
            timestamp=data.get('timestamp', datetime.now().timestamp()),
            system_info=data.get('system_info', {}),
            results=[TestResult.from_dict(r) for r in data.get('results', [])]
        )
    
    @property
    def formatted_date(self) -> str:
        """Return a formatted date string for display."""
        return datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the benchmark results."""
        summary = {
            'timestamp': self.timestamp,
            'formatted_date': self.formatted_date,
            'system_info': self.system_info,
            'test_count': len(self.results),
            'tests': {}
        }
        
        # Add individual test summaries
        for test in self.results:
            summary['tests'][test.name] = {
                'score': test.score,
                'unit': test.unit,
                'min': test.min_time,
                'max': test.max_time,
                'mean': test.avg_time,
                'median': test.median_time,
                'stdev': test.stdev
            }
            
        return summary
    
    def __str__(self) -> str:
        """Return a string representation of the benchmark result."""
        return f"BenchmarkResult(timestamp={self.formatted_date}, tests={len(self.results)})"


class BenchmarkHistory:
    """Class to manage benchmark history storage and retrieval."""
    
    def __init__(self, history_file: Optional[str] = None):
        """
        Initialize the benchmark history.
        
        Args:
            history_file: Path to the history file. If None, a default path will be used.
        """
        if history_file is None:
            # Default to user's app data directory
            app_data_dir = os.path.join(os.path.expanduser('~'), '.benchmark')
            os.makedirs(app_data_dir, exist_ok=True)
            history_file = os.path.join(app_data_dir, 'benchmark_history.json')
        
        self.history_file = history_file
        self._results: List[BenchmarkResult] = []
        self._load_history()
    
    def add_result(self, result: BenchmarkResult) -> None:
        """Add a new benchmark result to the history."""
        self._results.append(result)
        self._save_history()
    
    def get_recent_results(self, limit: int = 10) -> List[BenchmarkResult]:
        """Get the most recent benchmark results."""
        return sorted(self._results, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_results_by_test(self, test_name: str, limit: int = 100) -> List[Tuple[float, float]]:
        """
        Get historical results for a specific test.
        
        Args:
            test_name: Name of the test to get results for
            limit: Maximum number of results to return
            
        Returns:
            List of (timestamp, score) tuples
        """
        results = []
        for result in sorted(self._results, key=lambda x: x.timestamp, reverse=True):
            test_result = result.get_result(test_name)
            if test_result:
                results.append((result.timestamp, test_result.score))
                if len(results) >= limit:
                    break
        return results
    
    def get_test_names(self) -> List[str]:
        """Get a list of all unique test names in the history."""
        names = set()
        for result in self._results:
            for test in result.results:
                names.add(test.name)
        return sorted(names)
    
    def get_test_categories(self) -> Dict[str, List[str]]:
        """Get a dictionary of test categories and their tests."""
        categories = {}
        for result in self._results:
            for test in result.results:
                test_type = test.metadata.get('test_type', 'other')
                if test_type not in categories:
                    categories[test_type] = set()
                categories[test_type].add(test.name)
        
        # Convert sets to sorted lists
        return {k: sorted(list(v)) for k, v in categories.items()}
    
    def compare_results(self, result1: BenchmarkResult, result2: BenchmarkResult) -> Dict[str, Dict[str, Any]]:
        """
        Compare two benchmark results.
        
        Returns:
            Dictionary with comparison data for each test
        """
        comparison = {}
        
        # Get all test names from both results
        all_tests = set()
        for test in result1.results:
            all_tests.add(test.name)
        for test in result2.results:
            all_tests.add(test.name)
        
        # Compare each test
        for test_name in sorted(all_tests):
            test1 = result1.get_result(test_name)
            test2 = result2.get_result(test_name)
            
            if test1 and test2:
                # Both results exist, calculate difference
                score_diff = test2.score - test1.score
                score_pct = (score_diff / test1.score * 100) if test1.score != 0 else float('inf')
                
                comparison[test_name] = {
                    'test1_score': test1.score,
                    'test2_score': test2.score,
                    'score_diff': score_diff,
                    'score_pct': score_pct,
                    'unit': test1.unit,
                    'improvement': score_diff > 0,
                    'metadata': test1.metadata
                }
            elif test1:
                # Only in first result
                comparison[test_name] = {
                    'test1_score': test1.score,
                    'test2_score': None,
                    'score_diff': None,
                    'score_pct': None,
                    'unit': test1.unit,
                    'improvement': None,
                    'metadata': test1.metadata
                }
            else:
                # Only in second result
                comparison[test_name] = {
                    'test1_score': None,
                    'test2_score': test2.score,
                    'score_diff': None,
                    'score_pct': None,
                    'unit': test2.unit,
                    'improvement': None,
                    'metadata': test2.metadata
                }
        
        return comparison
    
    def clear_history(self) -> None:
        """Clear all benchmark history."""
        self._results = []
        self._save_history()
    
    def _load_history(self) -> None:
        """Load benchmark history from file."""
        if not os.path.exists(self.history_file):
            log.info(f"No history file found at {self.history_file}")
            return
            
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    # New format: list of benchmark results
                    self._results = [BenchmarkResult.from_dict(item) for item in data]
                elif 'results' in data:
                    # Single benchmark result in new format
                    self._results = [BenchmarkResult.from_dict(data)]
                else:
                    # Old format (pystone only)
                    self._results = [self._convert_old_format(data)]
            
            log.info(f"Loaded {len(self._results)} benchmark results from {self.history_file}")
        except Exception as e:
            log.error(f"Error loading benchmark history: {e}")
            self._results = []
    
    def _convert_old_format(self, data: Dict[str, Any]) -> BenchmarkResult:
        """Convert old format benchmark result to new format."""
        result = BenchmarkResult(
            timestamp=data.get('timestamp', 0),
            system_info=data.get('system_info', {})
        )
        
        # Add pystone result if available
        if 'pystones' in data:
            result.add_result(TestResult(
                name='Pystone',
                score=data['pystones'],
                unit='pystones/s',
                times=[data.get('time_elapsed', 0)],
                metadata={
                    'test_type': 'cpu',
                    'iterations': data.get('iterations', 0),
                    'legacy': True
                }
            ))
            
        return result
    
    def _save_history(self) -> None:
        """Save benchmark history to file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(self.history_file)), exist_ok=True)
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(
                    [r.to_dict() for r in self._results],
                    f,
                    indent=2,
                    ensure_ascii=False
                )
            log.info(f"Saved {len(self._results)} benchmark results to {self.history_file}")
        except Exception as e:
            log.error(f"Error saving benchmark history: {e}")
            
    def export_to_csv(self, file_path: str) -> bool:
        """Export benchmark history to a CSV file."""
        try:
            import csv
            
            # Get all unique test names
            test_names = self.get_test_names()
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                header = ['timestamp', 'date']
                for test_name in test_names:
                    header.extend([
                        f"{test_name} (score)",
                        f"{test_name} (unit)",
                        f"{test_name} (min)",
                        f"{test_name} (max)",
                        f"{test_name} (mean)",
                        f"{test_name} (median)",
                        f"{test_name} (stdev)"
                    ])
                writer.writerow(header)
                
                # Write data rows
                for result in sorted(self._results, key=lambda x: x.timestamp):
                    row = [
                        result.timestamp,
                        result.formatted_date
                    ]
                    
                    # Add data for each test
                    for test_name in test_names:
                        test = result.get_result(test_name)
                        if test:
                            row.extend([
                                test.score,
                                test.unit,
                                test.min_time,
                                test.max_time,
                                test.avg_time,
                                test.median_time,
                                test.stdev
                            ])
                        else:
                            # Add empty values for missing tests
                            row.extend([''] * 7)
                    
                    writer.writerow(row)
            
            log.info(f"Exported {len(self._results)} benchmark results to {file_path}")
            return True
            
        except Exception as e:
            log.error(f"Error exporting benchmark history to CSV: {e}")
            return False
    
    def __len__(self) -> int:
        """Return the number of benchmark results in the history."""
        return len(self._results)
    
    def __getitem__(self, index: int) -> BenchmarkResult:
        """Get a benchmark result by index."""
        return self._results[index]


# Global instance of BenchmarkHistory
_benchmark_history = None

def get_benchmark_history() -> BenchmarkHistory:
    """Get or create the global benchmark history instance."""
    global _benchmark_history
    if _benchmark_history is None:
        _benchmark_history = BenchmarkHistory()
    return _benchmark_history
