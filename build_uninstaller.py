# SubExtract Studio — Developed by NoYz
# Compiles uninstaller_wizard.py into standalone uninstall.exe

import os
import sys
import subprocess
import shutil

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIST_DIR = os.path.join(PROJECT_DIR, "dist", "SubExtract Studio")
ICON_PATH = os.path.join(PROJECT_DIR, "assets", "icon.ico")
UNINSTALLER_SRC = os.path.join(PROJECT_DIR, "uninstaller_wizard.py")

print("=" * 60)
print("Compiling Modern Graphical Uninstaller (uninstall.exe)...")
print("Developed by NoYz | Copyright © 2026 NoYz")
print("=" * 60)

cmd = [
    sys.executable, "-m", "PyInstaller",
    "--noconfirm",
    "--onefile",
    "--windowed",
    "--uac-admin",
    "--name", "uninstall",
    "--icon", ICON_PATH,
    "--hidden-import", "PyQt6",
    "--hidden-import", "PyQt6.QtCore",
    "--hidden-import", "PyQt6.QtGui",
    "--hidden-import", "PyQt6.QtWidgets",
    "--hidden-import", "winreg",
    "--distpath", APP_DIST_DIR,
    UNINSTALLER_SRC
]

res = subprocess.run(cmd, cwd=PROJECT_DIR)
if res.returncode == 0:
    out_exe = os.path.join(APP_DIST_DIR, "uninstall.exe")
    if os.path.exists(out_exe):
        sz_mb = os.path.getsize(out_exe) / (1024 * 1024)
        print("\nSUCCESS: uninstall.exe compiled successfully!")
        print(f"Location: {out_exe} ({sz_mb:.2f} MB)")
    else:
        print("Error: uninstall.exe not found!")
        sys.exit(1)
else:
    print(f"Compilation failed with code {res.returncode}")
    sys.exit(res.returncode)
