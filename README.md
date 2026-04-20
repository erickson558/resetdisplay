# 🖥️ ResetDisplay

**ResetDisplay** es una aplicación de escritorio para Windows que reinicia el proceso `explorer.exe` de forma segura y rápida, solucionando problemas comunes de pantalla, barra de tareas y escritorio.

**Versión:** `v0.0.1` | **Autor:** Synyster Rick | **Licencia:** Apache 2.0

---

## ✨ Características

- **Reinicio seguro de Explorer** — equivalente a `taskkill /f /im explorer.exe` + `start explorer.exe`
- **GUI moderna** — interfaz con tema oscuro/claro usando CustomTkinter
- **No bloqueante** — la GUI responde mientras el proceso trabaja en segundo plano
- **Auto-inicio** — ejecuta el reinicio automáticamente al abrir la app
- **Auto-cierre** — cierra la app automáticamente con countdown visible
- **Multiidioma** — Español e Inglés incluidos
- **Persistencia** — guarda configuración y posición de ventana en `config.json`
- **Logging** — registro de eventos con timestamp en `log.txt`
- **Atajos de teclado** — `Ctrl+R` / `F5` reiniciar, `Ctrl+Q` salir, `F1` acerca de

---

## 📋 Requisitos

- Windows 10 / 11
- Python 3.9+ (solo para ejecución desde fuente)

---

## 🚀 Uso

### Opción A — Ejecutable (recomendado)

1. Descarga `ResetDisplay.exe` desde la sección [Releases](../../releases)
2. Colócalo en cualquier carpeta
3. Ejecuta directamente — no requiere instalación ni Python

### Opción B — Desde fuente

```bash
# Clonar el repositorio
git clone https://github.com/TU_USUARIO/resetdisplay.git
cd resetdisplay

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python main.py
```

---

## 🔨 Compilar a .exe

Ejecuta el script de build incluido:

```bat
build.bat
```

O manualmente con PyInstaller:

```bat
pyinstaller --onefile --windowed --icon=preferences-desktop-display_36059.ico ^
    --name=ResetDisplay --distpath=. --add-data "locales;locales" --clean main.py
```

El ejecutable `ResetDisplay.exe` quedará en la carpeta raíz del proyecto.

---

## 📁 Estructura del proyecto

```
resetdisplay/
├── main.py                  # Punto de entrada
├── build.bat                # Script de compilación
├── requirements.txt         # Dependencias Python
├── app/
│   ├── __init__.py          # Versión centralizada
│   ├── utils.py             # Utilidades de rutas
│   ├── config.py            # Gestión de config.json
│   ├── logger.py            # Sistema de logging
│   ├── i18n.py              # Internacionalización
│   ├── core.py              # Backend: reinicio de Explorer
│   └── gui.py               # Frontend: interfaz gráfica
├── locales/
│   ├── es.json              # Textos en Español
│   └── en.json              # Textos en English
└── .github/
    └── workflows/
        └── release.yml      # CI/CD: build + release automático
```

---

## ⌨️ Atajos de teclado

| Atajo        | Acción                  |
|-------------|-------------------------|
| `Ctrl+R`    | Reiniciar Explorer      |
| `F5`        | Reiniciar Explorer      |
| `Ctrl+Q`    | Salir                   |
| `F1`        | Acerca de               |

---

## 📦 Versionado

Se usa **versionado semántico** `Vx.x.x`:

| Tipo    | Cuándo usarlo                                              |
|---------|-----------------------------------------------------------|
| `patch` | Corrección de bugs, ajustes menores (0.0.1 → 0.0.2)      |
| `minor` | Nueva funcionalidad sin romper compatibilidad (0.0.1 → 0.1.0) |
| `major` | Cambios grandes o ruptura de compatibilidad (0.1.0 → 1.0.0) |

La versión se define en `app/__init__.py` y se propaga automáticamente a la GUI, los tags y los releases de GitHub.

---

## 🔄 Flujo de release (paso a paso)

```bash
# 1. Inicializar Git (primera vez)
git init
git add .
git commit -m "feat: initial release v0.0.1 - ResetDisplay app"

# 2. Crear repositorio público en GitHub
gh repo create resetdisplay --public --source=. --remote=origin --push

# 3. Para versiones futuras — actualizar versión en app/__init__.py, luego:
git add .
git commit -m "feat: descripción del cambio"
git push origin main
# GitHub Actions crea el release automáticamente

# 4. (Opcional) Crear tag manualmente
git tag -a v0.0.1 -m "Release v0.0.1"
git push origin v0.0.1
```

---

## 📝 Licencia

Apache License 2.0 — ver [LICENSE](LICENSE)

© 2026 Synyster Rick. Derechos Reservados.
