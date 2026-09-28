@echo off
echo Starting ANOMYMOUS...
:: Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

:: Set common settings
set PYTHON=python
set HOST=127.0.0.1
set PORT=8000

echo [INFO] Starting ANOMYMOUS server...
echo [INFO] Server listening at: http://%HOST%:%PORT%
echo [INFO] Press CTRL+C to stop the server...
echo.

:: Start the server
"%PYTHON%" server.py

if %errorlevel% neq 0 (
    echo [ERROR] Server failed to start
)
pause