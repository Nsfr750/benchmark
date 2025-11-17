# Benchmark Application API Documentation

This document provides detailed information about the Benchmark Application's programming interface.

## Table of Contents
- [Core Modules](#core-modules)
- [Benchmark Classes](#benchmark-classes)
- [Result Handling](#result-handling)
- [Configuration](#configuration)
- [Utilities](#utilities)

## Core Modules

### `benchmark.runner`
Main module for executing benchmarks.

```python
from benchmark.runner import BenchmarkRunner

# Initialize benchmark runner
runner = BenchmarkRunner(config_path='config/benchmark_config.json')

# Run all benchmarks
results = runner.run_all()

# Run specific benchmark
cpu_result = runner.run_benchmark('cpu')
```

### `benchmark.metrics`
Handles performance metric collection and analysis.

```python
from benchmark.metrics import PerformanceMetrics

metrics = PerformanceMetrics()
metrics.start()
# ... run some code ...
metrics.stop()

print(f"Elapsed time: {metrics.elapsed_time} seconds")
print(f"CPU usage: {metrics.cpu_usage}%")
print(f"Memory usage: {metrics.memory_usage}MB")
```

## Benchmark Classes

### `CPUBenchmark`
Measures CPU performance.

```python
from benchmark.benchmarks.cpu import CPUBenchmark

cpu_bench = CPUBenchmark()
result = cpu_bench.run(iterations=1000)
```

### `MemoryBenchmark`
Measures memory performance.

```python
from benchmark.benchmarks.memory import MemoryBenchmark

mem_bench = MemoryBenchmark()
result = mem_bench.run(size_mb=1024)
```

## Result Handling

### `BenchmarkResult`
Container for benchmark results.

```python
from benchmark.results import BenchmarkResult

result = BenchmarkResult(
    name="CPU Benchmark",
    metrics={
        'score': 1250.5,
        'iterations': 1000,
        'time_elapsed': 5.23
    },
    metadata={
        'system': 'Windows 10',
        'cpu': 'Intel i7-10700K'
    }
)

# Save results to file
result.save('results/cpu_benchmark.json')

# Compare with another result
comparison = result.compare(other_result)
```

## Configuration

### `BenchmarkConfig`
Handles benchmark configuration.

```python
from benchmark.config import BenchmarkConfig

# Load from file
config = BenchmarkConfig.from_file('config/benchmark_config.json')

# Or create programmatically
config = BenchmarkConfig(
    benchmarks=['cpu', 'memory', 'disk'],
    iterations=1000,
    output_dir='results',
    verbose=True
)

# Save configuration
config.save('config/custom_config.json')
```

## Utilities

### `benchmark.utils.timer`
Precision timing utilities.

```python
from benchmark.utils.timer import Timer

with Timer() as t:
    # Code to time
    pass

print(f"Execution time: {t.elapsed:.4f} seconds")
```

### `benchmark.utils.logger`
Logging utilities.

```python
from benchmark.utils.logger import get_logger

logger = get_logger('benchmark')
logger.info('Starting benchmark...')
logger.warning('Resource usage is high')
logger.error('Benchmark failed')
```

## Error Handling

Custom exceptions for better error management:

```python
from benchmark.exceptions import (
    BenchmarkError,
    ConfigurationError,
    ExecutionError,
    TimeoutError
)

try:
    # Benchmark code
    pass
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except TimeoutError as e:
    print(f"Benchmark timed out: {e}")
except BenchmarkError as e:
    print(f"Benchmark error: {e}")
```
