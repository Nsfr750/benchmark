"""
About dialog and related functionality for the Benchmark application.
"""
import os
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import Qt
from wand.image import Image as WandImage
from wand.drawing import Drawing
from wand.color import Color
from script.version import (
    __version__, __author__, __copyright__, APP_NAME, APP_DESCRIPTION,
    GITHUB_URL, PATREON_URL, PAYPAL_URL, DISCORD_URL, CREDITS
)
from script.lang_mgr import get_language_manager

def create_about_dialog(parent=None):
    """Create and return an about dialog."""
    lang = get_language_manager()
    
    # Format credits text with translations
    credits_text = []
    for role, name in CREDITS.items():
        role_key = 'credits.' + role.lower().replace(' ', '_')
        role_text = lang.get_text(role_key, default=role, name=name) if name else lang.get_text(role_key, default=role)
        # Add the role text with HTML formatting
        if name and '{}' not in role_text and ':' not in role_text:
            credits_text.append(f"<b>{role_text}:</b> {name}")
        else:
            credits_text.append(f"<b>{role_text}</b>")
    credits_text = "<br>".join(credits_text)
    
    about_text = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            h2 {{ color: #3498db; margin-bottom: 10px; margin-top: 0; }}
            h3 {{ color: #3498db; margin-top: 20px; }}
            a {{ color: #2980b9; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .version {{ color: #7f8c8d; font-style: italic; }}
            .copyright {{ font-size: small; color: white; align-items: center; }}
            .header {{ display: flex; align-items: center; gap: 20px; }}
            .logo {{ width: 185px; height: 96px; }}
            .content {{ flex: 1; }}
        </style>
    </head>
    <body>
    <div class="header">
        <img src="{os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets/logo.png')}" class="logo" alt="Logo">
        <div class="content">
            <h2>{APP_NAME} <span class="version">v{__version__}</span></h2>
            <p>{lang.get_text('about.description', default=APP_DESCRIPTION)}</p>
        </div>
    </div>
    
    <h3>{lang.get_text('about.credits', default='Credits')}</h3>
    <p>{credits_text}</p>
    
    <h3>{lang.get_text('about.connect', default='Connect')}</h3>
    <p>
    <a href='{GITHUB_URL}'>{lang.get_text('about.github', default='GitHub')}</a> | 
    <a href='{DISCORD_URL}'>{lang.get_text('about.discord', default='Discord')}</a> | 
    <a href='{PATREON_URL}'>{lang.get_text('about.support_on_patreon', default='Support on Patreon')}</a> | 
    <a href='{PAYPAL_URL}'>{lang.get_text('about.donate_via_paypal', default='Donate via PayPal')}</a>
    </p>
    
    <p class="copyright">{__copyright__}</p>
    </body>
    </html>
    """
    
    msg = QMessageBox(parent)
    msg.setWindowTitle(f"{lang.get_text('about.title', default='About')} {APP_NAME}")
    msg.setTextFormat(Qt.RichText)
    msg.setText(about_text)
    
    # Set standard buttons with translation
    ok_button = msg.addButton(QMessageBox.Ok)
    ok_button.setText(lang.get_text('buttons.ok', default='OK'))
    
    # Make links clickable
    msg.setTextInteractionFlags(Qt.LinksAccessibleByMouse | Qt.LinksAccessibleByKeyboard)
    
    # Ensure the dialog is large enough
    msg.setMinimumSize(600, 500)
    
    return msg

def show_about(parent=None):
    """Show the about dialog."""
    dialog = create_about_dialog(parent)
    return dialog.exec()
