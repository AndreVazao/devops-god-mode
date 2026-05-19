' VBScript to run a command hidden
Set WshShell = CreateObject("WScript.Shell")

If WScript.Arguments.Count < 2 Then
    WScript.Quit
End If

PythonExe = WScript.Arguments(0)
LauncherScript = WScript.Arguments(1)

' Run command: python launcher.py
' 0 = Hidden window, True = Wait for exit
WshShell.Run """" & PythonExe & """ """ & LauncherScript & """", 0, False
