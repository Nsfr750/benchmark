"""
Hardware monitoring module for tracking system resources during benchmark tests.
"""
import time
import psutil
import platform
import logging
import threading
import traceback
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class HardwareMetrics:
    """Class to store hardware metrics at a point in time."""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used: float  # in MB
    memory_available: float  # in MB
    disk_read_bytes: int
    disk_write_bytes: int
    net_sent_bytes: int
    net_recv_bytes: int
    cpu_temp: Optional[float] = None  # in Celsius
    gpu_usage: Optional[float] = None  # percent
    gpu_temp: Optional[float] = None  # in Celsius
    gpu_memory_used: Optional[float] = None  # in MB

def get_cpu_temperature() -> Optional[float]:
    """Get CPU temperature if available."""
    try:
        if platform.system() == 'Linux':
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = float(f.read()) / 1000.0
                return temp
        elif platform.system() == 'Windows':
            import wmi
            w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            temperature_infos = w.Sensor()
            for sensor in temperature_infos:
                if sensor.SensorType == 'Temperature' and 'CPU' in sensor.Name:
                    return float(sensor.Value)
    except Exception as e:
        logger.warning(f"Could not get CPU temperature: {e}")
    return None

class HardwareMonitor:
    """Monitor hardware metrics during benchmark execution."""
    
    def __init__(self, interval: float = 1.0):
        """Initialize the hardware monitor.
        
        Args:
            interval: Time between measurements in seconds.
        """
        self.interval = interval
        self.running = False
        self.metrics: List[HardwareMetrics] = []
        self._start_time = 0
        self._last_disk_io = psutil.disk_io_counters()
        self._last_net_io = psutil.net_io_counters()
        self._monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._exception: Optional[Exception] = None
        
    def _monitor_loop(self):
        """Background thread that captures metrics at regular intervals."""
        try:
            while self.running:
                start_time = time.time()
                self.capture_metrics()
                
                # Calculate sleep time, ensuring we don't sleep for a negative duration
                elapsed = time.time() - start_time
                sleep_time = max(0, self.interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
        except Exception as e:
            self._exception = e
            logger.error(f"Error in monitor thread: {e}\n{traceback.format_exc()}")
            self.running = False
    
    def start(self):
        """Start monitoring hardware metrics."""
        with self._lock:
            if self.running:
                logger.warning("Hardware monitoring is already running")
                return
                
            self.running = True
            self._start_time = time.time()
            self.metrics = []
            self._exception = None
            
            # Get initial disk and network I/O counters
            self._last_disk_io = psutil.disk_io_counters()
            self._last_net_io = psutil.net_io_counters()
            
            # Start the monitoring thread
            self._monitor_thread = threading.Thread(
                target=self._monitor_loop,
                name="HardwareMonitor",
                daemon=True
            )
            self._monitor_thread.start()
            
            logger.info(f"Hardware monitoring started with {self.interval}s interval")
        
    def stop(self):
        """Stop monitoring hardware metrics."""
        with self._lock:
            if not self.running:
                return
                
            self.running = False
            
            # Wait for the monitoring thread to finish
            if self._monitor_thread and self._monitor_thread.is_alive():
                self._monitor_thread.join(timeout=2.0)
                
            # Check if there was an exception in the monitoring thread
            if self._exception:
                logger.error(f"Error in monitoring thread: {self._exception}")
                raise self._exception
                
            logger.info(f"Hardware monitoring stopped. Collected {len(self.metrics)} data points.")
        
    def capture_metrics(self):
        """Capture current hardware metrics."""
        if not self.running:
            return
            
        try:
            # Get CPU and memory usage
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            
            # Get disk I/O
            disk_io = psutil.disk_io_counters()
            disk_read = disk_io.read_bytes - self._last_disk_io.read_bytes if self._last_disk_io else 0
            disk_write = disk_io.write_bytes - self._last_disk_io.write_bytes if self._last_disk_io else 0
            self._last_disk_io = disk_io
            
            # Get network I/O
            net_io = psutil.net_io_counters()
            net_sent = net_io.bytes_sent - self._last_net_io.bytes_sent if self._last_net_io else 0
            net_recv = net_io.bytes_recv - self._last_net_io.bytes_recv if self._last_net_io else 0
            self._last_net_io = net_io
            
            # Get CPU temperature if available
            cpu_temp = get_cpu_temperature()
            
            # Create metrics object
            metrics = HardwareMetrics(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used=memory.used / (1024 * 1024),  # Convert to MB
                memory_available=memory.available / (1024 * 1024),  # Convert to MB
                disk_read_bytes=disk_read,
                disk_write_bytes=disk_write,
                net_sent_bytes=net_sent,
                net_recv_bytes=net_recv,
                cpu_temp=cpu_temp
            )
            
            with self._lock:
                self.metrics.append(metrics)
            
        except Exception as e:
            logger.error(f"Error capturing hardware metrics: {e}")
            raise  # Re-raise to be caught by the monitoring thread
    
    def get_metrics(self) -> List[Dict[str, Any]]:
        """Get all captured metrics as a list of dictionaries."""
        with self._lock:
            return [asdict(m) for m in self.metrics]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the captured metrics."""
        with self._lock:
            if not self.metrics:
                return {}
                
            cpu_percent = [m.cpu_percent for m in self.metrics]
            memory_percent = [m.memory_percent for m in self.metrics]
            
            return {
                'start_time': datetime.fromtimestamp(self.metrics[0].timestamp).isoformat(),
                'end_time': datetime.fromtimestamp(self.metrics[-1].timestamp).isoformat(),
                'duration_seconds': self.metrics[-1].timestamp - self.metrics[0].timestamp,
                'cpu_avg': sum(cpu_percent) / len(cpu_percent) if cpu_percent else 0,
                'cpu_max': max(cpu_percent) if cpu_percent else 0,
                'memory_avg': sum(memory_percent) / len(memory_percent) if memory_percent else 0,
                'memory_max': max(memory_percent) if memory_percent else 0,
                'total_disk_read_mb': sum(m.disk_read_bytes for m in self.metrics) / (1024 * 1024),
                'total_disk_write_mb': sum(m.disk_write_bytes for m in self.metrics) / (1024 * 1024),
                'total_network_sent_mb': sum(m.net_sent_bytes for m in self.metrics) / (1024 * 1024),
                'total_network_recv_mb': sum(m.net_recv_bytes for m in self.metrics) / (1024 * 1024),
                'samples': len(self.metrics)
            }
