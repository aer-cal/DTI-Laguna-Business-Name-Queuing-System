@echo off
setlocal

cd /d "%~dp0"

echo Creating desktop shortcut for DTI Queue System...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0create_desktop_shortcut.ps1"

if errorlevel 1 (
    echo.
    echo Failed to create the desktop shortcut.
    pause
    exit /b 1
)

echo.
echo Desktop shortcut created successfully.
pause
