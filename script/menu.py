"""
Menu bar and related functionality for the Pystone Benchmark application.
"""
import os
import importlib
from PySide6.QtWidgets import QMenuBar, QMenu, QStyle
from PySide6.QtGui import QKeySequence, QIcon, QAction, QActionGroup
from PySide6.QtCore import Qt, Signal, QObject

from script.version import APP_NAME, APP_DESCRIPTION, __version__
from script.lang_mgr import get_language_manager
# Import view_log directly since it doesn't cause circular imports
from script import view_log
from script.lang_mgr import LanguageManager

# Lazy import updates to avoid circular imports
updates = None
def get_updates_module():
    global updates
    if updates is None:
        updates = importlib.import_module('script.updates')
    return updates

# Lazy import settings to avoid circular imports
settings = None
def get_settings_module():
    global settings
    if settings is None:
        settings = importlib.import_module('script.settings')
    return settings

# Lazy import help to avoid circular imports
help = None
def get_help_module():
    global help
    if help is None:
        help = importlib.import_module('script.help')
    return help

# Lazy import sponsor to avoid circular imports
sponsor = None
def get_sponsor_module():
    global sponsor
    if sponsor is None:
        sponsor = importlib.import_module('script.sponsor')
    return sponsor

def create_menu_bar(parent):
    """Create and return the application menu bar."""
    menubar = QMenuBar(parent)
    
    # Get the application style for standard icons
    style = parent.style()
    
    # Get translations
    lang = get_language_manager()
    
    # File menu
    file_menu = menubar.addMenu(parent.tr("&File"))
    
    file_menu.addSeparator()
    
    # Exit action with icon
    exit_action = QAction(
        style.standardIcon(QStyle.SP_DialogCancelButton),  # Icon
        "E&xit",  # Text
        parent
    )
    exit_action.setShortcut(QKeySequence.Quit)
    exit_action.triggered.connect(parent.close)
    file_menu.addAction(exit_action)
    
    # Language menu
    language_menu = menubar.addMenu(parent.tr("&Language"))
    
    # Create an action group
    language_group = QActionGroup(parent)
    language_group.setExclusive(True)
    
    # Add language actions from available translations
    lang_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lang')
    if os.path.exists(lang_dir):
        # Create a temporary instance of LanguageManager to get language names
        temp_lang_manager = LanguageManager()
        for lang_file in sorted(os.listdir(lang_dir)):  # Sort languages alphabetically
            if lang_file.endswith('.json'):
                lang_code = os.path.splitext(lang_file)[0]
                # Get language name from the language manager
                lang_name = temp_lang_manager.get_language_name(lang_code)
                if lang_name:
                    action = QAction(lang_name, parent, checkable=True)
                    action.setData(lang_code)
                    # Check if this is the current language
                    if hasattr(parent, 'lang_manager') and parent.lang_manager.get_current_language() == lang_code:
                        action.setChecked(True)
                    # Use a lambda with a default argument to capture the current lang_code
                    action.triggered.connect(lambda checked, code=lang_code: parent.change_language(code))
                    language_group.addAction(action)
                    language_menu.addAction(action)
    
    # Tools menu
    tools_menu = menubar.addMenu(parent.tr("&Tools"))
    
    # Settings action with icon
    settings_text = lang.get_text('menu.settings', '&Settings...')
    settings_action = QAction(
        style.standardIcon(QStyle.SP_ComputerIcon),  # You might want to use a better icon
        settings_text,
        parent
    )
    settings_action.setStatusTip(lang.get_text('menu.settings_tooltip', 'Configure application settings'))
    settings_action.triggered.connect(lambda: get_settings_module().show_settings(parent))
    tools_menu.addAction(settings_action)

    # View Logs action with shortcut and icon
    view_logs_action = QAction(
        style.standardIcon(QStyle.SP_FileDialogListView),  # Icon
        lang.get_text('menu.view_logs', 'View &Logs'),  # Text
        parent
    )
    view_logs_action.setShortcut("Ctrl+L")
    view_logs_action.setStatusTip(lang.get_text('menu.view_logs_tooltip', 'View application logs (Ctrl+L)'))
    view_logs_action.triggered.connect(lambda: view_log.show_log_viewer(parent))
    tools_menu.addAction(view_logs_action)

     # Add a separator
    tools_menu.addSeparator()

    # Check for Updates action
    update_text = lang.get_text('menu.check_for_updates', 'Check for &Updates...')
    update_action = QAction(
        style.standardIcon(QStyle.SP_BrowserReload),  # Using refresh icon for updates
        update_text,
        parent
    )
    update_action.setStatusTip(lang.get_text('menu.check_for_updates_tooltip', 'Check for the latest version'))
    update_action.triggered.connect(lambda: get_updates_module().check_for_updates(parent))
    tools_menu.addAction(update_action)

    # Add a separator before Help
    menubar.addSeparator()
    
    # Help menu
    help_text = lang.get_text('menu.help', default='&Help')
    help_menu = menubar.addMenu(help_text)
    
    # Help Contents action
    help_action = QAction(
        style.standardIcon(QStyle.SP_MessageBoxQuestion),  # Icon
        lang.get_text('menu.help_contents', '&Help Contents'),  # Text
        parent
    )
    help_action.triggered.connect(lambda: get_help_module().show_help(parent))
    help_action.setShortcut(QKeySequence.HelpContents)
    help_menu.addAction(help_action)
    
    # Add separator
    help_menu.addSeparator()
    
    # Support Development action with QR code
    support_action = QAction(
        style.standardIcon(QStyle.SP_DialogHelpButton),  # Using help icon as placeholder
        lang.get_text('menu.support', '&Support Development...'),
        parent
    )
    support_action.triggered.connect(lambda: get_sponsor_module().show_sponsor_dialog(parent))
    help_menu.addAction(support_action)
    
    # Add separator
    help_menu.addSeparator()
    
    # About action with icon
    about_text = lang.get_text('menu.about', default=f'&About {APP_NAME} {__version__}')
    about_action = QAction(
        style.standardIcon(QStyle.SP_MessageBoxInformation),  # Icon
        about_text,  # Text
        parent
    )
    about_action.triggered.connect(parent.show_about)
    help_menu.addAction(about_action)
    
    return menubar
