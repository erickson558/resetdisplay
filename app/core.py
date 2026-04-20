# app/core.py
# Backend: lógica para reiniciar el proceso explorer.exe de Windows.
# Se ejecuta en un hilo separado para no bloquear la interfaz gráfica.

import subprocess
import threading
import time
from typing import Callable, Optional

from app.logger import logger


def restart_explorer(
    on_status:   Optional[Callable[[str], None]]        = None,
    on_complete: Optional[Callable[[bool, str], None]]  = None,
) -> threading.Thread:
    """
    Reinicia explorer.exe en un hilo daemon para no bloquear la GUI.

    Flujo:
        1. taskkill /f /im explorer.exe  → fuerza el cierre del proceso
        2. sleep(1)                       → espera a que el SO libere recursos
        3. Popen explorer.exe            → inicia el explorador nuevamente

    Args:
        on_status:   Callback(estado:str)          — notifica progreso a la GUI.
                     Estados posibles: "killing" | "waiting" | "starting"
        on_complete: Callback(éxito:bool, msg:str) — notifica resultado final.
                     msg posibles: "success" | "timeout" | "not_found" | "error"

    Returns:
        El objeto Thread ya iniciado (daemon=True).
    """

    def _run() -> None:
        try:
            # ── Paso 1: Terminar explorer.exe ─────────────────────────────────
            logger.info("Iniciando reinicio de explorer.exe")
            _notify_status(on_status, "killing")

            result = subprocess.run(
                ["taskkill", "/f", "/im", "explorer.exe"],
                capture_output=True,   # Suprimir salida en pantalla
                text=True,
                timeout=10,            # No esperar más de 10 segundos
            )

            # returncode 0 = OK, 128 = proceso no existía (ambos aceptables)
            if result.returncode not in (0, 128):
                logger.warning(
                    f"taskkill finalizó con código inesperado: {result.returncode}"
                )
            else:
                logger.info("explorer.exe terminado correctamente")

            # ── Paso 2: Esperar a que el SO libere el proceso ─────────────────
            _notify_status(on_status, "waiting")
            time.sleep(1)

            # ── Paso 3: Lanzar explorer.exe nuevamente ────────────────────────
            _notify_status(on_status, "starting")

            subprocess.Popen(
                ["explorer.exe"],
                shell=False,     # Nunca usar shell=True con rutas fijas (riesgo de inyección)
                close_fds=True,  # No heredar descriptores de archivo de la app padre
            )

            logger.info("explorer.exe iniciado correctamente")
            _notify_complete(on_complete, True, "success")

        except subprocess.TimeoutExpired:
            logger.error("Timeout: taskkill tardó más de 10 segundos")
            _notify_complete(on_complete, False, "timeout")

        except FileNotFoundError as exc:
            logger.error(f"Ejecutable no encontrado: {exc}")
            _notify_complete(on_complete, False, "not_found")

        except Exception as exc:
            logger.error(f"Error inesperado al reiniciar explorer: {exc}")
            _notify_complete(on_complete, False, "error")

    # Hilo daemon: si la app se cierra, el hilo no bloquea la salida
    thread = threading.Thread(target=_run, daemon=True, name="ExplorerRestart")
    thread.start()
    return thread


# ── Helpers internos ────────────────────────────────────────────────────────────

def _notify_status(callback: Optional[Callable[[str], None]], state: str) -> None:
    """Llama al callback de estado solo si fue proporcionado."""
    if callback:
        callback(state)


def _notify_complete(
    callback: Optional[Callable[[bool, str], None]],
    success: bool,
    message: str,
) -> None:
    """Llama al callback de finalización solo si fue proporcionado."""
    if callback:
        callback(success, message)
