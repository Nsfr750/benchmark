"""
Theme management for the Benchmark application.
"""
import os
import json
import logging
from PySide6.QtGui import QPalette, QColor, QIcon
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings, QStandardPaths

log = logging.getLogger(__name__)

class ThemeManager:
    """Manages application themes and styles."""
    
    THEMES = {
        'light': {
            'name': 'Light',
            'background': '#f5f5f5',
            'foreground': '#333333',
            'primary': '#0078d7',
            'secondary': '#6c757d',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'border': '#dee2e6',
            'text': '#212529',
            'text_light': '#6c757d',
            'window': '#ffffff',
            'window_text': '#212529',
            'base': '#ffffff',
            'alternate_base': '#f8f9fa',
            'tooltip_base': '#ffffff',
            'tooltip_text': '#212529',
            'button': '#f8f9fa',
            'button_text': '#212529',
            'bright_text': '#ffffff',
            'link': '#0078d7',
            'highlight': '#0078d7',
            'highlighted_text': '#ffffff',
            'disabled': '#6c757d',
            'disabled_text': '#6c757d',
        },
        'dark': {
            'name': 'Dark',
            'background': '#2d2d2d',
            'foreground': '#e0e0e0',
            'primary': '#0078d7',
            'secondary': '#6c757d',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'border': '#444444',
            'text': '#f8f9fa',
            'text_light': '#adb5bd',
            'window': '#1e1e1e',
            'window_text': '#f8f9fa',
            'base': '#2d2d2d',
            'alternate_base': '#252526',
            'tooltip_base': '#2d2d2d',
            'tooltip_text': '#f8f9fa',
            'button': '#3e3e42',
            'button_text': '#f8f9fa',
            'bright_text': '#ffffff',
            'link': '#4da6ff',
            'highlight': '#0078d7',
            'highlighted_text': '#ffffff',
            'disabled': '#6c757d',
            'disabled_text': '#6c757d',
        }
    }
    
    def __init__(self, app):
        """Initialize the theme manager."""
        self.app = app
        self.settings = QSettings('Nsfr750', 'Benchmark')
        self.current_theme = self.settings.value('theme', 'light')
        
    def apply_theme(self, theme_name=None):
        """Apply the specified theme or the saved theme."""
        if theme_name is None:
            theme_name = self.current_theme
        else:
            self.current_theme = theme_name
            self.settings.setValue('theme', theme_name)
        
        if theme_name not in self.THEMES:
            log.warning(f"Theme '{theme_name}' not found, using 'light' theme")
            theme_name = 'light'
            
        theme = self.THEMES[theme_name]
        
        # Apply the theme to the application
        palette = QPalette()
        
        # Set color roles
        palette.setColor(QPalette.Window, QColor(theme['window']))
        palette.setColor(QPalette.WindowText, QColor(theme['window_text']))
        palette.setColor(QPalette.Base, QColor(theme['base']))
        palette.setColor(QPalette.AlternateBase, QColor(theme['alternate_base']))
        palette.setColor(QPalette.ToolTipBase, QColor(theme['tooltip_base']))
        palette.setColor(QPalette.ToolTipText, QColor(theme['tooltip_text']))
        palette.setColor(QPalette.Text, QColor(theme['text']))
        palette.setColor(QPalette.Button, QColor(theme['button']))
        palette.setColor(QPalette.ButtonText, QColor(theme['button_text']))
        palette.setColor(QPalette.BrightText, QColor(theme['bright_text']))
        palette.setColor(QPalette.Link, QColor(theme['link']))
        palette.setColor(QPalette.Highlight, QColor(theme['highlight']))
        palette.setColor(QPalette.HighlightedText, QColor(theme['highlighted_text']))
        
        # Disabled colors
        palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(theme['disabled_text']))
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(theme['disabled_text']))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(theme['disabled_text']))
        palette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(theme['disabled']))
        palette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(theme['highlighted_text']))
        
        # Apply the palette
        self.app.setPalette(palette)
        
        # Set style sheet for additional theming
        self.app.setStyleSheet(f"""
            QMainWindow, QDialog, QWidget {{
                background-color: {theme['window']};
                color: {theme['window_text']};
            }}
            QPushButton {{
                background-color: {theme['button']};
                color: {theme['button_text']};
                border: 1px solid {theme['border']};
                padding: 5px 10px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {theme['highlight']};
                color: {theme['highlighted_text']};
            }}
            QPushButton:disabled {{
                background-color: {theme['disabled']};
                color: {theme['disabled_text']};
            }}
            QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit, QDateTimeEdit {{
                background-color: {theme['base']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                padding: 3px;
                border-radius: 3px;
            }}
            QLabel, QCheckBox, QRadioButton {{
                color: {theme['text']};
            }}
            QTabWidget::pane {{
                border: 1px solid {theme['border']};
                background: {theme['window']};
            }}
            QTabBar::tab {{
                background: {theme['button']};
                color: {theme['button_text']};
                padding: 5px 10px;
                border: 1px solid {theme['border']};
                border-bottom: none;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
            }}
            QTabBar::tab:selected, QTabBar::tab:hover {{
                background: {theme['highlight']};
                color: {theme['highlighted_text']};
            }}
            QStatusBar {{
                background: {theme['button']};
                color: {theme['button_text']};
                border-top: 1px solid {theme['border']};
            }}
            QMenuBar {{
                background: {theme['button']};
                color: {theme['button_text']};
            }}
            QMenuBar::item:selected {{
                background: {theme['highlight']};
                color: {theme['highlighted_text']};
            }}
            QMenu {{
                background: {theme['button']};
                color: {theme['button_text']};
                border: 1px solid {theme['border']};
            }}
            QMenu::item:selected {{
                background: {theme['highlight']};
                color: {theme['highlighted_text']};
            }}
            QProgressBar {{
                border: 1px solid {theme['border']};
                border-radius: 3px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {theme['highlight']};
                width: 10px;
                margin: 0.5px;
            }}
            QTableWidget, QTableCornerButton::section, QHeaderView::section {{
                background: {theme['base']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                padding: 3px;
            }}
            QTableWidget::item {{
                padding: 3px;
            }}
            QTableWidget::item:selected {{
                background: {theme['highlight']};
                color: {theme['highlighted_text']};
            }}
            QToolTip {{
                background-color: {theme['tooltip_base']};
                color: {theme['tooltip_text']};
                border: 1px solid {theme['border']};
                padding: 3px;
            }}
        """)
        
        log.info(f"Applied theme: {theme_name}")
        return True
    
    def get_available_themes(self):
        """Return a list of available theme names."""
        return list(self.THEMES.keys())
    
    def get_current_theme(self):
        """Get the current theme name."""
        return self.current_theme

# Global theme manager instance
_theme_manager = None

def get_theme_manager(app=None):
    """Get or create the theme manager instance."""
    global _theme_manager
    if _theme_manager is None and app is not None:
        _theme_manager = ThemeManager(app)
    return _theme_manager
