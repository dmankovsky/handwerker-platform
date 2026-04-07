from typing import Optional
from fastapi import Header, Request
from app.services.i18n_service import i18n, t


def get_language_from_header(accept_language: Optional[str] = Header(None)) -> str:
    """
    Extract language from Accept-Language header

    Args:
        accept_language: Accept-Language header value

    Returns:
        Language code (de or en)
    """
    if not accept_language:
        return i18n.default_language

    # Parse Accept-Language header (e.g., "en-US,en;q=0.9,de;q=0.8")
    languages = accept_language.split(",")

    for lang in languages:
        # Extract language code (e.g., "en" from "en-US" or "en;q=0.9")
        lang_code = lang.split(";")[0].strip().split("-")[0].lower()

        if lang_code in i18n.supported_languages:
            return lang_code

    return i18n.default_language


async def get_current_language(request: Request) -> str:
    """
    Get current language from request

    Priority:
    1. Query parameter (?lang=de)
    2. Accept-Language header
    3. Default language (de)
    """
    # Check query parameter
    lang = request.query_params.get("lang")
    if lang and lang in i18n.supported_languages:
        return lang

    # Check Accept-Language header
    accept_language = request.headers.get("accept-language")
    if accept_language:
        return get_language_from_header(accept_language)

    return i18n.default_language


class LocalizedResponse:
    """Helper class for creating localized API responses"""

    def __init__(self, language: str = "de"):
        self.language = language

    def translate(self, key: str, **kwargs) -> str:
        """Translate a key"""
        return t(key, self.language, **kwargs)

    def success(self, message_key: str, data=None, **kwargs):
        """Create a success response"""
        return {
            "success": True,
            "message": self.translate(message_key, **kwargs),
            "data": data
        }

    def error(self, message_key: str, **kwargs):
        """Create an error response"""
        return {
            "success": False,
            "message": self.translate(message_key, **kwargs)
        }
