@echo off
echo Starting ANOMYMOUS...
setlocal enabledelayedexpansion

:: Known Python installation path (Windows)
set "PYTHON_PATH=C:\Users\ALI HAIDER\AppData\Local\Programs\Python\Python313\python.exe"
set "FALLBACK_PYTHON=python"

:: Check if known Python exists, else fall back to PATH python
if exist "%PYTHON_PATH%" (
    set "PYTHON=%PYTHON_PATH%"
    echo [INFO] Using known Python: %PYTHON_PATH%
) else (
    set "PYTHON=%FALLBACK_PYTHON%"
    echo [INFO] Using PATH Python: %FALLBACK_PYTHON%
)

:: Validate Python
"%PYTHON%" --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Tried: %PYTHON_PATH%
    pause
    exit /b 1
)

:: Set common settings
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