# app/utils.py
# Utilidades comunes para rutas de la aplicación.
# Centraliza la lógica para que funcione tanto como .py como como .exe compilado.

import sys
import os


def get_base_dir() -> str:
    """
    Retorna el directorio raíz de la aplicación.

    - Cuando corre como .py: directorio padre de app/  (raíz del proyecto)
    - Cuando corre como .exe PyInstaller: directorio del ejecutable
    """
    if getattr(sys, "frozen", False):
        # PyInstaller congela el exe; el directorio del exe es la raíz
        return os.path.dirname(sys.executable)
    # __file__ apunta a app/utils.py → subimos dos niveles
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_locales_dir() -> str:
    """
    Retorna la carpeta de archivos de idioma.

    - En .exe: dentro de _MEIPASS (recursos empaquetados por PyInstaller)
    - En .py: subcarpeta locales/ en la raíz del proyecto
    """
    if getattr(sys, "frozen", False):
        # PyInstaller extrae datos adicionales en sys._MEIPASS
        return os.path.join(sys._MEIPASS, "locales")  # type: ignore[attr-defined]
    return os.path.join(get_base_dir(), "locales")


def get_config_path() -> str:
    """Retorna la ruta completa del archivo config.json (siempre junto al exe o .py)."""
    return os.path.join(get_base_dir(), "config.json")


def get_log_path() -> str:
    """Retorna la ruta completa del archivo log.txt (siempre junto al exe o .py)."""
    return os.path.join(get_base_dir(), "log.txt")


def get_icon_path() -> str:
    """
    Retorna la ruta del icono .ico si existe en la carpeta raíz.
    Busca el nombre exacto del icono incluido en el proyecto.
    """
    base = get_base_dir()
    # Nombre preferido del icono del proyecto
    preferred = os.path.join(base, "resetdisplay.ico")
    if os.path.exists(preferred):
        return preferred
    # Alternativa: cualquier .ico en la carpeta raíz
    for f in os.listdir(base):
        if f.lower().endswith(".ico"):
            return os.path.join(base, f)
    return ""
