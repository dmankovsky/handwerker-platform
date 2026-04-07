import json
import os
from typing import Optional, Dict, Any
from pathlib import Path


class I18nService:
    """Service for handling internationalization (i18n)"""

    def __init__(self):
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.default_language = "de"  # German is default for German market
        self.supported_languages = {"de", "en"}
        self._load_translations()

    def _load_translations(self):
        """Load all translation files"""
        translations_dir = Path(__file__).parent.parent / "translations"

        for lang in self.supported_languages:
            translation_file = translations_dir / f"{lang}.json"
            if translation_file.exists():
                with open(translation_file, "r", encoding="utf-8") as f:
                    self.translations[lang] = json.load(f)
            else:
                print(f"Warning: Translation file for {lang} not found")
                self.translations[lang] = {}

    def translate(self, key: str, language: Optional[str] = None, **kwargs) -> str:
        """
        Translate a key to the specified language

        Args:
            key: Translation key (e.g., "errors.not_found")
            language: Language code (de/en). Uses default if not specified
            **kwargs: Variables to interpolate in the translation

        Returns:
            Translated string
        """
        if language not in self.supported_languages:
            language = self.default_language

        # Navigate nested keys (e.g., "errors.not_found")
        keys = key.split(".")
        value = self.translations.get(language, {})

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                value = None
                break

        # If translation not found, try English as fallback
        if value is None and language != "en":
            value = self.translations.get("en", {})
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                else:
                    value = None
                    break

        # If still not found, return the key itself
        if value is None:
            return key

        # Interpolate variables
        if kwargs and isinstance(value, str):
            try:
                value = value.format(**kwargs)
            except KeyError:
                pass

        return str(value)

    def get_supported_languages(self) -> list:
        """Get list of supported language codes"""
        return list(self.supported_languages)


# Global i18n service instance
i18n = I18nService()


def t(key: str, language: Optional[str] = None, **kwargs) -> str:
    """Shorthand for translate"""
    return i18n.translate(key, language, **kwargs)
