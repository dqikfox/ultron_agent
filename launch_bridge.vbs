''' Launch Bridge - No CMD/PowerShell Required
''' This VBScript directly executes Python without any shell invocation

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the script directory
scriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)
pythonPath = scriptPath & "\.venv\Scripts\python.exe"
bridgeScript = scriptPath & "\copilot_amazon_q_bridge.py"

' Check if files exist
If Not objFSO.FileExists(pythonPath) Then
    WScript.Echo "ERROR: Python not found at: " & pythonPath
    WScript.Quit 1
End If

If Not objFSO.FileExists(bridgeScript) Then
    WScript.Echo "ERROR: Bridge script not found at: " & bridgeScript
    WScript.Quit 1
End If

' Run Python with bridge script
' 0 = run hidden, 1 = run normally
objShell.CurrentDirectory = scriptPath
objShell.Run """" & pythonPath & """ """ & bridgeScript & """ --listen", 1, False

WScript.Echo "Bridge started successfully!"
