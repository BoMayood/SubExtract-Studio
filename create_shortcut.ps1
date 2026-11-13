
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('C:\Users\NoYz\Desktop\Sub Studio.lnk')
$Shortcut.TargetPath = 'C:\Users\NoYz\AppData\Local\Programs\Python\Python312\pythonw.exe'
$Shortcut.Arguments = '"C:\Users\NoYz\.gemini\antigravity\scratch\subextract_studio\app.py"'
$Shortcut.WorkingDirectory = 'C:\Users\NoYz\.gemini\antigravity\scratch\subextract_studio'
$Shortcut.Description = 'Sub Studio — Developed by NoYz'
$Shortcut.IconLocation = 'C:\Users\NoYz\.gemini\antigravity\scratch\subextract_studio\assets\icon.ico,0'
$Shortcut.Save()
