# SubExtract Studio — Developed by NoYz
# Intellectual Property & Copyright (c) 2026 NoYz. All Rights Reserved.
# Modern, Elegant GUI Uninstaller for SubExtract Studio

import os
import sys
import shutil
import subprocess
import ctypes
import winreg
import tempfile
import time

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QStackedWidget, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QPixmap

# UAC Elevation
def check_and_elevate():
    """Ensures uninstaller runs with Administrator privileges to delete files from Program Files and clean HKLM."""
    if sys.platform == "win32":
        try:
            if not ctypes.windll.shell32.IsUserAnAdmin():
                target = sys.executable if getattr(sys, 'frozen', False) else sys.executable
                params = " ".join([f'"{a}"' for a in sys.argv[1:]]) if getattr(sys, 'frozen', False) else f'"{os.path.abspath(sys.argv[0])}" ' + " ".join([f'"{a}"' for a in sys.argv[1:]])
                ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", target, params, None, 1)
                if ret > 32:
                    sys.exit(0)
        except Exception:
            pass

I18N = {
    "ar": {
        "title": "إلغاء تثبيت SubExtract Studio — NoYz",
        "header_title": "إلغاء تثبيت SubExtract Studio",
        "header_sub": "تطوير وإشراف NoYz | الإصدار 2.5",
        "lang_btn": "English",
        
        # Step 1: Confirm
        "confirm_title": "تأكيد إزالة البرنامج بالكامل",
        "confirm_desc": (
            "هل أنت متأكد من رغبتك في إزالة برنامج SubExtract Studio وكافة مكوناته بالكامل من جهاز الكمبيوتر الخاص بك؟\n\n"
            "سيتم حذف كافة الملفات، أدوات الفيديو المدمجة، الاختصارات، وإلغاء تسجيل البرنامج من نظام ويندوز.\n\n"
            "المجلد المستهدف للإزالة:\n{path}"
        ),
        "btn_uninstall": "إلغاء التثبيت الآن",
        "btn_cancel": "إلغاء",
        
        # Step 2: Progress
        "prog_title": "جاري إزالة البرنامج...",
        "prog_desc": "يرجى الانتظار بينما يتم تنظيف وحذف ملفات البرنامج من جهازك...",
        "status_prep": "جاري التجهيز...",
        "status_shortcuts": "إزالة اختصارات سطح المكتب وقائمة ابدأ...",
        "status_registry": "تنظيف سجل النظام ولوحة تحكم ويندوز...",
        "status_files": "حذف ملفات ومكونات البرنامج...",
        "status_done": "اكتملت الإزالة بنجاح!",
        
        # Step 3: Finish
        "finish_title": "تمت إزالة البرنامج بنجاح تام",
        "finish_desc": (
            "تمت إزالة برنامج SubExtract Studio بنجاح من جهاز الكمبيوتر الخاص بك.\n\n"
            "تم تنظيف كافة الاختصارات والبيانات المسجلة بالكامل.\n"
            "شكراً لاستخدامك SubExtract Studio."
        ),
        "btn_close": "إغلاق"
    },
    
    "en": {
        "title": "SubExtract Studio — Uninstall Wizard",
        "header_title": "SubExtract Studio Uninstaller",
        "header_sub": "Developed by NoYz | Version 2.5",
        "lang_btn": "العربية",
        
        # Step 1: Confirm
        "confirm_title": "Confirm Complete Uninstallation",
        "confirm_desc": (
            "Are you sure you want to completely remove SubExtract Studio and all of its components from your computer?\n\n"
            "This will delete all application files, bundled video engines, system shortcuts, and unregister the application from Windows.\n\n"
            "Target Directory:\n{path}"
        ),
        "btn_uninstall": "Uninstall Now",
        "btn_cancel": "Cancel",
        
        # Step 2: Progress
        "prog_title": "Uninstalling SubExtract Studio...",
        "prog_desc": "Please wait while files and shortcuts are being removed from your system...",
        "status_prep": "Preparing uninstallation...",
        "status_shortcuts": "Removing Desktop and Start Menu shortcuts...",
        "status_registry": "Cleaning Windows Registry and Control Panel...",
        "status_files": "Deleting application files and binaries...",
        "status_done": "Uninstallation complete!",
        
        # Step 3: Finish
        "finish_title": "Uninstallation Completed Successfully",
        "finish_desc": (
            "SubExtract Studio has been successfully removed from your computer.\n\n"
            "All shortcuts, components, and registration entries have been cleaned.\n"
            "Thank you for using SubExtract Studio."
        ),
        "btn_close": "Close"
    }
}


