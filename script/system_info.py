"""
System information collection module for the Benchmark application.
Collects hardware and software information for benchmarking context.
"""
import platform
import psutil
import socket
import cpuinfo
import json
from datetime import datetime
from typing import Dict, Any, Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QTabWidget, QWidget, QFormLayout, QGroupBox,
    QTreeWidget, QTreeWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from script.lang_mgr import get_language_manager, get_text

def get_system_info() -> Dict[str, Any]:
    """
    Collect comprehensive system information.
    
    Returns:
        Dict containing system information
    """
    try:
        # Get CPU information
        cpu_info = cpuinfo.get_cpu_info()
        
        # Get memory information
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Get disk information
        disk_usage = psutil.disk_usage('/' if platform.system() != 'Windows' else 'C:')
        
        # Get network information
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        
        # Get OS information
        os_info = {
            'system': platform.system(),
            'node': platform.node(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'python_compiler': platform.python_compiler(),
            'python_implementation': platform.python_implementation(),
        }
        
        # Compile all information
        system_info = {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'brand': cpu_info.get('brand_raw', 'Unknown'),
                'cores': psutil.cpu_count(logical=False),
                'logical_cores': psutil.cpu_count(logical=True),
                'hz_actual': cpu_info.get('hz_actual_friendly', 'Unknown'),
                'hz_advertised': cpu_info.get('hz_advertised_friendly', 'Unknown'),
                'architecture': cpu_info.get('arch_string_raw', 'Unknown'),
                'bits': cpu_info.get('bits', 'Unknown'),
            },
            'memory': {
                'total': mem.total,
                'available': mem.available,
                'used': mem.used,
                'free': mem.free,
                'percent': mem.percent,
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_free': swap.free,
                'swap_percent': swap.percent,
            },
            'disk': {
                'total': disk_usage.total,
                'used': disk_usage.used,
                'free': disk_usage.free,
                'percent': disk_usage.percent,
            },
            'network': {
                'hostname': hostname,
                'ip_address': ip_address,
            },
            'os': os_info,
            'environment': {
                'python_version': platform.python_version(),
                'system': platform.system(),
                'release': platform.release(),
            }
        }
        
        return system_info
        
    except Exception as e:
        # Return minimal information if detailed collection fails
        return {
            'error': str(e),
            'minimal_info': {
                'system': platform.system(),
                'node': platform.node(),
                'python_version': platform.python_version(),
                'timestamp': datetime.now().isoformat()
            }
        }

