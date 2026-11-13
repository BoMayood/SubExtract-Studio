# SubExtract Studio — Developed by NoYz
# Intellectual Property & Copyright (c) 2026 NoYz. All Rights Reserved.
# Compiles installer_wizard.py with embedded payload into SubExtract_Studio_Setup.exe with UAC Admin

import os
import sys
import subprocess
import shutil

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PAYLOAD_ZIP = os.path.join(PROJECT_DIR, "installer_payload.zip")
ICON_PATH = os.path.join(PROJECT_DIR, "assets", "icon.ico")
RELEASE_DIR = os.path.join(PROJECT_DIR, "release")
INSTALLER_SRC = os.path.join(PROJECT_DIR, "installer_wizard.py")

print("=" * 60)
print("SubExtract Studio — Single Executable Installer Build")
print("With UAC Administrator Manifest for C:\\Program Files Installation")
print("Developed by NoYz | Copyright © 2026 NoYz")
print("=" * 60)

if not os.path.exists(PAYLOAD_ZIP):
    print(f"Error: Payload archive {PAYLOAD_ZIP} not found!")
    sys.exit(1)

cmd = [
    sys.executable, "-m", "PyInstaller",
    "--noconfirm",
    "--onefile",
    "--windowed",
    "--uac-admin",
    "--name", "SubExtract_Studio_Setup",
    "--icon", ICON_PATH,
    "--add-data", f"{PAYLOAD_ZIP};.",
    "--add-data", f"{ICON_PATH};assets",
    "--hidden-import", "PyQt6",
    "--hidden-import", "PyQt6.QtCore",
    "--hidden-import", "PyQt6.QtGui",
    "--hidden-import", "PyQt6.QtWidgets",
    "--hidden-import", "winreg",
    "--distpath", RELEASE_DIR,
    INSTALLER_SRC
]

print("Compiling SubExtract_Studio_Setup.exe with PyInstaller + UAC Admin...")
res = subprocess.run(cmd, cwd=PROJECT_DIR)

if res.returncode == 0:
    out_exe = os.path.join(RELEASE_DIR, "SubExtract_Studio_Setup.exe")
    if os.path.exists(out_exe):
        sz_mb = os.path.getsize(out_exe) / (1024 * 1024)
        print("\n" + "=" * 60)
        print("BUILD SUCCESSFUL!")
        print(f"Standalone Installer: {out_exe}")
        print(f"Installer File Size: {sz_mb:.2f} MB")
        print("=" * 60)
    else:
        print("Warning: Expected executable not found in release folder.")
else:
    print(f"PyInstaller failed with return code {res.returncode}")
    sys.exit(res.returncode)
