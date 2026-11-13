# Create desktop shortcut for Sub Studio dynamically on any user's PC
import os
import sys
import shutil
import subprocess

user_home = os.environ.get("USERPROFILE") or os.path.expanduser("~")
desktop = os.path.join(user_home, "Desktop")
shortcut_path = os.path.join(desktop, "Sub Studio.lnk")

work_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(work_dir, "app.py")
icon_path = os.path.join(work_dir, "assets", "icon.ico")

# Find pythonw.exe or python.exe dynamically on current machine
python_dir = os.path.dirname(sys.executable)
candidate_pythonw = os.path.join(python_dir, "pythonw.exe")
if os.path.exists(candidate_pythonw):
    target_exe = candidate_pythonw
else:
    target_exe = shutil.which("pythonw.exe") or sys.executable

ps_script = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
$Shortcut.TargetPath = '{target_exe}'
$Shortcut.Arguments = '"{script_path}"'
$Shortcut.WorkingDirectory = '{work_dir}'
$Shortcut.Description = 'Sub Studio — Developed by NoYz'
$Shortcut.IconLocation = '{icon_path},0'
$Shortcut.Save()
"""

ps_file = os.path.join(work_dir, "create_shortcut.ps1")
with open(ps_file, "w", encoding="utf-8") as f:
    f.write(ps_script)

res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_file], capture_output=True, text=True)
print("Return code:", res.returncode)
print("Output:", res.stdout)
print("Error:", res.stderr)

if os.path.exists(shortcut_path):
    print("SUCCESS: Shortcut verified at", shortcut_path)
else:
    print("FAILED: Shortcut not found.")
