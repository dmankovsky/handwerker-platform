from typing import Dict, List
from fastapi import APIRouter, Depends, Request
from app.services.i18n_service import i18n, t
from app.core.i18n import get_current_language

router = APIRouter(prefix="/api/i18n", tags=["Internationalization"])


@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "supported_languages": i18n.get_supported_languages(),
        "default_language": i18n.default_language
    }


@router.get("/translations/{category}")
async def get_translations(
    category: str,
    request: Request,
    language: str = Depends(get_current_language)
):
    """
    Get translations for a specific category

    Categories: common, errors, auth, booking, craftsman, payment, review, verification, messages, notifications, email, date, general
    """
    translations = i18n.translations.get(language, {})
    category_translations = translations.get(category, {})

    if not category_translations:
        return {
            "language": language,
            "category": category,
            "translations": {},
            "message": "Category not found"
        }

    return {
        "language": language,
        "category": category,
        "translations": category_translations
    }


@router.get("/translations")
async def get_all_translations(
    request: Request,
    language: str = Depends(get_current_language)
):
    """Get all translations for the current language"""
    return {
        "language": language,
        "translations": i18n.translations.get(language, {})
    }


@router.get("/translate/{key}")
async def translate_key(
    key: str,
    request: Request,
    language: str = Depends(get_current_language)
):
    """
    Translate a specific key

    Example: /api/i18n/translate/common.welcome?lang=de
    """
    translation = t(key, language)

    return {
        "key": key,
        "language": language,
        "translation": translation
    }