class UninstallWorker(QThread):
    progress_changed = pyqtSignal(int, str)
    uninstall_finished = pyqtSignal(bool, str)

    def __init__(self, target_dir: str, parent=None):
        super().__init__(parent)
        self.target_dir = target_dir

    def run(self):
        try:
            self.progress_changed.emit(15, "shortcuts")
            time.sleep(0.3)
            # 1. Remove Desktop Shortcut
            user_profile = os.environ.get("USERPROFILE", os.path.expanduser("~"))
            desk_shortcut = os.path.join(user_profile, "Desktop", "Sub Studio.lnk")
            if os.path.exists(desk_shortcut):
                try:
                    os.remove(desk_shortcut)
                except Exception:
                    pass

            # 2. Remove Start Menu Shortcuts
            self.progress_changed.emit(35, "shortcuts")
            for base_prog in [
                os.path.join(os.environ.get("ProgramData", r"C:\ProgramData"), "Microsoft", "Windows", "Start Menu", "Programs"),
                os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "Microsoft", "Windows", "Start Menu", "Programs")
            ]:
                sm_dir = os.path.join(base_prog, "SubExtract Studio")
                if os.path.exists(sm_dir):
                    try:
                        shutil.rmtree(sm_dir, ignore_errors=True)
                    except Exception:
                        pass

            # 3. Clean Windows Registry (Add/Remove Programs)
            self.progress_changed.emit(60, "registry")
            time.sleep(0.3)
            reg_sub = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\SubExtractStudio"
            for hive in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
                try:
                    winreg.DeleteKey(hive, reg_sub)
                except Exception:
                    pass

            # 4. Remove Target Directory Files
            self.progress_changed.emit(80, "files")
            time.sleep(0.4)
            if os.path.exists(self.target_dir):
                # Delete files inside target_dir
                for item in os.listdir(self.target_dir):
                    item_path = os.path.join(self.target_dir, item)
                    try:
                        if os.path.isdir(item_path):
                            shutil.rmtree(item_path, ignore_errors=True)
                        else:
                            os.remove(item_path)
                    except Exception:
                        pass
                
                # Try removing directory itself
                try:
                    os.rmdir(self.target_dir)
                except Exception:
                    pass

            self.progress_changed.emit(100, "done")
            time.sleep(0.2)
            self.uninstall_finished.emit(True, "")

        except Exception as e:
            self.uninstall_finished.emit(False, str(e))


