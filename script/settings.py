"""
Settings management for the Benchmark application.
"""
import os
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, 
    QFormLayout, QSpinBox, QCheckBox, QDialogButtonBox,
    QComboBox
)

from script.lang_mgr import get_language_manager

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = get_language_manager()
        self.setWindowTitle(self.tr('Settings'))
        self.setMinimumSize(600, 400)
        
        self.settings = self.load_settings()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # General tab
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)
        
        # Language selection
        self.language_combo = QComboBox()
        
        # Add available languages
        self.languages = [
            ('en', 'English'),
            ('it', 'Italiano')
        ]
        
        for code, name in self.languages:
            self.language_combo.addItem(f"{name} ({code})", code)
            
        general_layout.addRow(self.tr('Language:'), self.language_combo)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([
            self.tr('Light'),
            self.tr('Dark'),
            self.tr('System')
        ])
        general_layout.addRow(self.tr('Theme:'), self.theme_combo)
        
        # Startup options
        self.start_minimized = QCheckBox(self.tr('Start minimized'))
        general_layout.addRow('', self.start_minimized)
        
        # Update options
        self.check_updates = QCheckBox(self.tr('Check for updates on startup'))
        general_layout.addRow('', self.check_updates)
        
        self.tabs.addTab(general_tab, self.lang.get_text('settings.general', 'General'))
        
        # Add more tabs as needed
        # advanced_tab = QWidget()
        # self.tabs.addTab(advanced_tab, "Advanced")
        
        layout.addWidget(self.tabs)
        
        # Add dialog buttons
        from PySide6.QtWidgets import QDialogButtonBox, QPushButton
        from PySide6.QtCore import Qt
        
        self.button_box = QDialogButtonBox()
        self.button_box.setOrientation(Qt.Horizontal)
        
        # Add standard buttons
        self.ok_button = self.button_box.addButton(QDialogButtonBox.Ok)
        self.cancel_button = self.button_box.addButton(QDialogButtonBox.Cancel)
        self.apply_button = self.button_box.addButton(QDialogButtonBox.Apply)
        
        # Connect signals
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        self.apply_button.clicked.connect(self.apply_settings)
        
        layout.addWidget(self.button_box)
        
        # Load current settings
        self.load_current_settings()
    
    def load_settings(self):
        """Load settings from file or return defaults."""
        config_path = self.get_config_path()
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
        
        # Default settings
        return {
            'theme': 'System',
            'start_minimized': False,
            'language': 'en',
            'check_updates': True
        }
    
    def save_settings(self):
        """Save current settings to file."""
        config_path = self.get_config_path()
        os.makedirs(config_path.parent, exist_ok=True)
        
        try:
            with open(config_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get_config_path(self):
        """Get the path to the settings file."""
        config_dir = Path(__file__).parent.parent / 'config'
        config_dir.mkdir(exist_ok=True)
        return config_dir / 'config.json'
    
    def load_current_settings(self):
        """Load current settings into the UI"""
        # Load language
        current_lang = self.settings.get('language', 'en')
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        
        # Load theme
        theme_map = {
            'Light': self.tr('Light'),
            'Dark': self.tr('Dark'),
            'System': self.tr('System')
        }
        current_theme = self.settings.get('theme', 'System')
        self.theme_combo.setCurrentText(theme_map.get(current_theme, theme_map['System']))
        
        # Set other options
        self.start_minimized.setChecked(self.settings.get('start_minimized', False))
        self.check_updates.setChecked(self.settings.get('check_updates', True))
    
    def gather_settings(self):
        """Gather settings from UI controls."""
        # Get selected language code
        selected_lang = self.language_combo.currentData() or 'en'
        
        # Map theme text back to internal value
        theme_text = self.theme_combo.currentText()
        if theme_text == self.tr('Light'):
            selected_theme = 'Light'
        elif theme_text == self.tr('Dark'):
            selected_theme = 'Dark'
        else:
            selected_theme = 'System'
        
        return {
            'theme': selected_theme,
            'start_minimized': self.start_minimized.isChecked(),
            'language': selected_lang,
            'check_updates': self.check_updates.isChecked()
        }
    
    def apply_settings(self):
        """Apply settings and save them."""
        new_settings = self.gather_settings()
        language_changed = (self.settings.get('language') != new_settings['language'])
        theme_changed = (self.settings.get('theme') != new_settings['theme'])
        
        self.settings.update(new_settings)
        self.save_settings()
        
        # Apply settings in main app
        if hasattr(self.parent(), 'apply_settings'):
            self.parent().apply_settings(self.settings)
            
        # If language changed, show message that restart is needed
        if language_changed:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                self.lang.get_text('settings.restart_required', 'Restart Required'),
                self.lang.get_text(
                    'settings.language_change_message',
                    'Language change will take effect after restarting the application.'
                )
            )
    
    def accept(self):
        self.apply_settings()
        super().accept()

def show_settings(parent=None):
    """Show the settings dialog."""
    dialog = SettingsDialog(parent)
    return dialog.exec()
