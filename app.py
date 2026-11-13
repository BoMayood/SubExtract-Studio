# SubExtract Studio — Developed by NoYz
# Intellectual Property & Copyright (c) 2026 NoYz. All Rights Reserved.
# Main Application Launcher & Process Manager

import os
import sys
import ctypes

# Enable High DPI and Native Windows Scaling
if hasattr(sys, 'frozen'):
    # When packaged with PyInstaller --noconsole
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

# Set AppUserModelID so Windows groups the taskbar icon properly
try:
    if sys.platform == "win32":
        myappid = "noyz.subextractstudio.desktopapp.v2"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow

def main():
    # Configure Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName("SubExtract Studio")
    app.setOrganizationName("NoYz")
    app.setApplicationVersion("2.5")

    # Set Window and Taskbar Icon
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, "assets", "icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Instantiate and display master window
    window = MainWindow()
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))
    window.show()

    # Enter smooth Qt event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
