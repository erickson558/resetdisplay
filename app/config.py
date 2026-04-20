# app/config.py
# Gestión de configuración persistente mediante config.json.
# Carga defaults al arrancar, fusiona con valores guardados y autoguarda
# cada vez que el usuario cambia algo en la GUI.

import json
import os
from typing import Any

from app.utils import get_config_path
from app.logger import logger

# ──────────────────────────────────────────────────────────────────────────────
# Valores por defecto — usados cuando config.json no existe o falta una clave
# ──────────────────────────────────────────────────────────────────────────────
DEFAULT_CONFIG: dict = {
    "language":        "es",    # Idioma de la interfaz
    "theme":           "dark",  # Tema visual: "dark" | "light"
    "auto_start":      False,   # Ejecutar el reinicio automáticamente al abrir
    "auto_close":      False,   # Cerrar la app automáticamente tras ejecutar
    "auto_close_time": 60,      # Segundos antes del cierre automático
    "window_x":        None,    # Posición X de la ventana (None = centrada)
    "window_y":        None,    # Posición Y de la ventana
    "window_width":    440,     # Ancho de la ventana en píxeles
    "window_height":   540,     # Alto de la ventana en píxeles
}


def load_config() -> dict:
    """
    Carga la configuración desde config.json.

    Si el archivo no existe o está corrupto, retorna una copia de DEFAULT_CONFIG.
    Siempre fusiona con defaults para garantizar que existan todas las claves,
    incluso cuando se añaden nuevas en versiones futuras.
    """
    config = DEFAULT_CONFIG.copy()
    path = get_config_path()

    if not os.path.exists(path):
        logger.info("config.json no encontrado, usando valores por defecto")
        return config

    try:
        with open(path, "r", encoding="utf-8") as fh:
            saved = json.load(fh)
        config.update(saved)   # Los valores guardados sobreescriben los defaults
        logger.debug(f"Configuración cargada desde {path}")
    except (json.JSONDecodeError, OSError) as exc:
        # Archivo corrupto o sin permisos → usar defaults y registrar el error
        logger.warning(f"No se pudo leer config.json ({exc}), usando defaults")

    return config


def save_config(config: dict) -> None:
    """
    Persiste el diccionario de configuración en config.json con indentación legible.
    No lanza excepciones para no interrumpir la GUI; solo registra errores.
    """
    path = get_config_path()
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(config, fh, indent=4, ensure_ascii=False)
        logger.debug(f"Configuración guardada en {path}")
    except (OSError, PermissionError) as exc:
        logger.error(f"No se pudo guardar config.json: {exc}")


def get(config: dict, key: str, default: Any = None) -> Any:
    """Atajo seguro para leer un valor del diccionario de configuración."""
    return config.get(key, default)
