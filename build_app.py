# SubExtract Studio — Developed by NoYz
# Intellectual Property & Copyright (c) 2026 NoYz. All Rights Reserved.
# Build script for SubExtract Studio application bundle

import os
import sys
import shutil
import subprocess

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(PROJECT_DIR, "dist")
BUILD_DIR = os.path.join(PROJECT_DIR, "build")
APP_DIST = os.path.join(DIST_DIR, "SubExtract Studio")

print("=" * 60)
print("SubExtract Studio — Application Build Process")
print("Developed by NoYz | Copyright © 2026 NoYz")
print("=" * 60)

# Clean previous build artifacts if any
if os.path.exists(BUILD_DIR):
    shutil.rmtree(BUILD_DIR, ignore_errors=True)

pyinstaller_cmd = [
    sys.executable, "-m", "PyInstaller",
    "--noconfirm",
    "--onedir",
    "--windowed",
    "--name", "SubExtract Studio",
    "--icon", os.path.join(PROJECT_DIR, "assets", "icon.ico"),
    "--hidden-import", "PyQt6",
    "--hidden-import", "PyQt6.QtCore",
    "--hidden-import", "PyQt6.QtGui",
    "--hidden-import", "PyQt6.QtWidgets",
    "--hidden-import", "requests",
    "--hidden-import", "deep_translator",
    "--hidden-import", "PIL",
    "--hidden-import", "pytesseract",
    "--hidden-import", "winsound",
    os.path.join(PROJECT_DIR, "app.py")
]

print("Running PyInstaller...")
res = subprocess.run(pyinstaller_cmd, cwd=PROJECT_DIR)
if res.returncode != 0:
    print("PyInstaller build failed!")
    sys.exit(res.returncode)

print("\nCopying bundled portable dependencies...")
# 1. Copy bin directory (ffmpeg.exe and ffprobe.exe)
dest_bin = os.path.join(APP_DIST, "bin")
os.makedirs(dest_bin, exist_ok=True)
src_bin = os.path.join(PROJECT_DIR, "bin")
if os.path.exists(src_bin):
    for f in os.listdir(src_bin):
        src_f = os.path.join(src_bin, f)
        dest_f = os.path.join(dest_bin, f)
        if not os.path.exists(dest_f):
            print(f"Copying {f}...")
            shutil.copy2(src_f, dest_f)

# 2. Copy assets directory
dest_assets = os.path.join(APP_DIST, "assets")
os.makedirs(dest_assets, exist_ok=True)
src_assets = os.path.join(PROJECT_DIR, "assets")
if os.path.exists(src_assets):
    for f in os.listdir(src_assets):
        shutil.copy2(os.path.join(src_assets, f), os.path.join(dest_assets, f))

# 3. Copy default config.json
shutil.copy2(os.path.join(PROJECT_DIR, "config.json"), os.path.join(APP_DIST, "config.json"))

print("\n" + "=" * 60)
print("SUCCESS: SubExtract Studio bundled successfully!")
print(f"Output folder: {APP_DIST}")
print("=" * 60)
