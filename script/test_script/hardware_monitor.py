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

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QProgressBar, QTabWidget, QWidget, QFormLayout, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal as QSignal
from PySide6.QtGui import QFont, QColor
from script.lang_mgr import get_language_manager, get_text

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
    """
    Get CPU temperature using multiple methods.
    Returns temperature in Celsius or None if not available.
    """
    system = platform.system()
    
    # Linux implementation
    if system == 'Linux':
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = float(f.read().strip()) / 1000.0
                return temp if temp > 0 and temp < 120 else None
        except (FileNotFoundError, ValueError, IOError) as e:
            logger.debug(f"Linux temperature read failed: {e}")
    
    # Windows implementation
    elif system == 'Windows':
        # Try OpenHardwareMonitor WMI
        try:
            import wmi
            w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            for sensor in w.Sensor():
                if sensor.SensorType == 'Temperature' and 'CPU' in sensor.Name:
                    temp = float(sensor.Value)
                    if 0 < temp < 120:  # Basic sanity check
                        return temp
        except Exception as e:
            logger.debug(f"OpenHardwareMonitor WMI failed: {e}")
        
        # Try standard WMI for CPU temperature
        try:
            import wmi
            w = wmi.WMI(namespace="root\\wmi")
            temps = w.MSAcpi_ThermalZoneTemperature()
            if temps:
                temp = (float(temps[0].CurrentTemperature) / 10.0) - 273.15  # Kelvin to Celsius
                if 0 < temp < 120:
                    return temp
        except Exception as e:
            logger.debug(f"Standard WMI temperature read failed: {e}")
        
        # Try using psutil if available (Windows 10+)
        try:
            import ctypes
            from ctypes import wintypes
            
            class FILETIME(ctypes.Structure):
                _fields_ = [
                    ('dwLowDateTime', wintypes.DWORD),
                    ('dwHighDateTime', wintypes.DWORD)
                ]
            
            class SYSTEM_POWER_STATUS(ctypes.Structure):
                _fields_ = [
                    ('ACLineStatus', wintypes.BYTE),
                    ('BatteryFlag', wintypes.BYTE),
                    ('BatteryLifePercent', wintypes.BYTE),
                    ('Reserved1', wintypes.BYTE),
                    ('BatteryLifeTime', wintypes.DWORD),
                    ('BatteryFullLifeTime', wintypes.DWORD)
                ]
            
            GetSystemPowerStatus = ctypes.windll.kernel32.GetSystemPowerStatus
            GetSystemPowerStatus.argtypes = [ctypes.POINTER(SYSTEM_POWER_STATUS)]
            GetSystemPowerStatus.restype = wintypes.BOOL
            
            status = SYSTEM_POWER_STATUS()
            if GetSystemPowerStatus(ctypes.pointer(status)):
                # Some systems report temperature in BatteryLifePercent when on AC
                if status.ACLineStatus == 1 and 0 < status.BatteryLifePercent < 120:
                    return float(status.BatteryLifePercent)
        except Exception as e:
            logger.debug(f"Power status temperature read failed: {e}")
    
    # macOS implementation
    elif system == 'Darwin':
        try:
            import subprocess
            process = subprocess.Popen(['osx-cpu-temp'], stdout=subprocess.PIPE)
            output = process.communicate()[0].decode('utf-8').strip()
            if output.endswith('°C'):
                temp = float(output[:-2])
                if 0 < temp < 120:
                    return temp
        except (FileNotFoundError, ValueError, subprocess.SubprocessError) as e:
            logger.debug(f"macOS temperature read failed: {e}")
    
    logger.debug("No valid CPU temperature reading method available")
    return None


