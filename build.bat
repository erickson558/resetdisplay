@echo off
REM build.bat — Compila ResetDisplay a un ejecutable .exe con PyInstaller
REM Ejecutar desde la raíz del proyecto: build.bat

echo ============================================================
echo  ResetDisplay — Build Script
echo ============================================================

REM Paso 1: Instalar/actualizar dependencias
echo [1/3] Instalando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Fallo al instalar dependencias.
    pause
    exit /b 1
)

REM Paso 2: Compilar con PyInstaller
REM   --onefile          : un solo .exe sin carpetas adicionales
REM   --windowed         : no abrir ventana de consola (modo GUI)
REM   --icon             : icono .ico del ejecutable
REM   --name             : nombre del ejecutable resultante
REM   --distpath=.       : dejar el .exe en la carpeta actual (raíz del proyecto)
REM   --add-data         : incluir la carpeta locales/ dentro del exe
REM   --clean            : limpiar caché de builds anteriores
echo [2/3] Compilando a .exe...
pyinstaller ^
    --onefile ^
    --windowed ^
    --icon=preferences-desktop-display_36059.ico ^
    --name=ResetDisplay ^
    --distpath=. ^
    --add-data "locales;locales" ^
    --clean ^
    main.py

if %errorlevel% neq 0 (
    echo ERROR: Fallo la compilacion con PyInstaller.
    pause
    exit /b 1
)

REM Paso 3: Limpiar artefactos temporales de PyInstaller
echo [3/3] Limpiando artefactos temporales...
if exist build\ rmdir /s /q build
if exist ResetDisplay.spec del /f /q ResetDisplay.spec

echo.
echo ============================================================
echo  Build completado: ResetDisplay.exe creado en esta carpeta
echo ============================================================
pause
