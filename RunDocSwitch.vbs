Option Explicit

Dim wshShell, currentFolder, pythonPath, appScript, edgeAppCmd

Set wshShell = CreateObject("WScript.Shell")
currentFolder = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Paths for the backend
pythonPath = currentFolder & "\venv\Scripts\pythonw.exe"
appScript = currentFolder & "\app.py"

' Command to start Flask server completely hidden
wshShell.Run """" & pythonPath & """ """ & appScript & """", 0, False

' Wait 2 seconds for Flask to initialize
WScript.Sleep 2000

' Launch Microsoft Edge in App Mode (looks like a standalone desktop app)
edgeAppCmd = "cmd /c start msedge --app=http://127.0.0.1:5000"
wshShell.Run edgeAppCmd, 0, False

Set wshShell = Nothing
