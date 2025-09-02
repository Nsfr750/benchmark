"""
Test script for the TestMenu class.
"""
import sys
import unittest
from unittest.mock import MagicMock, patch

from PySide6.QtWidgets import QApplication

# Add the script directory to the Python path
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestTestMenu(unittest.TestCase):
    """Test cases for the TestMenu class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment."""
        # Create a QApplication instance if one doesn't already exist
        cls.app = QApplication.instance() or QApplication(sys.argv)
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        from script.test_menu import TestMenu
        self.test_menu = TestMenu()
    
    def test_menu_initialization(self):
        """Test that the menu initializes correctly."""
        self.assertIsNotNone(self.test_menu)
        self.assertEqual(self.test_menu.title(), "&Test")
    
    def test_menu_actions_exist(self):
        """Test that all menu actions are created."""
        actions = self.test_menu.actions()
        action_texts = [action.text() for action in actions if action.text()]
        
        expected_actions = [
            "System Information",
            "Run Benchmark",
            "Hardware Monitor",
            "View Logs",
            "View History",
            "Export Results...",
            "Import Results...",
            "Test Action"
        ]
        
        for expected in expected_actions:
            self.assertIn(expected, "".join(action_texts))
    
    @patch('script.test_menu.QMessageBox.critical')
    @patch('script.test_menu.import_module', side_effect=ImportError("Test error"))
    def test_show_system_info_error_handling(self, mock_import, mock_critical):
        """Test error handling in show_system_info method."""
        self.test_menu.show_system_info()
        mock_critical.assert_called_once()
    
    @patch('script.test_menu.QMessageBox.critical')
    @patch('script.test_menu.import_module', side_effect=ImportError("Test error"))
    def test_run_benchmark_tests_error_handling(self, mock_import, mock_critical):
        """Test error handling in run_benchmark_tests method."""
        self.test_menu.run_benchmark_tests()
        mock_critical.assert_called_once()
    
    def tearDown(self):
        """Clean up after each test method."""
        self.test_menu.deleteLater()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all test methods have run."""
        if cls.app:
            cls.app.quit()

if __name__ == "__main__":
    unittest.main()