class UninstallerWizard(QMainWindow):
    def __init__(self, target_dir: str):
        super().__init__()
        self.target_dir = target_dir
        self.current_lang = "ar"  # Default Arabic
        self.setWindowTitle(self.t("title"))
        self.setFixedSize(580, 420)

        # Set Window Icon if available
        icon_path = os.path.join(self.target_dir, "assets", "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._init_ui()
        self._apply_stylesheet()

    def t(self, key: str) -> str:
        return I18N[self.current_lang].get(key, I18N["en"].get(key, key))

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header Bar
        hdr = QFrame()
        hdr.setObjectName("headerFrame")
        hdr_layout = QHBoxLayout(hdr)
        hdr_layout.setContentsMargins(24, 16, 24, 16)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        self.lbl_hdr_title = QLabel(self.t("header_title"))
        self.lbl_hdr_title.setObjectName("headerTitle")
        self.lbl_hdr_sub = QLabel(self.t("header_sub"))
        self.lbl_hdr_sub.setObjectName("headerSub")
        text_layout.addWidget(self.lbl_hdr_title)
        text_layout.addWidget(self.lbl_hdr_sub)
        hdr_layout.addLayout(text_layout)
        hdr_layout.addStretch()

        self.btn_lang = QPushButton(self.t("lang_btn"))
        self.btn_lang.setObjectName("btnLang")
        self.btn_lang.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_lang.clicked.connect(self._toggle_lang)
        hdr_layout.addWidget(self.btn_lang)

        layout.addWidget(hdr)

        # Stack Pages
        self.stack = QStackedWidget()
        self.stack.setObjectName("contentStack")

        self.page_confirm = self._create_confirm_page()
        self.page_progress = self._create_progress_page()
        self.page_finish = self._create_finish_page()

        self.stack.addWidget(self.page_confirm)  # 0
        self.stack.addWidget(self.page_progress) # 1
        self.stack.addWidget(self.page_finish)   # 2

        layout.addWidget(self.stack, 1)

        # Bottom Bar
        nav = QFrame()
        nav.setObjectName("navBar")
        nav_layout = QHBoxLayout(nav)
        nav_layout.setContentsMargins(24, 14, 24, 14)
        nav_layout.addStretch()

        self.btn_cancel = QPushButton(self.t("btn_cancel"))
        self.btn_cancel.setObjectName("btnNav")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.close)
        nav_layout.addWidget(self.btn_cancel)

        self.btn_action = QPushButton(self.t("btn_uninstall"))
        self.btn_action.setObjectName("btnDanger")
        self.btn_action.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_action.clicked.connect(self._start_uninstall)
        nav_layout.addWidget(self.btn_action)

        layout.addWidget(nav)

        if self.current_lang == "ar":
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    def _create_confirm_page(self) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(28, 24, 28, 20)
        l.setSpacing(14)

        self.lbl_conf_h = QLabel(self.t("confirm_title"))
        self.lbl_conf_h.setObjectName("pageHeading")
        l.addWidget(self.lbl_conf_h)

        self.lbl_conf_b = QLabel(self.t("confirm_desc").format(path=self.target_dir))
        self.lbl_conf_b.setObjectName("pageBody")
        self.lbl_conf_b.setWordWrap(True)
        l.addWidget(self.lbl_conf_b)

        l.addStretch()
        return w

    def _create_progress_page(self) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(28, 36, 28, 20)
        l.setSpacing(14)

        self.lbl_prog_h = QLabel(self.t("prog_title"))
        self.lbl_prog_h.setObjectName("pageHeading")
        self.lbl_prog_b = QLabel(self.t("prog_desc"))
        self.lbl_prog_b.setObjectName("pageBody")

        l.addWidget(self.lbl_prog_h)
        l.addWidget(self.lbl_prog_b)

        self.prog_bar = QProgressBar()
        self.prog_bar.setObjectName("uninstallProgress")
        self.prog_bar.setRange(0, 100)
        self.prog_bar.setValue(0)
        self.prog_bar.setTextVisible(True)
        l.addWidget(self.prog_bar)

        self.lbl_prog_status = QLabel(self.t("status_prep"))
        self.lbl_prog_status.setObjectName("statusDetail")
        l.addWidget(self.lbl_prog_status)

        l.addStretch()
        return w

    def _create_finish_page(self) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(28, 30, 28, 20)
        l.setSpacing(14)

        self.lbl_fin_h = QLabel(self.t("finish_title"))
        self.lbl_fin_h.setObjectName("pageHeadingSuccess")
        self.lbl_fin_b = QLabel(self.t("finish_desc"))
        self.lbl_fin_b.setObjectName("pageBody")
        self.lbl_fin_b.setWordWrap(True)

        l.addWidget(self.lbl_fin_h)
        l.addWidget(self.lbl_fin_b)

        l.addStretch()
        return w

    def _start_uninstall(self):
        if self.stack.currentIndex() == 0:
            self.stack.setCurrentIndex(1)
            self.btn_cancel.setVisible(False)
            self.btn_action.setVisible(False)
            self.btn_lang.setEnabled(False)

            self.worker = UninstallWorker(self.target_dir)
            self.worker.progress_changed.connect(self._on_progress)
            self.worker.uninstall_finished.connect(self._on_finished)
            self.worker.start()
        elif self.stack.currentIndex() == 2:
            self.close()

    def _on_progress(self, pct: int, key: str):
        self.prog_bar.setValue(pct)
        if key == "shortcuts":
            self.lbl_prog_status.setText(self.t("status_shortcuts"))
        elif key == "registry":
            self.lbl_prog_status.setText(self.t("status_registry"))
        elif key == "files":
            self.lbl_prog_status.setText(self.t("status_files"))
        elif key == "done":
            self.lbl_prog_status.setText(self.t("status_done"))

    def _on_finished(self, success: bool, err: str):
        self.stack.setCurrentIndex(2)
        self.btn_action.setVisible(True)
        self.btn_action.setText(self.t("btn_close"))
        self.btn_action.setObjectName("btnPrimary")
        self.btn_action.setStyle(self.btn_action.style())

    def _toggle_lang(self):
        self.current_lang = "en" if self.current_lang == "ar" else "ar"
        self._refresh_texts()

    def _refresh_texts(self):
        self.setWindowTitle(self.t("title"))
        self.lbl_hdr_title.setText(self.t("header_title"))
        self.lbl_hdr_sub.setText(self.t("header_sub"))
        self.btn_lang.setText(self.t("lang_btn"))

        self.lbl_conf_h.setText(self.t("confirm_title"))
        self.lbl_conf_b.setText(self.t("confirm_desc").format(path=self.target_dir))

        self.lbl_prog_h.setText(self.t("prog_title"))
        self.lbl_prog_b.setText(self.t("prog_desc"))

        self.lbl_fin_h.setText(self.t("finish_title"))
        self.lbl_fin_b.setText(self.t("finish_desc"))

        self.btn_cancel.setText(self.t("btn_cancel"))
        if self.stack.currentIndex() == 2:
            self.btn_action.setText(self.t("btn_close"))
        else:
            self.btn_action.setText(self.t("btn_uninstall"))

        if self.current_lang == "ar":
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

    def _apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #11141c;
            }
            #headerFrame {
                background-color: #161b26;
                border-bottom: 1px solid #232a3b;
            }
            #headerTitle {
                color: #ffbe3b;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI', 'Cairo', sans-serif;
            }
            #headerSub {
                color: #94a3b8;
                font-size: 12px;
            }
            #btnLang {
                background-color: #222938;
                color: #ffbe3b;
                border: 1px solid #333e56;
                border-radius: 5px;
                padding: 5px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            #btnLang:hover {
                background-color: #ffbe3b;
                color: #0c0f16;
            }
            #contentStack {
                background-color: #11141c;
            }
            #pageHeading {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI', 'Cairo', sans-serif;
            }
            #pageHeadingSuccess {
                color: #22c55e;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', 'Cairo', sans-serif;
            }
            #pageBody {
                color: #cbd5e1;
                font-size: 13px;
                line-height: 1.6;
                font-family: 'Segoe UI', 'Cairo', sans-serif;
            }
            #uninstallProgress {
                background-color: #161b26;
                border: 1px solid #232a3b;
                border-radius: 6px;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
                height: 22px;
            }
            #uninstallProgress::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ef4444, stop:1 #f59e0b);
                border-radius: 5px;
            }
            #statusDetail {
                color: #94a3b8;
                font-size: 12px;
                font-family: 'Segoe UI', 'Cairo', sans-serif;
            }
            #navBar {
                background-color: #141822;
                border-top: 1px solid #232a3b;
            }
            #btnNav {
                background-color: #1c2230;
                color: #cbd5e1;
                border: 1px solid #2e374d;
                border-radius: 6px;
                padding: 8px 18px;
                font-size: 12px;
                font-weight: bold;
            }
            #btnNav:hover {
                background-color: #273044;
                color: #ffffff;
            }
            #btnDanger {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ef4444, stop:1 #dc2626);
                color: #ffffff;
                border: 1px solid #ef4444;
                border-radius: 6px;
                padding: 8px 22px;
                font-size: 13px;
                font-weight: bold;
            }
            #btnDanger:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f87171, stop:1 #ef4444);
            }
            #btnPrimary {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffbe3b, stop:1 #e5a013);
                color: #0c0f16;
                border: 1px solid #ffbe3b;
                border-radius: 6px;
                padding: 8px 24px;
                font-size: 13px;
                font-weight: bold;
            }
            #btnPrimary:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffd166, stop:1 #ffbe3b);
            }
        """)


def main():
    check_and_elevate()

    current_exe = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])
    current_dir = os.path.dirname(current_exe)

    # Parse arguments
    target_dir = current_dir
    is_temp_runner = False
    for i, arg in enumerate(sys.argv):
        if arg == "--temp-runner":
            is_temp_runner = True
        elif arg == "--dir" and i + 1 < len(sys.argv):
            target_dir = sys.argv[i + 1]

    # If running from inside the installation folder, copy to %TEMP% and relaunch so install folder can be deleted!
    if not is_temp_runner and getattr(sys, 'frozen', False):
        try:
            temp_dir = tempfile.gettempdir()
            temp_uninstaller = os.path.join(temp_dir, "subextract_uninstaller.exe")
            shutil.copy2(current_exe, temp_uninstaller)
            subprocess.Popen([temp_uninstaller, "--temp-runner", "--dir", current_dir])
            sys.exit(0)
        except Exception:
            pass

    if hasattr(sys, 'frozen'):
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    wizard = UninstallerWizard(target_dir)
    wizard.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
