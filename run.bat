@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
    if errorlevel 1 (
        pause
        exit /b 1
    )
)
set ENABLE_DEBUG_TOOLBAR=0
if /i "%~1"=="debug" set ENABLE_DEBUG_TOOLBAR=1
echo Open http://127.0.0.1:8000/ in your browser.
echo Stop the server with Ctrl+C.
.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
pause
