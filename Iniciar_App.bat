@echo off
title V128 Downloader - Servidor
echo ============================================
echo   V128 Downloader - Iniciando servidor...
echo ============================================
echo.
echo Abre tu navegador en: http://localhost:5000
echo Para detener el servidor presiona CTRL+C
echo.

cd /d "%~dp0"
call "..\\.venv\Scripts\activate.bat"
python app.py

pause
