"""
Language Manager for Benchmark
Handles loading and managing translations from JSON files.
"""
import json
import os
import sys
import logging
from typing import Dict, Optional, Any

# Set up logging
log = logging.getLogger(__name__)

class LanguageManager:
    """Manages application translations."""
    
    def __init__(self, lang_dir: str = 'lang', default_lang: str = 'en'):
        """Initialize the language manager.
        
        Args:
            lang_dir: Directory containing language files
            default_lang: Default language code (e.g., 'en', 'it')
        """
        # Handle paths in both development and compiled mode
        if getattr(sys, 'frozen', False):
            # Running in compiled mode
            base_path = os.path.dirname(sys.executable)
            self.lang_dir = os.path.join(base_path, lang_dir)
        else:
            # Running in development mode
            self.lang_dir = lang_dir
            
        self.default_lang = default_lang
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.current_lang = default_lang
        
        # Ensure the language directory exists
        os.makedirs(self.lang_dir, exist_ok=True)
        
        # Load the default language
        self.load_language(self.default_lang)
    
    def get_available_languages(self) -> list[str]:
        """Get list of available language codes.
        
        Returns:
            List of language codes (e.g., ['en', 'it'])
        """
        try:
            return [f[:-5] for f in os.listdir(self.lang_dir) 
                   if f.endswith('.json') and os.path.isfile(os.path.join(self.lang_dir, f))]
        except Exception as e:
            log.error(f"Error listing language files: {e}")
            return [self.default_lang]
    
    def load_language(self, lang_code: str) -> bool:
        """Load translations for the specified language code.

        Args:
            lang_code (str): The language code to load (e.g., 'en', 'it')

        Returns:
            bool: True if the language was loaded successfully, False otherwise
        """
        # Try to load the requested language file
        lang_file = os.path.join(self.lang_dir, f"{lang_code}.json")
        
        # In compiled mode, also check in the lang directory next to the executable
        if getattr(sys, 'frozen', False) and not os.path.exists(lang_file):
            base_path = os.path.dirname(sys.executable)
            alt_lang_dir = os.path.join(base_path, 'lang')
            alt_lang_file = os.path.join(alt_lang_dir, f"{lang_code}.json")
            if os.path.exists(alt_lang_file):
                lang_file = alt_lang_file
                self.lang_dir = alt_lang_dir  # Update lang_dir to the found location
                log.info(f"Using language file from: {alt_lang_dir}")
        
        if not os.path.exists(lang_file):
            log.error(f"Language file not found: {lang_file}")
            # Try to fall back to default language if current load fails
            if lang_code != self.default_lang:
                log.info(f"Falling back to default language: {self.default_lang}")
                return self.load_language(self.default_lang)
            return False

        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.translations[lang_code] = json.load(f)
            self.current_lang = lang_code
            log.info(f"Successfully loaded language: {lang_code}")
            return True
        except json.JSONDecodeError as e:
            log.error(f"Invalid JSON in language file {lang_file}: {e}")
        except Exception as e:
            log.error(f"Error loading language {lang_code} from {lang_file}: {e}")
            
        # If we get here, there was an error loading the file
        if lang_code != self.default_lang:
            log.info(f"Falling back to default language: {self.default_lang}")
            return self.load_language(self.default_lang)
        return False
    
    def get_text(self, key: str, default: Optional[str] = None, **kwargs) -> str:
        """Get a translated text by key with optional formatting.
        
        Args:
            key: Dot-separated key (e.g., 'app.title')
            default: Default text if key not found
            **kwargs: Formatting parameters
            
        Returns:
            Formatted translated text
        """
        if not self.translations.get(self.current_lang):
            if not self.load_language(self.default_lang):
                return default or key
        
        # Split the key into parts (e.g., 'app.title' -> ['app', 'title'])
        parts = key.split('.')
        value = self.translations[self.current_lang]
        
        try:
            # Navigate through the nested dictionary
            for part in parts:
                value = value[part]
            
            # If we have a string, format it with kwargs or positional args
            if isinstance(value, str):
                try:
                    # First try with kwargs if any provided
                    if kwargs:
                        return value.format(**kwargs)
                    # Then try with positional args if the string uses {0} format
                    elif '{0}' in value:
                        return value.format('')  # Pass empty string to avoid IndexError
                    return value
                except (KeyError, IndexError):
                    log.warning(f"Error formatting string: {value}")
                    return value
            return str(value)
        except (KeyError, AttributeError):
            log.warning(f"Translation key not found: {key}")
            return default or key
    
    def get_language_name(self, lang_code: str) -> str:
        """Get the display name of a language.
        
        Args:
            lang_code: Language code (e.g., 'en')
            
        Returns:
            Display name of the language
        """
        # Map of language codes to display names
        language_names = {
            'en': 'English',
            'it': 'Italiano',
            # Add more languages as needed
        }
        return language_names.get(lang_code, lang_code)
    
    def get_current_language(self) -> str:
        """Get the current language code.
        
        Returns:
            Current language code (e.g., 'en')
        """
        return self.current_lang
        
    def set_language(self, lang_code: str) -> bool:
        """Set the current language.
        
        Args:
            lang_code: Language code to set (e.g., 'en', 'it')
            
        Returns:
            bool: True if language was changed successfully, False otherwise
        """
        if lang_code == self.current_lang:
            return True  # Already using this language
            
        # Try to load the new language
        if self.load_language(lang_code):
            self.current_lang = lang_code
            return True
        return False


# Singleton instance
_lang_manager = None

def get_language_manager() -> LanguageManager:
    """Get the global language manager instance.
    
    Returns:
        LanguageManager: The global language manager
    """
    global _lang_manager
    if _lang_manager is None:
        _lang_manager = LanguageManager()
    return _lang_manager


def get_text(key: str, default: Optional[str] = None, **kwargs) -> str:
    """Convenience function to get a translated text.
    
    Args:
        key: Dot-separated key (e.g., 'app.title')
        default: Default text if key not found
        **kwargs: Formatting parameters
        
    Returns:
        Formatted translated text
    """
    return get_language_manager().get_text(key, default, **kwargs)
