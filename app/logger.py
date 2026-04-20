# app/logger.py
# Configura el sistema de logging de la aplicación.
# Escribe en log.txt con timestamps y niveles, y opcionalmente en consola.

import logging
import os
from app.utils import get_log_path

# ──────────────────────────────────────────────────────────────────────────────
# Formato de log: fecha+hora | nivel | módulo | mensaje
# ──────────────────────────────────────────────────────────────────────────────
_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(module)-12s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(name: str = "resetdisplay") -> logging.Logger:
    """
    Crea y configura el logger principal.

    - FileHandler  → log.txt en la carpeta de la app (DEBUG en adelante)
    - StreamHandler→ consola (INFO en adelante, útil durante desarrollo)
    """
    logger = logging.getLogger(name)

    # Evitar agregar handlers duplicados si se llama varias veces
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT)

    # ── Handler de archivo ──────────────────────────────────────────────────
    try:
        file_handler = logging.FileHandler(get_log_path(), encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except (OSError, PermissionError) as exc:
        # Si no se puede escribir el log, continuar sin crashear la app
        print(f"[WARN] No se pudo crear log.txt: {exc}")

    # ── Handler de consola (solo en desarrollo, no en exe sin consola) ───────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# Logger global — importar en el resto de módulos con:
#   from app.logger import logger
logger = setup_logger()
