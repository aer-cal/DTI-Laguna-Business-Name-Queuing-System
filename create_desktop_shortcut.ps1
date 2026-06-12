$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$packedAppPath = Join-Path $repoRoot 'dist\queue_system.exe'
$fallbackPath = Join-Path $repoRoot 'start_queue_system.vbs'
$targetPath = if (Test-Path $packedAppPath) { $packedAppPath } else { $fallbackPath }
$iconPath = Join-Path $repoRoot 'web\DTI_Shortcut.ico'
$desktopPath = [Environment]::GetFolderPath('Desktop')
$shortcutPath = Join-Path $desktopPath 'DTI Laguna Queue System.lnk'
$legacyShortcutPath = Join-Path $desktopPath 'DTI Queue System.lnk'

if (Test-Path $legacyShortcutPath) {
	Remove-Item $legacyShortcutPath -Force
}

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $targetPath
$shortcut.WorkingDirectory = $repoRoot
$shortcut.WindowStyle = 1
$shortcut.IconLocation = $iconPath
$shortcut.Description = 'DTI Laguna Queue System'
$shortcut.Save()

Write-Host "Created shortcut: $shortcutPath"
