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
from typing import Dict, Any

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
