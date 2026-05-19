# Setup Windows Autostart for God Mode
$ProjectRoot = Get-Location
$LauncherPath = Join-Path $ProjectRoot "launcher.py"
$PythonExe = (Get-Command python).Source
$VbsPath = Join-Path $ProjectRoot "scripts\windows\start_hidden.vbs"
$StartupFolder = [System.IO.Path]::Combine($env:APPDATA, "Microsoft\Windows\Start Menu\Programs\Startup")
$ShortcutPath = Join-Path $StartupFolder "GodMode.lnk"

Write-Host "--- God Mode Autostart Setup ---"
Write-Host "Project Root: $ProjectRoot"
Write-Host "Launcher: $LauncherPath"
Write-Host "Python: $PythonExe"
Write-Host "Startup Shortcut: $ShortcutPath"

# Create the shortcut to the VBS script which runs the python launcher hidden
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "wscript.exe"
$Shortcut.Arguments = "`"$VbsPath`" `"$PythonExe`" `"$LauncherPath`""
$Shortcut.WorkingDirectory = $ProjectRoot
$Shortcut.IconLocation = "powershell.exe,0"
$Shortcut.Description = "God Mode Backend Launcher"
$Shortcut.Save()

Write-Host "✅ Autostart shortcut created in Startup folder."
Write-Host "To test, run: wscript.exe '$VbsPath' '$PythonExe' '$LauncherPath'"
