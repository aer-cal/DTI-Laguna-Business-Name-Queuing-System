@echo off
REM DTI Laguna Queue Management System
REM Starts Operator Panel (which automatically starts Client Display)

cd /d "%~dp0"

echo ======================================
echo DTI LAGUNA QUEUE MANAGEMENT SYSTEM
echo ======================================
echo.
echo Starting Queue System...
echo Operator Panel will launch automatically.
echo Client Display will open in a separate window.
echo.

REM Start Operator Panel - it will automatically spawn Client Display
set PYTHONIOENCODING=utf-8
.venv\Scripts\python.exe queue_system.py

pause
