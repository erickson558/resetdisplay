# main.py
# Punto de entrada de la aplicación ResetDisplay.
# Agrega la raíz del proyecto al sys.path para que los módulos en app/
# se resuelvan correctamente tanto en .py como en el exe compilado.

import os
import sys

# Forzar UTF-8 en la salida estándar para que los emojis no rompan en consolas Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Garantizar que la raíz del proyecto esté en el path de importación
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.logger import logger
from app.gui import ResetDisplayApp


def main() -> None:
    """Inicializa y ejecuta el loop principal de la GUI."""
    logger.info("Iniciando ResetDisplay...")
    try:
        app = ResetDisplayApp()
        app.mainloop()
    except Exception as exc:
        # Capturar errores fatales antes de que crasheen silenciosamente en el exe
        logger.critical(f"Error fatal al iniciar la aplicación: {exc}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
