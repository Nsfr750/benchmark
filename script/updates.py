"""
Update checker for Benchmark.
"""
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError
from PySide6.QtWidgets import QMessageBox, QApplication
from PySide6.QtCore import QThread, Signal, QObject

from script.version import __version__
from script.lang_mgr import get_language_manager

# Set up logging
logger = logging.getLogger(__name__)

# Constants
UPDATE_CHECK_URL = "https://api.github.com/repos/Nsfr750/benchmark/releases/latest"
# Ensure config directory exists
CONFIG_DIR = Path(__file__).parent.parent / "config"
CONFIG_DIR.mkdir(exist_ok=True)
CACHE_FILE = CONFIG_DIR / "updates.json"
CACHE_EXPIRY_DAYS = 1

# Global instance of the update checker
_update_checker = None

def get_updates_module():
    """Get the update checker instance."""
    global _update_checker
    if _update_checker is None or not _update_checker.parent():
        _update_checker = UpdateChecker()
    return _update_checker

class UpdateChecker(QObject):
    """Handles checking for application updates."""
    update_available = Signal(str, str)  # version, url
    no_update = Signal()
    error = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread = None
        self._is_shutting_down = False
        self._update_checker = None  # Reference to the UpdateChecker instance

    def check_for_updates(self, force=False):
        """Check for updates, using cache unless forced."""
        if self._is_shutting_down:
            return
            
        if not force and self._is_cache_valid():
            logger.debug("Using cached update information")
            cache = self._load_cache()
            if cache.get("update_available", False):
                self.update_available.emit(cache["latest_version"], cache["url"])
                return
            self.no_update.emit()
            return

        # Create a thread to perform the update check
        self._cleanup_thread()
            
        self.thread = UpdateCheckThread()
        self.thread.finished.connect(self._on_update_check_complete)
        self.thread.start()
        
    def _cleanup_thread(self):
        """Safely clean up any existing thread."""
        if hasattr(self, 'thread') and self.thread is not None:
            if self.thread.isRunning():
                self.thread.requestInterruption()
                self.thread.quit()
                if not self.thread.wait(1000):  # Wait up to 1 second
                    self.thread.terminate()
                    self.thread.wait()
            self.thread.deleteLater()
            self.thread = None
            
    def shutdown(self):
        """Clean up resources before shutting down."""
        self._is_shutting_down = True
        self._cleanup_thread()

    def _on_update_check_complete(self, result):
        """Handle the result of the update check."""
        if isinstance(result, Exception):
            self.error.emit(str(result))
            return
            
        latest_version, url = result
        if self._is_newer_version(latest_version):
            self._save_cache(latest_version, url, True)
            self.update_available.emit(latest_version, url)
        else:
            self._save_cache(latest_version, url, False)
            self.no_update.emit()

    def _is_cache_valid(self):
        """Check if the cache is still valid."""
        if not CACHE_FILE.exists():
            return False
            
        try:
            cache = json.loads(CACHE_FILE.read_text(encoding='utf-8'))
            last_check = datetime.fromisoformat(cache["last_check"])
            return (datetime.now() - last_check) < timedelta(days=CACHE_EXPIRY_DAYS)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning("Invalid cache file: %s", str(e))
            return False

    def _load_cache(self):
        """Load update information from cache."""
        try:
            return json.loads(CACHE_FILE.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_cache(self, version, url, update_available):
        """Save update information to cache."""
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        cache = {
            "last_check": datetime.now().isoformat(),
            "latest_version": version,
            "url": url,
            "update_available": update_available
        }
        CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding='utf-8')

    @staticmethod
    def _is_newer_version(version_str):
        """Check if the given version is newer than the current version."""
        try:
            from distutils.version import StrictVersion
            return StrictVersion(version_str) > StrictVersion(__version__)
        except (ValueError, AttributeError):
            # Fallback string comparison if version parsing fails
            return version_str > __version__


class UpdateCheckThread(QThread):
    """Thread for checking updates in the background."""
    finished = Signal(object)  # Emits either (version, url) or Exception

    def run(self):
        """Run the update check."""
        try:
            req = Request(UPDATE_CHECK_URL)
            req.add_header('Accept', 'application/vnd.github.v3+json')
            
            with urlopen(req, timeout=10) as response:
                if self.isInterruptionRequested():
                    return
                    
                data = json.loads(response.read().decode())
                
                if self.isInterruptionRequested():
                    return
                    
                latest_version = data["tag_name"].lstrip('v')
                url = data["html_url"]
                self.finished.emit((latest_version, url))
            
        except Exception as e:
            if not self.isInterruptionRequested():
                logger.error("Error checking for updates: %s", str(e))
                self.finished.emit(e)
                
    def stop(self):
        """Stop the thread safely."""
        self.requestInterruption()
        self.quit()
        self.wait()


def check_for_updates(parent, force=False):
    """
    Check for updates and show a message to the user.
    
    Args:
        parent: Parent widget for dialogs
        force: If True, ignore cache and force a check
    """
    lang = get_language_manager()
    app = QApplication.instance()
    
    def show_update_available(version, url):
        title = lang.get_text("updates.available_title", "Update Available")
        message = lang.get_text(
            "updates.available_message",
            f"A new version {version} is available!\n\n"
            f"Would you like to download it now?"
        )
        
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information)
        
        download_btn = msg_box.addButton(
            lang.get_text("updates.download", "&Download"), 
            QMessageBox.AcceptRole
        )
        msg_box.addButton(QMessageBox.Cancel)
        
        msg_box.exec()
        
        if msg_box.clickedButton() == download_btn:
            import webbrowser
            webbrowser.open(url)
    
    def show_no_updates():
        title = lang.get_text("updates.no_updates_title", "No Updates")
        message = lang.get_text(
            "updates.no_updates_message",
            "You're using the latest version of Benchmark."
        )
        QMessageBox.information(parent, title, message)
    
    def show_error(message):
        title = lang.get_text("updates.error_title", "Update Error")
        QMessageBox.warning(parent, title, str(message))
    
    # Create and configure the update checker
    checker = get_updates_module()
    checker.update_available.connect(show_update_available)
    checker.no_update.connect(show_no_updates)
    checker.error.connect(show_error)
    
    # Start the update check
    checker.check_for_updates(force=force)


def add_update_menu_item(tools_menu, parent):
    """Add the 'Check for Updates' menu item to the Tools menu."""
    lang = get_language_manager()
    
    update_action = parent.addAction(
        lang.get_icon("update"),  # You might want to add an update icon
        lang.get_text("menu.check_for_updates", "Check for &Updates...")
    )
    update_action.setStatusTip(
        lang.get_text("menu.check_for_updates_tooltip", "Check for the latest version")
    )
    update_action.triggered.connect(lambda: check_for_updates(parent))
    tools_menu.addAction(update_action)
    
    # Add a separator after the update item
    tools_menu.addSeparator()
    
    return update_action