class HardwareMonitor(QThread):
    """Thread for monitoring hardware metrics."""
    metrics_updated = QSignal(dict)  # Emits the latest metrics
    
    def __init__(self, update_interval=1.0, parent=None):
        super().__init__(parent)
        self.update_interval = update_interval
        self.running = True
        self.disk_io_start = psutil.disk_io_counters()
        self.net_io_start = psutil.net_io_counters()
    
    def run(self):
        """Main monitoring loop."""
        while self.running:
            try:
                # Get CPU and memory info
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                
                # Get disk and network I/O
                disk_io = psutil.disk_io_counters()
                net_io = psutil.net_io_counters()
                
                # Calculate deltas
                disk_read = disk_io.read_bytes - self.disk_io_start.read_bytes
                disk_write = disk_io.write_bytes - self.disk_io_start.write_bytes
                net_sent = net_io.bytes_sent - self.net_io_start.bytes_sent
                net_recv = net_io.bytes_recv - self.net_io_start.bytes_recv
                
                # Update start values for next iteration
                self.disk_io_start = disk_io
                self.net_io_start = net_io
                
                # Get temperatures
                cpu_temp = get_cpu_temperature()
                
                # Create metrics object
                metrics = {
                    'timestamp': time.time(),
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_used': memory.used / (1024 * 1024),  # Convert to MB
                    'memory_available': memory.available / (1024 * 1024),  # Convert to MB
                    'disk_read_bytes': disk_read,
                    'disk_write_bytes': disk_write,
                    'net_sent_bytes': net_sent,
                    'net_recv_bytes': net_recv,
                    'cpu_temp': cpu_temp,
                    'gpu_usage': None,  # Placeholder for GPU metrics
                    'gpu_temp': None,   # Placeholder for GPU temperature
                    'gpu_memory_used': None  # Placeholder for GPU memory
                }
                
                self.metrics_updated.emit(metrics)
                
                # Sleep for the update interval
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error in hardware monitor: {e}")
                time.sleep(1)  # Prevent tight loop on error
    
    def stop(self):
        """Stop the monitoring thread."""
        self.running = False
        self.wait()