def save_system_info(file_path: str, format: str = 'json') -> bool:
    """
    Save system information to a file.
    
    Args:
        file_path: Path to save the file
        format: Output format ('json' or 'txt')
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        sys_info = get_system_info()
        
        if format.lower() == 'json':
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(sys_info, f, indent=4, ensure_ascii=False)
        else:  # txt format
            with open(file_path, 'w', encoding='utf-8') as f:
                for category, data in sys_info.items():
                    if category == 'timestamp':
                        f.write(f"Timestamp: {data}\n\n")
                        continue
                    f.write(f"=== {category.upper()} ===\n")
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, dict):
                                f.write(f"{key}:\n")
                                for subkey, subvalue in value.items():
                                    f.write(f"  {subkey}: {subvalue}\n")
                            else:
                                f.write(f"{key}: {value}\n")
                    else:
                        f.write(f"{data}\n")
                    f.write("\n")
        return True
    except Exception as e:
        print(f"Error saving system info: {e}")
        return False


class SystemInfoDialog(QDialog):
    """Dialog for displaying system information."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = get_language_manager()
        self.setup_ui()
        self.retranslate_ui()
        self.load_system_info()
    
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle(get_text("system_info.title", "System Information"))
        self.setMinimumSize(800, 600)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Create tabs
        self.tabs = QTabWidget()
        
        # System Tab
        system_tab = QWidget()
        system_layout = QVBoxLayout(system_tab)
        
        # System Info Group
        system_group = QGroupBox()
        system_group_layout = QFormLayout()
        
        self.system_info = {}
        self.system_info['os'] = QLabel()
        self.system_info['hostname'] = QLabel()
        self.system_info['ip_address'] = QLabel()
        self.system_info['python_version'] = QLabel()
        
        system_group_layout.addRow(QLabel(get_text("system_info.os", "Operating System:")), 
                                 self.system_info['os'])
        system_group_layout.addRow(QLabel(get_text("system_info.hostname", "Hostname:")), 
                                 self.system_info['hostname'])
        system_group_layout.addRow(QLabel(get_text("system_info.ip_address", "IP Address:")), 
                                 self.system_info['ip_address'])
        system_group_layout.addRow(QLabel(get_text("system_info.python_version", "Python Version:")), 
                                 self.system_info['python_version'])
        
        system_group.setLayout(system_group_layout)
        
        # CPU Tab
        cpu_tab = QWidget()
        cpu_layout = QVBoxLayout(cpu_tab)
        
        cpu_group = QGroupBox()
        cpu_group_layout = QFormLayout()
        
        self.cpu_info = {}
        self.cpu_info['brand'] = QLabel()
        self.cpu_info['cores'] = QLabel()
        self.cpu_info['threads'] = QLabel()
        self.cpu_info['architecture'] = QLabel()
        
        cpu_group_layout.addRow(QLabel(get_text("system_info.cpu_model", "CPU Model:")), 
                              self.cpu_info['brand'])
        cpu_group_layout.addRow(QLabel(get_text("system_info.cores", "Cores:")), 
                              self.cpu_info['cores'])
        cpu_group_layout.addRow(QLabel(get_text("system_info.threads", "Threads:")), 
                              self.cpu_info['threads'])
        cpu_group_layout.addRow(QLabel(get_text("system_info.architecture", "Architecture:")), 
                              self.cpu_info['architecture'])
        
        cpu_group.setLayout(cpu_group_layout)
        
        # Memory Tab
        mem_tab = QWidget()
        mem_layout = QVBoxLayout(mem_tab)
        
        mem_group = QGroupBox()
        mem_group_layout = QFormLayout()
        
        self.mem_info = {}
        self.mem_info['total'] = QLabel()
        self.mem_info['available'] = QLabel()
        self.mem_info['used'] = QLabel()
        self.mem_info['percent'] = QLabel()
        
        mem_group_layout.addRow(QLabel(get_text("system_info.total_memory", "Total Memory:")), 
                              self.mem_info['total'])
        mem_group_layout.addRow(QLabel(get_text("system_info.available_memory", "Available Memory:")), 
                              self.mem_info['available'])
        mem_group_layout.addRow(QLabel(get_text("system_info.used_memory", "Used Memory:")), 
                              self.mem_info['used'])
        mem_group_layout.addRow(QLabel(get_text("system_info.memory_usage", "Memory Usage:")), 
                              self.mem_info['percent'])
        
        mem_group.setLayout(mem_group_layout)
        
        # Disk Tab
        disk_tab = QWidget()
        disk_layout = QVBoxLayout(disk_tab)
        
        disk_group = QGroupBox()
        disk_group_layout = QFormLayout()
        
        self.disk_info = {}
        self.disk_info['total'] = QLabel()
        self.disk_info['used'] = QLabel()
        self.disk_info['free'] = QLabel()
        self.disk_info['percent'] = QLabel()
        
        disk_group_layout.addRow(QLabel(get_text("system_info.disk_total", "Total Space:")), 
                               self.disk_info['total'])
        disk_group_layout.addRow(QLabel(get_text("system_info.disk_used", "Used Space:")), 
                               self.disk_info['used'])
        disk_group_layout.addRow(QLabel(get_text("system_info.disk_free", "Free Space:")), 
                               self.disk_info['free'])
        disk_group_layout.addRow(QLabel(get_text("system_info.disk_usage", "Disk Usage:")), 
                               self.disk_info['percent'])
        
        disk_group.setLayout(disk_group_layout)
        
        # Raw Info Tab
        raw_tab = QWidget()
        raw_layout = QVBoxLayout(raw_tab)
        
        self.raw_info = QTextEdit()
        self.raw_info.setReadOnly(True)
        self.raw_info.setFont(QFont("Courier", 9))
        
        # Assemble tabs
        system_layout.addWidget(system_group)
        system_layout.addStretch()
        
        cpu_layout.addWidget(cpu_group)
        cpu_layout.addStretch()
        
        mem_layout.addWidget(mem_group)
        mem_layout.addStretch()
        
        disk_layout.addWidget(disk_group)
        disk_layout.addStretch()
        
        raw_layout.addWidget(self.raw_info)
        
        # Add tabs
        self.tabs.addTab(system_tab, get_text("system_info.tab_system", "System"))
        self.tabs.addTab(cpu_tab, get_text("system_info.tab_cpu", "CPU"))
        self.tabs.addTab(mem_tab, get_text("system_info.tab_memory", "Memory"))
        self.tabs.addTab(disk_tab, get_text("system_info.tab_disk", "Disk"))
        self.tabs.addTab(raw_tab, get_text("system_info.tab_raw", "Raw Info"))
        
        # Buttons
        button_box = QHBoxLayout()
        self.refresh_btn = QPushButton()
        self.refresh_btn.clicked.connect(self.load_system_info)
        
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
        self.setWindowTitle(get_text("system_info.title", "System Information"))
        self.refresh_btn.setText(get_text("common.refresh", "Refresh"))
        
        # Update tab names
        self.tabs.setTabText(0, get_text("system_info.tab_system", "System"))
        self.tabs.setTabText(1, get_text("system_info.tab_cpu", "CPU"))
        self.tabs.setTabText(2, get_text("system_info.tab_memory", "Memory"))
        self.tabs.setTabText(3, get_text("system_info.tab_disk", "Disk"))
        self.tabs.setTabText(4, get_text("system_info.tab_raw", "Raw Info"))
    
    def format_bytes(self, bytes_count):
        """Format bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.2f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.2f} PB"
    
    def load_system_info(self):
        """Load and display system information."""
        try:
            info = get_system_info()
            
            # System Info with safe dictionary access
            os_system = info.get('os', {}).get('system', platform.system())
            os_release = info.get('os', {}).get('release', platform.release())
            os_version = info.get('os', {}).get('version', platform.version())
            python_version = info.get('environment', {}).get('python_version', platform.python_version())
            
            self.system_info['os'].setText(f"{os_system} {os_release} ({os_version})")
            self.system_info['hostname'].setText(info.get('network', {}).get('hostname', 'Unknown'))
            self.system_info['ip_address'].setText(info.get('network', {}).get('ip_address', 'Unknown'))
            self.system_info['python_version'].setText(python_version)
            
            # CPU Info with safe dictionary access
            cpu_brand = info.get('cpu', {}).get('brand', 'Unknown')
            cpu_cores = info.get('cpu', {}).get('cores', psutil.cpu_count(logical=False))
            cpu_arch = info.get('cpu', {}).get('architecture', platform.machine())
            
            self.cpu_info['brand'].setText(cpu_brand)
            self.cpu_info['cores'].setText(str(cpu_cores))
            self.cpu_info['threads'].setText(str(psutil.cpu_count(logical=True)))
            self.cpu_info['architecture'].setText(cpu_arch)
            
            # Memory Info
            total_mem = info['memory']['total']
            available_mem = info['memory']['available']
            used_mem = info['memory']['used']
            percent = info['memory']['percent']
            
            self.mem_info['total'].setText(self.format_bytes(total_mem))
            self.mem_info['available'].setText(self.format_bytes(available_mem))
            self.mem_info['used'].setText(self.format_bytes(used_mem))
            self.mem_info['percent'].setText(f"{percent}%")
            
            # Disk Info
            total_disk = info['disk']['total']
            used_disk = info['disk']['used']
            free_disk = info['disk']['free']
            disk_percent = info['disk']['percent']
            
            self.disk_info['total'].setText(self.format_bytes(total_disk))
            self.disk_info['used'].setText(self.format_bytes(used_disk))
            self.disk_info['free'].setText(self.format_bytes(free_disk))
            self.disk_info['percent'].setText(f"{disk_percent}%")
            
            # Raw Info
            self.raw_info.setPlainText(json.dumps(info, indent=4, sort_keys=True))
            
        except Exception as e:
            import traceback
            error_msg = f"Error loading system information: {str(e)}\n\n{traceback.format_exc()}"
            self.raw_info.setPlainText(error_msg)
