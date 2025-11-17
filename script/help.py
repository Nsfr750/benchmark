"""
Help and documentation functionality for the Benchmark application.
"""
import webbrowser
import logging
from PySide6.QtWidgets import (QMessageBox, QTextBrowser, QVBoxLayout, QDialog,
                             QPushButton, QWidget, QHBoxLayout)
from PySide6.QtCore import Qt

from script.version import APP_NAME, GITHUB_URL, DISCORD_URL, __version__
from script.lang_mgr import get_language_manager

# Set up logger
log = logging.getLogger(__name__)

def show_help(parent=None):
    """Show the help dialog with documentation links."""
    try:
        # Create a simple dialog with a text browser
        class SimpleHelpDialog(QDialog):
            def __init__(self, parent=None):
                # Ensure parent is a QWidget or None
                if parent is not None and not isinstance(parent, QWidget):
                    parent = None
                    
                super().__init__(parent)
                app_name = APP_NAME if 'APP_NAME' in globals() else 'PyBench'
                self.setWindowTitle(f"{get_language_manager().get_text('help.title', default=f'{app_name} Help')}")
                self.setMinimumSize(600, 500)
                
                layout = QVBoxLayout(self)
                
                # Create text browser
                text_browser = QTextBrowser()
                text_browser.setOpenExternalLinks(True)
                text_browser.setHtml(get_help_text())
                
                # Add to layout
                layout.addWidget(text_browser)
                
                # Add close button
                close_btn = QPushButton(get_language_manager().get_text('buttons.close', default='Close'))
                close_btn.clicked.connect(self.accept)
                
                # Button layout for proper alignment
                btn_layout = QHBoxLayout()
                btn_layout.addStretch()
                btn_layout.addWidget(close_btn)
                
                layout.addLayout(btn_layout)
                
                # Handle links
                text_browser.anchorClicked.connect(self.on_link_clicked)
            
            def on_link_clicked(self, link):
                if link.toString() in (GITHUB_URL, DISCORD_URL):
                    webbrowser.open(link.toString())
        
        # Build the help text with proper HTML formatting
        def get_help_text():
            lang = get_language_manager()
            
            # Helper function to get text with fallback
            def get_text(key, default):
                return lang.get_text(key, default=default)
            
            # Build the HTML content in parts
            html_parts = []
            
            # Start of HTML with properly escaped CSS
            html_parts.append('''\
<!DOCTYPE html>
<html>
<head>
    <title>{0} Help</title>
    <style>\
        body {{\
            font-family: Arial, sans-serif;\
            line-height: 1.6;\
            max-width: 800px;\
            margin: 0 auto;\
            padding: 20px;\
            color: #7f8c8d;\
        }}\
        h1, h2, h3 {{\
            color: #3498db;\
        }}\
        h1 {{\
            border-bottom: 1px solid #eee;\
            padding-bottom: 10px;\
        }}\
        h2 {{\
            margin-top: 30px;\
            border-bottom: 1px solid #f0f0f0;\
            padding-bottom: 5px;\
        }}\
        code {{\
            background: #f5f5f5;\
            padding: 2px 5px;\
            border-radius: 3px;\
            font-family: monospace;
        }}\
        .section {{\
            margin: 20px 0;\
            padding: 15px;\
            border-radius: 5px;\
            border-left: 4px solid #3498db;\
        }}\
        .footer {{\
            margin-top: 30px;\
            padding-top: 15px;\
            border-top: 1px solid #eee;\
            font-size: 0.9em;\
            color: #7f8c8d;\
        }}\
    </style>
</head>
<body>
    <div class="container">
        <h1>{0}</h1>
            '''.format(get_text('help.title', '{0} Help'.format(APP_NAME))))
            
            # Getting Started section
            app_name = APP_NAME if 'APP_NAME' in globals() else 'PyBench'
            welcome_msg = get_text(
                'help.welcome',
                f'Welcome to {app_name}! This application allows you to benchmark your system\'s performance using the benchmark.'
            )
            html_parts.append('''
        <h2>{0}</h2>
        <p>{1}</p>
            '''.format(
                get_text('help.getting_started', 'Getting Started'),
                welcome_msg
            ))
            
            # How to Use section
            html_parts.append('''
        <h2>{0}</h2>
        <ol>
            <li>{1}</li>
            <li>{2}</li>
            <li>{3}</li>
            <li>{4}</li>
        </ol>
            '''.format(
                get_text('help.how_to_use', 'How to Use'),
                get_text('help.step1', 'Enter the number of iterations in the input field (default is 50,000)'),
                get_text('help.step2', 'Click the "Start Benchmark" button to begin the test'),
                get_text('help.step3', 'Wait for the benchmark to complete'),
                get_text('help.step4', 'View your results in the results section')
            ))
            
            # Understanding Results section
            html_parts.append('''
        <h2>{0}</h2>
        <p>{1}</p>
            '''.format(
                get_text('help.understanding_results', 'Understanding Results'),
                get_text('help.results_explanation', 'The benchmark measures how many "Pystones" your system can perform per second. Higher numbers indicate better performance.')
            ))
            
            # Need More Help section
            html_parts.append('''
        <h2>{0}</h2>
        <p>{1} <a href="{2}">GitHub repository</a> {3}</p>
        <p>{4} <a href="{5}">Discord server</a> {6}</p>
            '''.format(
                get_text('help.need_help', 'Need More Help?'),
                get_text('help.visit_github', 'Visit our'),
                GITHUB_URL,
                get_text('help.for_more_info', 'for more information and support.'),
                get_text('help.join_discord', 'Join our'),
                DISCORD_URL,
                get_text('help.community_support', 'for community support.')
            ))
            
            # Keyboard Shortcuts section
            html_parts.append('''
        <div class="section">
            <h3>{0}</h3>
            <ul>
                <li>{1}</li>
                <li>{2}</li>
                <li>{3}</li>
            </ul>
        </div>
            '''.format(
                get_text('help.keyboard_shortcuts', 'Keyboard Shortcuts'),
                get_text('help.shortcut_start', 'Ctrl+Enter: Start benchmark'),
                get_text('help.shortcut_stop', 'Esc: Stop benchmark'),
                get_text('help.shortcut_help', 'F1: Show this help')
            ))
            
            # Footer
            html_parts.append('''
        <div class="footer">
            &copy; 2025 Nsfr750 - GPLv3 License
        </div>
    </div>
</body>
</html>
            ''')
            
            # Join all parts and return
            return ''.join(html_parts).strip()
        
        # Create and show the dialog
        try:
            dialog = SimpleHelpDialog(parent)
            dialog.exec()
        except Exception as e:
            log.error(f"Error showing help: {str(e)}", exc_info=True)
            QMessageBox.critical(
                parent,
                get_language_manager().get_text('error_title', default='Error'),
                get_language_manager().get_text(
                    'help.error_loading',
                    default='Could not load help documentation.\n\nPlease visit the GitHub repository for documentation'
                )
            )
            webbrowser.open(GITHUB_URL)
        
    except Exception as e:
        # Fallback to a simple message box if the dialog fails
        log.error(f"Error showing help: {e}")       
        parent_widget = parent if isinstance(parent, QWidget) else None
        try:
            lang = get_language_manager()
            msg = QMessageBox(
                QMessageBox.Information,
                lang.get_text('help.title', 'Help'),
                lang.get_text('help.error_loading', 
                             'Could not load help documentation\n\nPlease visit the GitHub repository for documentation')
            )
            msg.exec()
        except Exception as e2:
            # If even the message box fails, just print the error
            print(f"Error showing help: {e}\nSecondary error: {e2}")
