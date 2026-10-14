@echo off
title SLONE Global Media Engine - Windows
color 0E
echo =======================================================================
echo   👑 SLONE GLOBAL MEDIA ENGINE · WINDOWS EDITION
echo   Sede Central: Girona Tech Hub (Catalunya, Espana)
echo =======================================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] No se ha detectado Python en tu sistema Windows.
    echo Por favor, instala Python 3 desde https://www.python.org/downloads/
    echo (Asegurate de marcar la casilla "Add Python to PATH" durante la instalacion).
    pause
    exit /b 1
)

echo [1/2] Verificando dependencias graficas PyQt6...
python -c "import PyQt6" >nul 2>nul
if %errorlevel% neq 0 (
    echo [SLONE] Instalando dependencias de interfaz PyQt6 automaticamente...
    python -m pip install --quiet PyQt6
)

echo [2/2] Iniciando SLONE Global Media Engine...
start "" python "%~dp0..\..\app\slocast.py" %*
exit /b 0
