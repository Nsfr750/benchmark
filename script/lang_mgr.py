"""
Language Manager for Benchmark
Handles loading and managing translations from the translations module.
"""
import logging
from typing import Dict, Optional, Any
from . import translations

# Set up logging
log = logging.getLogger(__name__)

class LanguageManager:
    """Manages application translations."""
    
    def __init__(self, default_lang: str = 'en'):
        """Initialize the language manager.
        
        Args:
            default_lang: Default language code (e.g., 'en', 'it')
        """
        self.default_lang = default_lang
        self.current_lang = default_lang
        self.translations = {}
        
        # Load the default language
        self.load_language(self.default_lang)
    
    def get_available_languages(self) -> list[str]:
        """Get list of available language codes.
        
        Returns:
            List of language codes (e.g., ['en', 'it'])
        """
        return list(translations.TRANSLATIONS.keys())
    
    def load_language(self, lang_code: str) -> bool:
        """Load translations for the specified language code.

        Args:
            lang_code (str): The language code to load (e.g., 'en', 'it')

        Returns:
            bool: True if the language was loaded successfully, False otherwise
        """
        if lang_code not in translations.TRANSLATIONS:
            log.error(f"Language not supported: {lang_code}")
            if lang_code != self.default_lang:
                log.info(f"Falling back to default language: {self.default_lang}")
                return self.load_language(self.default_lang)
            return False
            
        self.current_lang = lang_code
        log.info(f"Successfully loaded language: {lang_code}")
        return True
    
    def get_text(self, key: str, default: Optional[str] = None, **kwargs) -> str:
        """Get a translated text.
        
        Args:
            key: Dot-separated key (e.g., 'app.title')
            default: Default text if key not found
            **kwargs: Formatting parameters
            
        Returns:
            Formatted translated text
        """
        return translations.get_translation(self.current_lang, key, default or key).format(**kwargs)
    
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
