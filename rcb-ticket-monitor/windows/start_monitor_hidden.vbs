Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the directory where this VBS script is located
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Change to script directory and run using relative path (simpler, more reliable)
WshShell.CurrentDirectory = scriptDir
WshShell.Run "cmd /c venv\Scripts\python.exe rcb_ticket_monitor.py 15 > rcb_monitor.log 2>&1", 0, False