class HardwareMonitorDialog(QDialog):
    """Dialog for displaying real-time hardware monitoring."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = get_language_manager()
        self.monitor = None
        self.setup_ui()
        self.retranslate_ui()
        self.start_monitoring()
    
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle(get_text("hardware_monitor.title", "Hardware Monitor"))
        self.setMinimumSize(800, 600)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Create tabs
        self.tabs = QTabWidget()
        
        # CPU Tab
        cpu_tab = QWidget()
        cpu_layout = QVBoxLayout(cpu_tab)
        
        # CPU Usage
        cpu_group = QGroupBox()
        cpu_group_layout = QFormLayout()
        
        self.cpu_usage = QProgressBar()
        self.cpu_usage.setRange(0, 100)
        self.cpu_temp = QLabel()
        
        cpu_group_layout.addRow(QLabel(get_text("hardware_monitor.cpu_usage", "CPU Usage:")), self.cpu_usage)
        cpu_group_layout.addRow(QLabel(get_text("hardware_monitor.cpu_temp", "CPU Temperature:")), self.cpu_temp)
        cpu_group.setLayout(cpu_group_layout)
        
        # Memory Tab
        mem_tab = QWidget()
        mem_layout = QVBoxLayout(mem_tab)
        
        mem_group = QGroupBox()
        mem_group_layout = QFormLayout()
        
        self.mem_usage = QProgressBar()
        self.mem_usage.setRange(0, 100)
        self.mem_used = QLabel()
        self.mem_available = QLabel()
        
        mem_group_layout.addRow(QLabel(get_text("hardware_monitor.memory_usage", "Memory Usage:")), self.mem_usage)
        mem_group_layout.addRow(QLabel(get_text("hardware_monitor.memory_used", "Memory Used:")), self.mem_used)
        mem_group_layout.addRow(QLabel(get_text("hardware_monitor.memory_available", "Memory Available:")), self.mem_available)
        mem_group.setLayout(mem_group_layout)
        
        # I/O Tab
        io_tab = QWidget()
        io_layout = QVBoxLayout(io_tab)
        
        disk_group = QGroupBox(get_text("hardware_monitor.disk_io", "Disk I/O"))
        disk_layout = QFormLayout()
        
        self.disk_read = QLabel()
        self.disk_write = QLabel()
        
        disk_layout.addRow(QLabel(get_text("hardware_monitor.read", "Read:")), self.disk_read)
        disk_layout.addRow(QLabel(get_text("hardware_monitor.write", "Write:")), self.disk_write)
        disk_group.setLayout(disk_layout)
        
        net_group = QGroupBox(get_text("hardware_monitor.network", "Network"))
        net_layout = QFormLayout()
        
        self.net_sent = QLabel()
        self.net_recv = QLabel()
        
        net_layout.addRow(QLabel(get_text("hardware_monitor.sent", "Sent:")), self.net_sent)
        net_layout.addRow(QLabel(get_text("hardware_monitor.received", "Received:")), self.net_recv)
        net_group.setLayout(net_layout)
        
        # Assemble tabs
        cpu_layout.addWidget(cpu_group)
        cpu_layout.addStretch()
        
        mem_layout.addWidget(mem_group)
        mem_layout.addStretch()
        
        io_layout.addWidget(disk_group)
        io_layout.addWidget(net_group)
        io_layout.addStretch()
        
        # Add tabs
        self.tabs.addTab(cpu_tab, get_text("hardware_monitor.cpu_tab", "CPU"))
        self.tabs.addTab(mem_tab, get_text("hardware_monitor.memory_tab", "Memory"))
        self.tabs.addTab(io_tab, get_text("hardware_monitor.io_tab", "I/O"))
        
        # Buttons
        button_box = QHBoxLayout()
        self.refresh_btn = QPushButton()
        self.refresh_btn.clicked.connect(self.refresh_metrics)
        
        self.close_btn = QPushButton(get_text("common.close", "Close"))
        self.close_btn.clicked.connect(self.accept)
        
        button_box.addWidget(self.refresh_btn)
        button_box.addStretch()
        button_box.addWidget(self.close_btn)
        
        # Add widgets to main layout
        layout.addWidget(self.tabs)
        layout.addLayout(button_box)
    
    def retranslate_ui(self):
        """Update UI text based on current language."""
        self.setWindowTitle(get_text("hardware_monitor.title", "Hardware Monitor"))
        self.refresh_btn.setText(get_text("common.refresh", "Refresh"))
        
        # Update tab names
        self.tabs.setTabText(0, get_text("hardware_monitor.cpu_tab", "CPU"))
        self.tabs.setTabText(1, get_text("hardware_monitor.memory_tab", "Memory"))
        self.tabs.setTabText(2, get_text("hardware_monitor.io_tab", "I/O"))
    
    def start_monitoring(self):
        """Start the hardware monitoring thread."""
        if self.monitor and hasattr(self.monitor, 'isRunning') and self.monitor.isRunning():
            return
            
        # Use the first HardwareMonitor class (QThread based)
        self.monitor = HardwareMonitor(1.0)  # Pass interval as positional argument
        if hasattr(self.monitor, 'metrics_updated'):
            self.monitor.metrics_updated.connect(self.update_metrics)
        self.monitor.start()
    
    def stop_monitoring(self):
        """Stop the hardware monitoring thread."""
        if self.monitor:
            self.monitor.stop()
            self.monitor = None
    
    def update_metrics(self, metrics):
        """Update the UI with the latest metrics."""
        # CPU
        self.cpu_usage.setValue(int(metrics['cpu_percent']))
        
        if metrics['cpu_temp'] is not None:
            self.cpu_temp.setText(f"{metrics['cpu_temp']:.1f}°C")
        else:
            self.cpu_temp.setText(get_text("common.not_available", "N/A"))
        
        # Memory
        self.mem_usage.setValue(int(metrics['memory_percent']))
        self.mem_used.setText(f"{metrics['memory_used']:.1f} MB")
        self.mem_available.setText(f"{metrics['memory_available']:.1f} MB")
        
        # Disk I/O
        self.disk_read.setText(self.format_bytes(metrics['disk_read_bytes']) + 
                             get_text("common.per_second", "/s"))
        self.disk_write.setText(self.format_bytes(metrics['disk_write_bytes']) + 
                              get_text("common.per_second", "/s"))
        
        # Network I/O
        self.net_sent.setText(self.format_bytes(metrics['net_sent_bytes']) + 
                            get_text("common.per_second", "/s"))
        self.net_recv.setText(self.format_bytes(metrics['net_recv_bytes']) + 
                            get_text("common.per_second", "/s"))
    
    def format_bytes(self, bytes_count):
        """Format bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.1f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.1f} TB"
    
    def refresh_metrics(self):
        """Force a refresh of the metrics."""
        if self.monitor:
            self.monitor.disk_io_start = psutil.disk_io_counters()
            self.monitor.net_io_start = psutil.net_io_counters()
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.stop_monitoring()
        event.accept()
    
    def __del__(self):
        """Ensure monitoring is stopped when the dialog is destroyed."""
        self.stop_monitoring()


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
