"""
Configuration manager for benchmark application.
Handles loading, saving, and managing application settings.
"""
import json
import os
import logging
from typing import Any, Dict, Optional, Union, List
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages application configuration with support for profiles and validation."""
    
    def __init__(self, config_file: str = None):
        """Initialize the configuration manager.
        
        Args:
            config_file: Path to the configuration file. If None, uses default location.
        """
        self.config_file = config_file or str(Path.home() / '.benchmark_config.json')
        self.config: Dict[str, Any] = self._load_default_config()
        self.current_profile = 'default'
        self.profiles: Dict[str, Dict[str, Any]] = {}
        self._load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration values."""
        return {
            'app': {
                'theme': 'system',  # 'light', 'dark', or 'system'
                'language': 'en',
                'check_for_updates': True,
                'auto_update': False,
                'notifications': True,
                'log_level': 'INFO',
                'max_log_files': 10,
                'max_log_size_mb': 10,
            },
            'benchmark': {
                'default_iterations': 10,
                'warmup_iterations': 3,
                'timeout_seconds': 300,
                'save_results': True,
                'result_directory': str(Path.home() / 'benchmark_results'),
                'export_format': 'json',  # 'json', 'csv', or 'both'
                'compress_results': True,
            },
            'hardware_monitor': {
                'enabled': True,
                'interval_seconds': 1.0,
                'track_cpu': True,
                'track_memory': True,
                'track_disk': True,
                'track_network': True,
                'track_temperature': True,
                'track_gpu': True,
            },
            'visualization': {
                'theme': 'system',  # 'light', 'dark', or 'system'
                'show_grid': True,
                'smooth_lines': True,
                'animation_enabled': True,
                'animation_duration': 1000,  # ms
                'default_chart_type': 'line',
                'default_time_range': '7d',
                'point_size': 8,
                'line_width': 2,
            },
            'notifications': {
                'on_completion': True,
                'on_error': True,
                'on_warning': False,
                'sound_enabled': True,
                'desktop_notifications': True,
            },
            'advanced': {
                'debug_mode': False,
                'enable_telemetry': False,
                'telemetry_url': 'https://telemetry.example.com',
                'max_workers': None,  # None for auto-detect
                'memory_limit_mb': None,  # None for no limit
            },
        }
    
    def _load_config(self):
        """Load configuration from file if it exists, otherwise create it."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.config = self._merge_dicts(self.config, data.get('config', {}))
                    self.profiles = data.get('profiles', {})
                    self.current_profile = data.get('current_profile', 'default')
                logger.info(f"Configuration loaded from {self.config_file}")
            else:
                self._save_config()
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            # Reset to defaults on error
            self.config = self._load_default_config()
    
    def save(self):
        """Save the current configuration to file."""
        self._save_config()
    
    def _save_config(self):
        """Save configuration to file."""
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.config_file)), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'config': self.config,
                    'profiles': self.profiles,
                    'current_profile': self.current_profile,
                }, f, indent=4, ensure_ascii=False)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by dot notation key.
        
        Args:
            key: Dot notation key (e.g., 'app.theme')
            default: Default value if key not found
            
        Returns:
            The configuration value or default if not found
        """
        return self._get_nested(self.config, key.split('.'), default)
    
    def set(self, key: str, value: Any, save: bool = True):
        """Set a configuration value by dot notation key.
        
        Args:
            key: Dot notation key (e.g., 'app.theme')
            value: Value to set
            save: Whether to save the configuration after setting
        """
        keys = key.split('.')
        d = self.config
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value
        
        if save:
            self.save()
    
    def create_profile(self, name: str, copy_from: str = None):
        """Create a new configuration profile.
        
        Args:
            name: Name of the new profile
            copy_from: Optional name of profile to copy settings from
        """
        if name in self.profiles:
            raise ValueError(f"Profile '{name}' already exists")
            
        if copy_from and copy_from in self.profiles:
            self.profiles[name] = self._deep_copy(self.profiles[copy_from])
        else:
            self.profiles[name] = self._deep_copy(self.config)
        
        self.save()
    
    def delete_profile(self, name: str):
        """Delete a configuration profile.
        
        Args:
            name: Name of the profile to delete
        """
        if name not in self.profiles:
            raise ValueError(f"Profile '{name}' does not exist")
            
        if self.current_profile == name:
            self.current_profile = 'default'
            
        del self.profiles[name]
        self.save()
    
    def switch_profile(self, name: str):
        """Switch to a different configuration profile.
        
        Args:
            name: Name of the profile to switch to
        """
        if name not in self.profiles and name != 'default':
            raise ValueError(f"Profile '{name}' does not exist")
            
        # Save current config to current profile
        if self.current_profile != 'default':
            self.profiles[self.current_profile] = self._deep_copy(self.config)
        
        # Load new profile
        self.current_profile = name
        if name == 'default':
            self.config = self._load_default_config()
        else:
            self.config = self._deep_copy(self.profiles[name])
        
        self.save()
    
    def reset_to_defaults(self):
        """Reset configuration to default values."""
        self.config = self._load_default_config()
        self.current_profile = 'default'
        self.save()
    
    @staticmethod
    def _get_nested(d: dict, keys: list, default: Any = None) -> Any:
        """Get a nested value from a dictionary using a list of keys."""
        if not keys:
            return d
            
        key = keys[0]
        if key in d:
            if len(keys) == 1:
                return d[key]
            elif isinstance(d[key], dict):
                return ConfigManager._get_nested(d[key], keys[1:], default)
        return default
    
    @staticmethod
    def _merge_dicts(base: dict, update: dict) -> dict:
        """Recursively merge two dictionaries."""
        result = base.copy()
        for k, v in update.items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = ConfigManager._merge_dicts(result[k], v)
            else:
                result[k] = v
        return result
    
    @staticmethod
    def _deep_copy(obj: Any) -> Any:
        """Create a deep copy of an object that can be JSON serialized."""
        return json.loads(json.dumps(obj))
