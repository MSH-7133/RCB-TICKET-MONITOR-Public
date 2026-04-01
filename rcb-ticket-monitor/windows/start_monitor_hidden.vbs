Set WshShell = CreateObject("WScript.Shell")
' Get the directory where this VBS script is located
scriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
' Run the monitor with hidden window (0 = hidden, False = don't wait)
WshShell.Run "cmd /c cd /d """ & scriptDir & """ && call venv\Scripts\activate.bat && python rcb_ticket_monitor.py 15", 0, False
