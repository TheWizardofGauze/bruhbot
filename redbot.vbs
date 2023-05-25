'launch.vbs
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "redbot.bat", 0
WshShell.Run "bruhbot.py", 0
WshShell = Null