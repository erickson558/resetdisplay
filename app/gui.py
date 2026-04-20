# app/gui.py
# Interfaz gráfica principal de ResetDisplay usando CustomTkinter.
# Separa completamente la lógica de presentación del backend (core.py).
# Diseño moderno, no bloqueante y con persistencia de configuración.

import os
import sys
import tkinter as tk
from typing import Optional

import customtkinter as ctk

from app import __author__, __version__, __year__
from app.config import load_config, save_config
from app.core import restart_explorer
from app.i18n import available_languages, load_language, t
from app.logger import logger
from app.utils import get_icon_path

# ── Constantes de la aplicación ───────────────────────────────────────────────
APP_NAME = "ResetDisplay"

# Mapeo código → nombre visible en el selector de idioma
_LANG_DISPLAY: dict = {
    "es": "🇪🇸  Español",
    "en": "🇺🇸  English",
}
_LANG_REVERSE: dict = {v: k for k, v in _LANG_DISPLAY.items()}


# ══════════════════════════════════════════════════════════════════════════════
class ResetDisplayApp(ctk.CTk):
    """
    Ventana principal de la aplicación.

    Responsabilidades:
        - Construir y mostrar la GUI
        - Leer/guardar configuración en config.json
        - Delegar la lógica de reinicio a core.restart_explorer()
        - Gestionar el countdown de autocierre
        - Mantener la GUI fluida (sin freeze) mediante callbacks del hilo worker
    """

    def __init__(self) -> None:
        super().__init__()

        # ── Cargar configuración y activar idioma ──────────────────────────
        self._cfg = load_config()
        load_language(self._cfg.get("language", "es"))

        # ── Aplicar tema antes de crear widgets ───────────────────────────
        ctk.set_appearance_mode(self._cfg.get("theme", "dark"))
        ctk.set_default_color_theme("blue")

        # ── Estado interno ─────────────────────────────────────────────────
        self._is_running:       bool = False   # True mientras se reinicia explorer
        self._countdown_active: bool = False   # True mientras el countdown está activo
        self._countdown_value:  int  = 0       # Segundos restantes para autocierre

        # ── Construir la interfaz ──────────────────────────────────────────
        self._setup_window()
        self._create_menu()
        self._create_widgets()
        self._restore_window_position()

        # ── Comportamiento automático al arrancar ──────────────────────────
        if self._cfg.get("auto_start", False):
            # Pequeño delay para que la ventana se muestre primero
            self.after(500, self._execute_restart)

        if self._cfg.get("auto_close", False):
            self._start_countdown()

        logger.info(f"{APP_NAME} v{__version__} iniciado")

    # ══════════════════════════════════════════════════════════════════════════
    #  CONSTRUCCIÓN DE LA VENTANA
    # ══════════════════════════════════════════════════════════════════════════

    def _setup_window(self) -> None:
        """Propiedades básicas de la ventana: título, tamaño, icono y atajos."""
        self.title(f"{APP_NAME}  v{__version__}")

        w = self._cfg.get("window_width",  440)
        h = self._cfg.get("window_height", 540)
        self.geometry(f"{w}x{h}")
        self.minsize(380, 480)

        # Icono — busca cualquier .ico en la carpeta raíz del proyecto
        icon = get_icon_path()
        if icon:
            try:
                self.iconbitmap(icon)
            except Exception:
                pass   # Si el icono falla, la app continúa sin él

        # Interceptar el cierre de ventana para guardar estado
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # ── Atajos de teclado globales ────────────────────────────────────
        self.bind("<Control-r>", lambda _e: self._execute_restart())   # Ctrl+R
        self.bind("<F5>",        lambda _e: self._execute_restart())   # F5
        self.bind("<Control-q>", lambda _e: self._on_close())          # Ctrl+Q
        self.bind("<F1>",        lambda _e: self._show_about())        # F1

    def _create_menu(self) -> None:
        """Barra de menús: Archivo | Ver | Ayuda."""
        menubar = tk.Menu(self)

        # ── Menú Archivo ──────────────────────────────────────────────────
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(
            label=t("menu_restart"),
            command=self._execute_restart,
            accelerator="Ctrl+R / F5",
        )
        file_menu.add_separator()
        file_menu.add_command(
            label=t("menu_exit"),
            command=self._on_close,
            accelerator="Ctrl+Q",
        )
        menubar.add_cascade(label=t("menu_file"), menu=file_menu)

        # ── Menú Ver ──────────────────────────────────────────────────────
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(
            label=t("menu_theme_dark"),
            command=lambda: self._change_theme("dark"),
        )
        view_menu.add_command(
            label=t("menu_theme_light"),
            command=lambda: self._change_theme("light"),
        )
        menubar.add_cascade(label=t("menu_view"), menu=view_menu)

        # ── Menú Ayuda ────────────────────────────────────────────────────
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(
            label=t("menu_about"),
            command=self._show_about,
            accelerator="F1",
        )
        menubar.add_cascade(label=t("menu_help"), menu=help_menu)

        self.config(menu=menubar)

    def _create_widgets(self) -> None:
        """Construye todos los widgets del cuerpo de la ventana."""
        # Frame raíz que ocupa toda la ventana
        root_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        root_frame.pack(fill="both", expand=True, padx=12, pady=12)

        self._create_header(root_frame)
        self._create_divider(root_frame)
        self._create_action_section(root_frame)
        self._create_settings_section(root_frame)
        self._create_language_section(root_frame)
        self._create_exit_button(root_frame)
        self._create_status_bar()   # Se ancla a la ventana, no al frame interno

    # ── Secciones de la GUI ───────────────────────────────────────────────────

    def _create_header(self, parent: ctk.CTkFrame) -> None:
        """Encabezado con icono emoji, nombre y versión de la app."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(10, 4))

        # Icono grande representativo de la pantalla
        ctk.CTkLabel(frame, text="🖥️", font=ctk.CTkFont(size=52)).pack()

        # Nombre de la aplicación en negrita
        ctk.CTkLabel(
            frame,
            text=APP_NAME,
            font=ctk.CTkFont(size=26, weight="bold"),
        ).pack()

        # Versión en texto secundario
        ctk.CTkLabel(
            frame,
            text=f"v{__version__}",
            font=ctk.CTkFont(size=12),
            text_color=("gray45", "gray65"),
        ).pack()

        # Descripción breve de para qué sirve la app
        ctk.CTkLabel(
            frame,
            text=t("app_description"),
            font=ctk.CTkFont(size=11),
            text_color=("gray45", "gray65"),
            wraplength=340,
        ).pack(pady=(6, 8))

    def _create_divider(self, parent: ctk.CTkFrame) -> None:
        """Línea horizontal separadora entre el header y las acciones."""
        ctk.CTkFrame(
            parent, height=2, fg_color=("gray75", "gray28")
        ).pack(fill="x", padx=10, pady=(0, 12))

    def _create_action_section(self, parent: ctk.CTkFrame) -> None:
        """Botón principal de reinicio con hint de atajos de teclado."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(pady=8)

        self._restart_btn = ctk.CTkButton(
            frame,
            text=t("btn_restart"),
            command=self._execute_restart,
            width=230,
            height=58,
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=14,
            fg_color=("#1a6cb5", "#155d9e"),
            hover_color=("#155d9e", "#104e87"),
        )
        self._restart_btn.pack()

        # Mostrar los atajos de teclado disponibles debajo del botón
        ctk.CTkLabel(
            frame,
            text="Ctrl+R   ·   F5",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray60"),
        ).pack(pady=(5, 0))

    def _create_settings_section(self, parent: ctk.CTkFrame) -> None:
        """Panel de configuración: checkboxes de auto-inicio y auto-cierre."""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=4, pady=8)

        ctk.CTkLabel(
            frame,
            text=t("settings_title"),
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(anchor="w", padx=14, pady=(10, 4))

        # ── Checkbox: Ejecutar automáticamente al abrir ───────────────────
        self._auto_start_var = ctk.BooleanVar(value=self._cfg.get("auto_start", False))
        ctk.CTkCheckBox(
            frame,
            text=t("cb_auto_start"),
            variable=self._auto_start_var,
            command=self._on_settings_changed,
        ).pack(anchor="w", padx=14, pady=3)

        # ── Checkbox: Auto-cerrar la app después de ejecutar ──────────────
        self._auto_close_var = ctk.BooleanVar(value=self._cfg.get("auto_close", False))
        ctk.CTkCheckBox(
            frame,
            text=t("cb_auto_close"),
            variable=self._auto_close_var,
            command=self._on_settings_changed,
        ).pack(anchor="w", padx=14, pady=3)

        # ── Campo: segundos para el autocierre ────────────────────────────
        time_row = ctk.CTkFrame(frame, fg_color="transparent")
        time_row.pack(fill="x", padx=14, pady=(3, 12))

        ctk.CTkLabel(
            time_row,
            text=t("label_close_time"),
            font=ctk.CTkFont(size=12),
        ).pack(side="left")

        self._close_time_var = tk.StringVar(
            value=str(self._cfg.get("auto_close_time", 60))
        )
        entry = ctk.CTkEntry(
            time_row,
            textvariable=self._close_time_var,
            width=62,
            height=28,
            justify="center",
        )
        entry.pack(side="left", padx=8)
        # Autoguardar cuando el usuario escribe en el campo
        entry.bind("<KeyRelease>", lambda _e: self._on_settings_changed())

        ctk.CTkLabel(
            time_row,
            text=t("label_seconds"),
            font=ctk.CTkFont(size=12),
        ).pack(side="left")

    def _create_language_section(self, parent: ctk.CTkFrame) -> None:
        """Selector de idioma con los idiomas disponibles en locales/."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=4, pady=4)

        ctk.CTkLabel(
            frame,
            text=t("label_language"),
            font=ctk.CTkFont(size=12),
        ).pack(side="left", padx=(10, 8))

        # Construir lista de opciones desde los archivos disponibles en locales/
        langs        = available_languages()
        lang_options = [_LANG_DISPLAY.get(l, l) for l in langs]

        current_display = _LANG_DISPLAY.get(self._cfg.get("language", "es"), "🇪🇸  Español")
        self._lang_var  = tk.StringVar(value=current_display)

        ctk.CTkOptionMenu(
            frame,
            values=lang_options,
            variable=self._lang_var,
            command=self._on_language_changed,
            width=150,
        ).pack(side="left")

    def _create_exit_button(self, parent: ctk.CTkFrame) -> None:
        """Botón Salir al pie del panel principal."""
        ctk.CTkButton(
            parent,
            text=t("btn_exit"),
            command=self._on_close,
            width=110,
            height=32,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            fg_color=("gray72", "gray28"),
            hover_color=("gray60", "gray22"),
            text_color=("gray10", "gray92"),
        ).pack(pady=(6, 10))

    def _create_status_bar(self) -> None:
        """
        Barra de estado en la parte inferior de la ventana.

        - Izquierda: mensaje de estado actual del proceso
        - Derecha:   countdown de autocierre (si está activo)
        """
        bar = ctk.CTkFrame(
            self,
            height=28,
            corner_radius=0,
            fg_color=("gray88", "gray18"),
        )
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)  # Mantener altura fija de 28 px

        # Mensaje de estado (izquierda)
        self._status_lbl = ctk.CTkLabel(
            bar,
            text=t("status_ready"),
            font=ctk.CTkFont(size=11),
            anchor="w",
        )
        self._status_lbl.pack(side="left", padx=10, fill="y")

        # Countdown (derecha) — vacío cuando no hay autocierre activo
        self._countdown_lbl = ctk.CTkLabel(
            bar,
            text="",
            font=ctk.CTkFont(size=11),
            anchor="e",
            text_color=("gray40", "gray65"),
        )
        self._countdown_lbl.pack(side="right", padx=10, fill="y")

    # ══════════════════════════════════════════════════════════════════════════
    #  ACCIONES
    # ══════════════════════════════════════════════════════════════════════════

    def _execute_restart(self) -> None:
        """
        Lanza el reinicio de explorer.exe si no hay uno en curso.
        Delega el trabajo al hilo en core.restart_explorer() para no congelar la GUI.
        """
        if self._is_running:
            return   # Ignorar doble click mientras ya está ejecutando

        self._is_running = True
        self._restart_btn.configure(state="disabled", text=t("btn_restarting"))
        logger.info("Usuario solicitó reinicio de Explorer")

        # Mapeo de estado interno → mensaje para la barra de estado
        _state_msg = {
            "killing":  t("status_killing"),
            "waiting":  t("status_waiting"),
            "starting": t("status_starting"),
        }

        def on_status(state: str) -> None:
            """Callback llamado desde el hilo worker para actualizar la GUI."""
            # after() es thread-safe en tkinter
            self.after(0, self._set_status, _state_msg.get(state, state))

        def on_complete(success: bool, msg: str) -> None:
            """Callback llamado cuando el hilo worker termina."""
            def _update() -> None:
                self._is_running = False
                self._restart_btn.configure(state="normal", text=t("btn_restart"))

                if success:
                    self._set_status(t("status_success"))
                    logger.info("Reinicio de Explorer completado exitosamente")
                    # Si auto-close está activo, iniciar countdown tras el éxito
                    if self._cfg.get("auto_close", False) and not self._countdown_active:
                        self._start_countdown()
                else:
                    # Mostrar mensaje de error específico en la barra de estado
                    error_key = f"status_error_{msg}"
                    self._set_status(t(error_key))
                    logger.error(f"Error al reiniciar Explorer: {msg}")

            self.after(0, _update)

        restart_explorer(on_status=on_status, on_complete=on_complete)

    def _set_status(self, message: str) -> None:
        """Actualiza el texto de la barra de estado."""
        self._status_lbl.configure(text=message)

    # ── Countdown de autocierre ───────────────────────────────────────────────

    def _start_countdown(self) -> None:
        """Inicia el temporizador de autocierre desde el valor configurado."""
        try:
            seconds = int(self._close_time_var.get())
        except (ValueError, AttributeError):
            seconds = 60   # Valor por defecto si el campo tiene texto inválido

        self._countdown_active = True
        self._countdown_value  = seconds
        self._tick_countdown()

    def _tick_countdown(self) -> None:
        """
        Se llama a sí misma cada segundo mediante after().
        Muestra el tiempo restante y cierra la app cuando llega a 0.
        """
        if not self._countdown_active:
            self._countdown_lbl.configure(text="")
            return

        if self._countdown_value <= 0:
            self._on_close()
            return

        # Actualizar el label de la derecha con los segundos restantes
        self._countdown_lbl.configure(
            text=f"{t('status_closing_in')} {self._countdown_value}s"
        )
        self._countdown_value -= 1
        self.after(1000, self._tick_countdown)   # Programar el siguiente tick

    def _stop_countdown(self) -> None:
        """Cancela el countdown de autocierre y limpia el label."""
        self._countdown_active = False
        self._countdown_lbl.configure(text="")

    # ── Callbacks de la GUI ───────────────────────────────────────────────────

    def _on_settings_changed(self) -> None:
        """Guarda la configuración cuando el usuario modifica cualquier ajuste."""
        self._cfg["auto_start"] = self._auto_start_var.get()
        self._cfg["auto_close"] = self._auto_close_var.get()

        try:
            self._cfg["auto_close_time"] = int(self._close_time_var.get())
        except ValueError:
            pass   # Dejar el valor anterior si el campo no es numérico

        save_config(self._cfg)

        # Sincronizar el countdown con el nuevo estado del checkbox
        if self._auto_close_var.get():
            if not self._countdown_active:
                self._start_countdown()
        else:
            self._stop_countdown()

    def _on_language_changed(self, selected: str) -> None:
        """Cambia el idioma y notifica al usuario que se aplicará en el menú al reabrir."""
        lang_code = _LANG_REVERSE.get(selected, "es")
        self._cfg["language"] = lang_code
        save_config(self._cfg)
        load_language(lang_code)
        # Informar en la barra de estado sin usar messagebox
        self._set_status(t("status_lang_changed"))
        logger.info(f"Idioma cambiado a: {lang_code}")

    def _change_theme(self, theme: str) -> None:
        """Cambia entre tema oscuro y claro en tiempo real."""
        ctk.set_appearance_mode(theme)
        self._cfg["theme"] = theme
        save_config(self._cfg)
        logger.debug(f"Tema cambiado a: {theme}")

    def _show_about(self) -> None:
        """
        Ventana modal 'Acerca de' con nombre, versión, autor y derechos.
        Usa CTkToplevel en lugar de messagebox para mantener el estilo moderno.
        """
        win = ctk.CTkToplevel(self)
        win.title(t("menu_about"))
        win.geometry("300x230")
        win.resizable(False, False)
        win.transient(self)   # Siempre encima de la ventana principal
        win.grab_set()         # Modal: bloquea interacción con la ventana principal

        # Centrar el diálogo sobre la ventana principal
        self.update_idletasks()
        px, py = self.winfo_x(), self.winfo_y()
        pw, ph = self.winfo_width(), self.winfo_height()
        win.geometry(f"+{px + pw//2 - 150}+{py + ph//2 - 115}")

        frame = ctk.CTkFrame(win, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=24, pady=20)

        ctk.CTkLabel(frame, text="🖥️",         font=ctk.CTkFont(size=40)).pack()
        ctk.CTkLabel(frame, text=APP_NAME,     font=ctk.CTkFont(size=20, weight="bold")).pack()
        ctk.CTkLabel(frame, text=f"v{__version__}", font=ctk.CTkFont(size=13)).pack()
        ctk.CTkLabel(
            frame,
            text=f"{t('about_created_by')} {__author__}",
            font=ctk.CTkFont(size=11),
        ).pack(pady=(12, 2))
        ctk.CTkLabel(
            frame,
            text=f"© {__year__} {t('about_rights')}",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60"),
        ).pack()

        ctk.CTkButton(
            frame, text="OK", command=win.destroy, width=80, height=30
        ).pack(pady=(16, 0))

    # ── Gestión del ciclo de vida de la ventana ───────────────────────────────

    def _restore_window_position(self) -> None:
        """Restaura la posición y tamaño guardados, verificando límites de pantalla."""
        x = self._cfg.get("window_x")
        y = self._cfg.get("window_y")

        if x is not None and y is not None:
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            # Asegurar que la ventana sea visible al menos parcialmente
            x = max(0, min(int(x), sw - 100))
            y = max(0, min(int(y), sh - 100))
            self.geometry(f"+{x}+{y}")
        else:
            # Primera ejecución: centrar la ventana
            self.update_idletasks()
            sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
            w,  h  = self.winfo_width(),       self.winfo_height()
            self.geometry(f"+{(sw - w)//2}+{(sh - h)//2}")

    def _save_window_state(self) -> None:
        """Persiste posición y tamaño actuales de la ventana antes de cerrar."""
        self._cfg["window_x"]      = self.winfo_x()
        self._cfg["window_y"]      = self.winfo_y()
        self._cfg["window_width"]  = self.winfo_width()
        self._cfg["window_height"] = self.winfo_height()
        save_config(self._cfg)

    def _on_close(self) -> None:
        """Cierre limpio de la aplicación: detiene el countdown y guarda el estado."""
        self._stop_countdown()
        self._save_window_state()
        logger.info(f"{APP_NAME} cerrado correctamente")
        self.destroy()
