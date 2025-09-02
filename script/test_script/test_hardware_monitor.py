"""Tests for the hardware monitoring functionality."""

import time

import psutil
import pytest

from script.test_script.hardware_monitor import HardwareMonitor, HardwareMetrics


def test_hardware_metrics_initialization():
    """Test that HardwareMetrics can be initialized with default values."""
    metrics = HardwareMetrics(
        timestamp=time.time(),
        cpu_percent=50.0,
        memory_percent=30.0,
        memory_used=1024.0,
        memory_available=2048.0,
        disk_read_bytes=1000,
        disk_write_bytes=2000,
        net_sent_bytes=3000,
        net_recv_bytes=4000,
        cpu_temp=60.0,
        gpu_usage=30.0,
        gpu_temp=65.0,
        gpu_memory_used=512.0
    )
    
    assert metrics.cpu_percent == 50.0
    assert metrics.memory_used == 1024.0
    assert metrics.gpu_temp == 65.0


def test_hardware_monitor_initialization():
    """Test that HardwareMonitor initializes correctly."""
    monitor = HardwareMonitor(interval=0.5)
    assert monitor.interval == 0.5
    assert not monitor.running
    assert len(monitor.metrics) == 0


def test_hardware_monitor_start_stop():
    """Test starting and stopping the hardware monitor."""
    monitor = HardwareMonitor(interval=0.1)
    
    # Start monitoring
    monitor.start()
    assert monitor.running
    
    # Let it run for a short time
    time.sleep(0.3)
    
    # Stop monitoring
    monitor.stop()
    assert not monitor.running
    
    # Should have captured at least 2 measurements
    assert len(monitor.metrics) >= 2
    
    # Verify metrics have reasonable values
    for metric in monitor.metrics:
        assert 0 <= metric.cpu_percent <= 100
        assert 0 <= metric.memory_percent <= 100
        assert metric.memory_used > 0
        assert metric.memory_available > 0


def test_get_metrics():
    """Test getting metrics as dictionaries."""
    monitor = HardwareMonitor(interval=0.1)
    monitor.start()
    time.sleep(0.2)
    monitor.stop()
    
    metrics = monitor.get_metrics()
    assert isinstance(metrics, list)
    assert len(metrics) == len(monitor.metrics)
    
    # Check that each metric is a dictionary with expected keys
    for metric in metrics:
        assert isinstance(metric, dict)
        assert 'timestamp' in metric
        assert 'cpu_percent' in metric
        assert 'memory_percent' in metric


def test_get_summary():
    """Test getting a summary of the captured metrics."""
    monitor = HardwareMonitor(interval=0.1)
    monitor.start()
    time.sleep(0.3)  # Ensure we capture multiple data points
    monitor.stop()
    
    summary = monitor.get_summary()
    assert isinstance(summary, dict)
    assert 'start_time' in summary
    assert 'end_time' in summary
    assert 'duration_seconds' in summary
    assert 'cpu_avg' in summary
    assert 'memory_max' in summary
    
    # Check that the summary values are reasonable
    assert summary['duration_seconds'] > 0
    assert 0 <= summary['cpu_avg'] <= 100
    assert 0 <= summary['memory_max'] <= 100


@pytest.mark.skipif(not hasattr(psutil, 'sensors_temperatures'), 
                   reason="Temperature sensors not available")
def test_cpu_temperature():
    """Test getting CPU temperature (if available)."""

    from script.test_script.hardware_monitor import get_cpu_temperature
    temp = get_cpu_temperature()
    
    # Temperature should be None or a reasonable value
    if temp is not None:
        assert 0 <= temp <= 120  # Reasonable CPU temp range in Celsius

if __name__ == "__main__":
    # Run the tests
    import pytest
    pytest.main([__file__, "-v"])
