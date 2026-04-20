# app/i18n.py
# Internacionalización: carga cadenas de texto desde archivos JSON en locales/.
# Soporta cambio de idioma en tiempo de ejecución sin reiniciar la app.

import json
import os
from typing import Dict

from app.utils import get_locales_dir
from app.logger import logger

# ── Estado interno del módulo ──────────────────────────────────────────────────
_cache:        Dict[str, Dict[str, str]] = {}  # Traducciones ya cargadas
_current_lang: str = "es"                      # Idioma activo por defecto


def load_language(lang: str) -> Dict[str, str]:
    """
    Carga las traducciones para el idioma dado y lo activa como idioma actual.

    Si el archivo no existe, hace fallback a español ("es").
    Cachea los resultados para no re-leer el disco en cada llamada a t().
    """
    global _current_lang

    if lang in _cache:
        # Ya está en caché, solo activar
        _current_lang = lang
        logger.debug(f"Idioma '{lang}' activado desde caché")
        return _cache[lang]

    lang_file = os.path.join(get_locales_dir(), f"{lang}.json")

    if not os.path.exists(lang_file):
        logger.warning(f"Archivo de idioma '{lang}.json' no encontrado, usando 'es'")
        lang = "es"
        lang_file = os.path.join(get_locales_dir(), "es.json")

    try:
        with open(lang_file, "r", encoding="utf-8") as fh:
            translations = json.load(fh)
        _cache[lang] = translations
        _current_lang = lang
        logger.info(f"Idioma '{lang}' cargado correctamente")
        return translations
    except (json.JSONDecodeError, OSError) as exc:
        logger.error(f"Error al cargar idioma '{lang}': {exc}")
        # Retornar dict vacío — t() usará la clave como texto de emergencia
        return {}


def t(key: str) -> str:
    """
    Retorna la traducción para la clave en el idioma activo.

    Si la clave no existe, retorna la propia clave (legible aunque no traducida).
    """
    # Asegurar que el idioma actual esté cargado
    if _current_lang not in _cache:
        load_language(_current_lang)

    return _cache.get(_current_lang, {}).get(key, key)


def available_languages() -> list:
    """
    Retorna lista de códigos de idioma disponibles basándose en los .json en locales/.
    Ejemplo: ["es", "en"]
    """
    locales_dir = get_locales_dir()
    if not os.path.isdir(locales_dir):
        return ["es"]
    return sorted(
        f.replace(".json", "")
        for f in os.listdir(locales_dir)
        if f.endswith(".json")
    )
