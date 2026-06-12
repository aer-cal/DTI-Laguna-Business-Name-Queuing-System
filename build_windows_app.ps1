$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

if (-not (Test-Path '.venv\Scripts\python.exe')) {
    throw 'Virtual environment not found. Create .venv first.'
}

$python = Join-Path $repoRoot '.venv\Scripts\python.exe'

& $python -m pip install --upgrade pyinstaller

Remove-Item -Recurse -Force 'build', 'dist' -ErrorAction SilentlyContinue

& $python -m PyInstaller --noconfirm --clean --onefile --windowed --icon 'web/DTI_Shortcut.ico' --name 'queue_system' --add-data 'web;web' 'queue_system.py'
& $python -m PyInstaller --noconfirm --clean --onefile --windowed --icon 'web/DTI_Shortcut.ico' --name 'client_display' --add-data 'web;web' 'client_display.py'

& powershell -NoProfile -ExecutionPolicy Bypass -File 'create_desktop_shortcut.ps1'

Write-Host ''
Write-Host 'Build complete.'
Write-Host 'Look in dist for queue_system.exe and client_display.exe.'
