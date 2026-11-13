# SubExtract Studio — Developed by NoYz
# Intellectual Property & Copyright (c) 2026 NoYz. All Rights Reserved.
# Modern, Enterprise-Grade Setup Installer Wizard for Windows

import os
import sys
import shutil
import zipfile
import subprocess
import ctypes
import winreg

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFileDialog, QProgressBar,
    QCheckBox, QRadioButton, QStackedWidget, QFrame, QMessageBox,
    QTextEdit, QButtonGroup
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QPixmap

# -------------------------------------------------------------
# UAC Administrator Elevation Check
# -------------------------------------------------------------
def check_and_elevate():
    """Ensures installer runs with Administrator privileges to install into C:\\Program Files."""
    if sys.platform == "win32":
        try:
            if not ctypes.windll.shell32.IsUserAnAdmin():
                if getattr(sys, 'frozen', False):
                    target = sys.executable
                    params = " ".join([f'"{a}"' for a in sys.argv[1:]])
                else:
                    target = sys.executable
                    script = os.path.abspath(sys.argv[0])
                    params = f'"{script}" ' + " ".join([f'"{a}"' for a in sys.argv[1:]])

                ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", target, params, None, 1)
                if ret > 32:
                    sys.exit(0)
        except Exception:
            pass


# -------------------------------------------------------------
# Localization Strings (English & Arabic)
# -------------------------------------------------------------
I18N = {
    "en": {
        "app_name": "SubExtract Studio",
        "app_edition": "v2.5 Pro Edition",
        "developer": "Developed by NoYz",
        "copyright": "Copyright © 2026 NoYz. All Rights Reserved.",
        "lang_btn": "العربية",
        
        # Steps in sidebar
        "step_welcome": "1. Welcome",
        "step_license": "2. Terms of Use",
        "step_location": "3. Install Location",
        "step_options": "4. Setup Options",
        "step_install": "5. Installing",
        "step_finish": "6. Completed",
        
        # Step 1: Welcome
        "welcome_title": "Welcome to SubExtract Studio Setup",
        "welcome_body": (
            "This setup wizard will install SubExtract Studio v2.5 Pro Edition on your computer.\n\n"
            "Key Features of SubExtract Studio:\n"
            "• Direct & Silent subtitle extraction from MKV, MP4, MOV, and WEBM videos\n"
            "• Neural AI Translation (Google Gemini & OpenAI) and Free Google Translate\n"
            "• High-precision OCR extraction for PGS / image-based anime & movie subtitles\n"
            "• Hardcoded subtitle burn-in with complete font, color, and outline typography\n"
            "• Integrated Subtitle Studio with live player, time synchronization, and format conversion\n\n"
            "★ Fully Standalone: Bundled with FFmpeg & FFprobe media engines.\n"
            "★ Zero Prerequisites: No Python, command line, or external dependencies required.\n\n"
            "Click Next to continue."
        ),
        
        # Step 2: License / Terms of Use
        "license_title": "Terms of Use",
        "license_subtitle": "Please read the following terms of use carefully before continuing:",
        "license_text": (
            "Terms of Use\n"
            "By using this software, you agree to the following terms:\n\n"
            "• Free & Open Source: This software is completely free and available to everyone for personal and educational use. The source code is accessible for review, learning, and development.\n\n"
            "• Commercial Sale Strictly Prohibited: Selling this software or profiting from it in any way—whether in its original form or after modification—is strictly forbidden.\n\n"
            "• Developer Attribution & Rights: You have the right to modify the code and share it with others, provided that you clearly attribute the original developer and project, without removing or altering proprietary notices.\n\n"
            "• Disclaimer of Responsibility: This software is purely a technical tool for extracting and translating text. The user assumes full legal responsibility for processed files. The developer is not responsible for any misuse or copyright infringements.\n\n"
            "• Disclaimer of Warranty: The software is provided 'AS IS' without any warranties. The developer assumes no responsibility for any system glitches, data loss, or damages that may occur during use."
        ),
        "license_accept": "I accept the terms of use",
        "license_decline": "I do not accept the terms",
        
        # Step 3: Location
        "loc_title": "Select Destination Location",
        "loc_subtitle": "Where should SubExtract Studio be installed?",
        "loc_desc": "Setup will install SubExtract Studio into the following folder.\nTo continue, click Next. To choose a different folder, click Browse.",
        "btn_browse": "Browse...",
        "space_req": "Space required: ~540 MB",
        "space_avail": "Space available on drive: {avail} GB",
        
        # Step 4: Options
        "opt_title": "Select Additional Tasks",
        "opt_subtitle": "Which additional tasks should be performed?",
        "opt_desc": "Select the additional tasks you would like Setup to perform while installing SubExtract Studio:",
        "chk_desktop": "Create a Desktop shortcut (Sub Studio)",
        "chk_startmenu": "Create a Start Menu program shortcut",
        "chk_launch": "Launch SubExtract Studio after installation",
        
        # Step 5: Installing
        "inst_title": "Installing SubExtract Studio",
        "inst_subtitle": "Please wait while Setup installs SubExtract Studio on your computer...",
        "status_prep": "Preparing destination folder...",
        "status_extracting": "Extracting: {filename}",
        "status_shortcuts": "Creating application shortcuts...",
        "status_registering": "Registering application in Windows...",
        "status_finalizing": "Finalizing installation...",
        
        # Step 6: Completed
        "finish_title": "Setup Completed Successfully!",
        "finish_body": (
            "SubExtract Studio v2.5 has been successfully installed on your computer.\n\n"
            "The application is fully configured and ready for immediate use.\n"
            "Click Finish to exit the Setup Wizard."
        ),
        "chk_finish_launch": "Launch SubExtract Studio now",
        
        # Navigation buttons
        "btn_next": "Next >",
        "btn_back": "< Back",
        "btn_install": "Install Now",
        "btn_cancel": "Cancel",
        "btn_finish": "Finish",
        
        # Dialogs
        "cancel_title": "Exit Setup",
        "cancel_msg": "Are you sure you want to cancel the installation?",
        "error_title": "Installation Error",
        "error_msg": "An error occurred during installation:\n{error}\n\nPlease ensure you run the setup as Administrator."
    },
    
    "ar": {
        "app_name": "SubExtract Studio",
        "app_edition": "الإصدار 2.5 الاحترافي",
        "developer": "تطوير وإشراف NoYz",
        "copyright": "جميع الحقوق محفوظة © 2026 NoYz",
        "lang_btn": "English",
        
        # Steps in sidebar
        "step_welcome": "1. الترحيب بالبرنامج",
        "step_license": "2. شروط الاستخدام",
        "step_location": "3. مسار التثبيت",
        "step_options": "4. خيارات التثبيت",
        "step_install": "5. جاري التثبيت",
        "step_finish": "6. اكتمال التثبيت",
        
        # Step 1: Welcome
        "welcome_title": "أهلاً بك في معالج تثبيت SubExtract Studio",
        "welcome_body": (
            "سيقوم هذا المعالج بتثبيت برنامج SubExtract Studio الإصدار 2.5 الاحترافي على جهازك.\n\n"
            "أهم مميزات البرنامج:\n"
            "• استخراج صامت وفوري للترجمات من كافة صيغ الفيديو (MKV, MP4, MOV, WEBM)\n"
            "• ترجمة فورية بالذكاء الاصطناعي (Google Gemini / OpenAI) وترجمة قوقل المجانية\n"
            "• استخراج الترجمات المصورة بدقة فائقة عبر محرك التعرف الضوئي OCR\n"
            "• حرق الترجمة نهائياً داخل الفيديو مع تخصيص كامل للخطوط والألوان والظلال\n"
            "• استوديو متكامل لمزامنة الترجمات وتعديل النصوص والتحويل بين الصيغ\n\n"
            "★ برنامج محمول ومستقل بالكامل: يضم أدوات FFmpeg و FFprobe مدمجة ذاتياً.\n"
            "★ لا يتطلب أي برامج إضافية: يعمل مباشرة دون الحاجة لتثبيت بايثون أو أي متطلبات.\n\n"
            "اضغط على التالي للبدء في خطوات التثبيت."
        ),
        
        # Step 2: License / Terms of Use
        "license_title": "شروط الاستخدام",
        "license_subtitle": "يرجى قراءة شروط الاستخدام بعناية قبل المتابعة في التثبيت:",
        "license_text": (
            "شروط الاستخدام\n"
            "باستخدامك لهذا البرنامج، فإنك توافق على الشروط التالية:\n\n"
            "• مجاني ومفتوح المصدر: هذا البرنامج مجاني بالكامل ومتاح للجميع للاستخدام الشخصي والتعليمي، كما أن الكود المصدري (Source Code) متوفر للجميع للاطلاع والتطوير.\n\n"
            "• يُمنع البيع أو الاستغلال التجاري: يُمنع منعاً باتاً بيع هذا البرنامج أو التربح منه بأي شكل من الأشكال، سواء بنسخته الأصلية أو بعد التعديل عليه.\n\n"
            "• حفظ حقوق المطور: يحق لك التعديل على الكود ومشاركته مع الآخرين بشرط الإشارة بوضوح إلى اسم المطور الأصلي ورابط المشروع، وعدم إزالة أو تغيير حقوق الملكية الموجودة في البرنامج.\n\n"
            "• إخلاء المسؤولية: البرنامج مجرد أداة تقنية لاستخراج وترجمة النصوص. المستخدم يتحمل المسؤولية الكاملة عن الملفات التي يتعامل معها ومدى قانونيتها، والمطور غير مسؤول عن أي استخدام خاطئ أو مخالف لحقوق النشر.\n\n"
            "• الضمان: يُقدم البرنامج \"كما هو\" دون أي ضمانات، ولا يتحمل المطور أي مسؤولية عن أي أعطال أو فقدان للبيانات قد يحدث أثناء الاستخدام."
        ),
        "license_accept": "أوافق على جميع الشروط المذكورة أعلاه",
        "license_decline": "لا أوافق على الشروط",
        
        # Step 3: Location
        "loc_title": "اختيار مجلد التثبيت",
        "loc_subtitle": "أين ترغب في تثبيت برنامج SubExtract Studio؟",
        "loc_desc": "سيقوم معالج التثبيت بتثبيت البرنامج في المجلد الموضح أدناه.\nللمتابعة اضغط التالي، أو اضغط استعراض لاختيار مجلد أو قرص آخر.",
        "btn_browse": "استعراض...",
        "space_req": "المساحة المطلوبة: ~540 ميجابايت",
        "space_avail": "المساحة المتوفرة على القرص: {avail} جيجابايت",
        
        # Step 4: Options
        "opt_title": "الخيارات والإجراءات الإضافية",
        "opt_subtitle": "ما هي الإجراءات التي ترغب في تطبيقها أثناء التثبيت؟",
        "opt_desc": "حدد المهام الإضافية التي ترغب أن يقوم بها معالج التثبيت:",
        "chk_desktop": "إنشاء اختصار على سطح المكتب (Sub Studio)",
        "chk_startmenu": "إنشاء اختصار في قائمة ابدأ (Start Menu)",
        "chk_launch": "تشغيل البرنامج تلقائياً فور اكتمال التثبيت",
        
        # Step 5: Installing
        "inst_title": "جاري تثبيت SubExtract Studio",
        "inst_subtitle": "يرجى الانتظار بينما يقوم المعالج بتهيئة وتثبيت الملفات على جهازك...",
        "status_prep": "جاري تجهيز مجلد التثبيت...",
        "status_extracting": "جاري فك: {filename}",
        "status_shortcuts": "جاري إنشاء اختصارات النظام...",
        "status_registering": "جاري تسجيل البرنامج في نظام ويندوز...",
        "status_finalizing": "جاري إنهاء التثبيت والتهيئة...",
        
        # Step 6: Completed
        "finish_title": "اكتمل التثبيت بنجاح تام!",
        "finish_body": (
            "تم تثبيت برنامج SubExtract Studio v2.5 بنجاح على جهاز الكمبيوتر الخاص بك.\n\n"
            "تمت تهيئة كافة ملفات النظام والبرنامج جاهز للاستخدام الفوري.\n"
            "اضغط على إنهاء لإغلاق معالج التثبيت."
        ),
        "chk_finish_launch": "تشغيل برنامج SubExtract Studio الآن",
        
        # Navigation buttons
        "btn_next": "التالي >",
        "btn_back": "< السابق",
        "btn_install": "تثبيت الآن",
        "btn_cancel": "إلغاء",
        "btn_finish": "إنهاء",
        
        # Dialogs
        "cancel_title": "إلغاء التثبيت",
        "cancel_msg": "هل أنت متأكد من رغبتك في إغلاق معالج التثبيت؟",
        "error_title": "خطأ أثناء التثبيت",
        "error_msg": "حدث خطأ أثناء عملية التثبيت:\n{error}\n\nيرجى التأكد من تشغيل المعالج كمسؤول (Run as administrator)."
    }
}


def get_resource_path(relative_path: str) -> str:
    """Returns absolute path to resource, resolving PyInstaller temp directory if frozen."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, relative_path)


class InstallWorker(QThread):
    """Background worker that extracts the application, creates shortcuts, and registers with Windows."""
    progress_changed = pyqtSignal(int, str)       # percentage, status_text
    installation_finished = pyqtSignal(bool, str) # success, error_message

    def __init__(self, dest_dir: str, create_desktop: bool, create_startmenu: bool, parent=None):
        super().__init__(parent)
        self.dest_dir = dest_dir
        self.create_desktop = create_desktop
        self.create_startmenu = create_startmenu
        self._is_cancelled = False

    def run(self):
        try:
            self.progress_changed.emit(2, "Preparing destination directory...")
            os.makedirs(self.dest_dir, exist_ok=True)

            payload_path = get_resource_path("installer_payload.zip")
            if not os.path.exists(payload_path):
                alt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "installer_payload.zip")
                if os.path.exists(alt_path):
                    payload_path = alt_path
                else:
                    raise FileNotFoundError(f"Installer payload not found at: {payload_path}")

            with zipfile.ZipFile(payload_path, "r") as zf:
                file_list = zf.infolist()
                total_files = len(file_list)
                extracted_count = 0

                for item in file_list:
                    if self._is_cancelled:
                        return
                    zf.extract(item, self.dest_dir)
                    extracted_count += 1
                    pct = int(5 + (extracted_count / total_files) * 82)
                    short_name = os.path.basename(item.filename) or item.filename
                    self.progress_changed.emit(pct, f"Extracting: {short_name}")

            exe_path = os.path.join(self.dest_dir, "SubExtract Studio.exe")
            uninst_exe = os.path.join(self.dest_dir, "uninstall.exe")
            icon_path = os.path.join(self.dest_dir, "assets", "icon.ico")

            # Create Desktop Shortcut
            if self.create_desktop and os.path.exists(exe_path):
                self.progress_changed.emit(90, "Creating Desktop shortcut...")
                desktop_dir = os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "Desktop")
                shortcut_dest = os.path.join(desktop_dir, "Sub Studio.lnk")
                self._create_windows_shortcut(shortcut_dest, exe_path, self.dest_dir, icon_path)

            # Create Start Menu Shortcuts
            if self.create_startmenu and os.path.exists(exe_path):
                self.progress_changed.emit(93, "Creating Start Menu shortcuts...")
                common_programs = os.path.join(os.environ.get("ProgramData", r"C:\ProgramData"), "Microsoft", "Windows", "Start Menu", "Programs")
                if not os.path.exists(common_programs):
                    common_programs = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "Microsoft", "Windows", "Start Menu", "Programs")
                startmenu_folder = os.path.join(common_programs, "SubExtract Studio")
                os.makedirs(startmenu_folder, exist_ok=True)
                
                # Main App Shortcut
                start_shortcut = os.path.join(startmenu_folder, "SubExtract Studio.lnk")
                self._create_windows_shortcut(start_shortcut, exe_path, self.dest_dir, icon_path)

                # Modern Uninstaller Shortcut
                if os.path.exists(uninst_exe):
                    start_uninst = os.path.join(startmenu_folder, "Uninstall SubExtract Studio.lnk")
                    self._create_windows_shortcut(start_uninst, uninst_exe, self.dest_dir, icon_path)

            # Always Register Application in Windows Settings / Control Panel
            self.progress_changed.emit(98, "Registering application in Windows...")
            self._register_in_windows(self.dest_dir, exe_path, icon_path)

            self.progress_changed.emit(100, "Installation complete!")
            self.installation_finished.emit(True, "")

        except Exception as e:
            self.installation_finished.emit(False, str(e))

    def _create_windows_shortcut(self, shortcut_path: str, target_exe: str, work_dir: str, icon_path: str):
        """Creates a native Windows .lnk shortcut via PowerShell WScript.Shell."""
        try:
            ps_cmd = (
                f'$ws = New-Object -ComObject WScript.Shell; '
                f'$s = $ws.CreateShortcut("{shortcut_path}"); '
                f'$s.TargetPath = "{target_exe}"; '
                f'$s.WorkingDirectory = "{work_dir}"; '
                f'$s.Description = "SubExtract Studio — Developed by NoYz"; '
            )
            if os.path.exists(icon_path):
                ps_cmd += f'$s.IconLocation = "{icon_path},0"; '
            ps_cmd += '$s.Save();'

            subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                capture_output=True,
                text=True
            )
        except Exception:
            pass

    def _register_in_windows(self, install_dir: str, exe_path: str, icon_path: str):
        """Registers the application in Windows Registry under Add/Remove Programs with GUI uninstaller."""
        uninst_exe = os.path.join(install_dir, "uninstall.exe")
        reg_key_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\SubExtractStudio"

        # Try HKLM first (machine-wide for Program Files), then HKCU as fallback
        hives = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]
        for hive in hives:
            try:
                with winreg.CreateKeyEx(hive, reg_key_path, 0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "SubExtract Studio")
                    winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "2.5")
                    winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "NoYz")
                    winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, install_dir)
                    winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, icon_path if os.path.exists(icon_path) else exe_path)
                    winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'"{uninst_exe}"')
                    winreg.SetValueEx(key, "EstimatedSize", 0, winreg.REG_DWORD, 550000)
                    winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
                break
            except Exception:
                continue


class InstallerWizard(QMainWindow):
    """High-end Windows Setup Wizard with Hero Sidebar and multi-page workflow."""

    def __init__(self):
        super().__init__()
        self.current_lang = "ar"  # Default to Arabic for user
        self.setWindowTitle(self.t("app_name") + " — Setup")
        self.setFixedSize(760, 520)

        # Set App Icon
        icon_path = get_resource_path(os.path.join("assets", "icon.ico"))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Default Destination Path: C:\Program Files\SubExtract Studio
        prog_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        self.default_dest = os.path.join(prog_files, "SubExtract Studio")

        self._init_ui()
        self._apply_stylesheet()
        self._update_disk_space()

    def t(self, key: str) -> str:
        return I18N[self.current_lang].get(key, I18N["en"].get(key, key))

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---------------------------------------------------------
        # Left Hero Sidebar (Brand, Logo, Stepper)
        # ---------------------------------------------------------
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebarFrame")
        self.sidebar.setFixedWidth(225)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(18, 24, 18, 20)
        sidebar_layout.setSpacing(14)

        # App Logo & Brand
        brand_layout = QVBoxLayout()
        brand_layout.setSpacing(4)
        
        self.lbl_logo = QLabel()
        self.lbl_logo.setObjectName("sidebarLogo")
        icon_path = get_resource_path(os.path.join("assets", "icon.ico"))
        if os.path.exists(icon_path):
            pix = QPixmap(icon_path)
            self.lbl_logo.setPixmap(pix.scaled(52, 52, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        brand_layout.addWidget(self.lbl_logo)

        self.lbl_brand_name = QLabel(self.t("app_name"))
        self.lbl_brand_name.setObjectName("sidebarBrandTitle")
        self.lbl_brand_dev = QLabel(self.t("developer"))
        self.lbl_brand_dev.setObjectName("sidebarBrandSub")
        brand_layout.addWidget(self.lbl_brand_name)
        brand_layout.addWidget(self.lbl_brand_dev)
        sidebar_layout.addLayout(brand_layout)

        # Divider line
        div = QFrame()
        div.setObjectName("sidebarDivider")
        div.setFrameShape(QFrame.Shape.HLine)
        sidebar_layout.addWidget(div)

        # Step Indicators
        self.step_labels = []
        steps_keys = ["step_welcome", "step_license", "step_location", "step_options", "step_install", "step_finish"]
        for key in steps_keys:
            lbl = QLabel(self.t(key))
            lbl.setObjectName("stepItem")
            sidebar_layout.addWidget(lbl)
            self.step_labels.append(lbl)

        sidebar_layout.addStretch()

        # Sidebar Footer
        self.lbl_edition = QLabel(self.t("app_edition"))
        self.lbl_edition.setObjectName("sidebarEdition")
        sidebar_layout.addWidget(self.lbl_edition)

        main_layout.addWidget(self.sidebar)

        # ---------------------------------------------------------
        # Right Main Content Area
        # ---------------------------------------------------------
        right_container = QWidget()
        right_container.setObjectName("rightContainer")
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Header Bar (Step title + Language switcher)
        header_bar = QFrame()
        header_bar.setObjectName("topBar")
        header_bar_layout = QHBoxLayout(header_bar)
        header_bar_layout.setContentsMargins(28, 14, 28, 14)

        self.lbl_top_title = QLabel(self.t("welcome_title"))
        self.lbl_top_title.setObjectName("topBarTitle")
        header_bar_layout.addWidget(self.lbl_top_title)
        header_bar_layout.addStretch()

        self.btn_lang = QPushButton(self.t("lang_btn"))
        self.btn_lang.setObjectName("btnLang")
        self.btn_lang.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_lang.clicked.connect(self._toggle_language)
        header_bar_layout.addWidget(self.btn_lang)

        right_layout.addWidget(header_bar)

        # Wizard Stack
        self.stack = QStackedWidget()
        self.stack.setObjectName("wizardStack")

        self.page_welcome = self._create_welcome_page()
        self.page_license = self._create_license_page()
        self.page_location = self._create_location_page()
        self.page_options = self._create_options_page()
        self.page_progress = self._create_progress_page()
        self.page_finish = self._create_finish_page()

        self.stack.addWidget(self.page_welcome)   # 0
        self.stack.addWidget(self.page_license)   # 1
        self.stack.addWidget(self.page_location)  # 2
        self.stack.addWidget(self.page_options)   # 3
        self.stack.addWidget(self.page_progress)  # 4
        self.stack.addWidget(self.page_finish)    # 5

        right_layout.addWidget(self.stack, 1)

        # Navigation Bar
        nav_bar = QFrame()
        nav_bar.setObjectName("navBar")
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(28, 14, 28, 14)
        nav_layout.setSpacing(10)

        self.lbl_nav_note = QLabel(self.t("copyright"))
        self.lbl_nav_note.setObjectName("navNote")
        nav_layout.addWidget(self.lbl_nav_note)
        nav_layout.addStretch()

        self.btn_back = QPushButton(self.t("btn_back"))
        self.btn_back.setObjectName("btnNav")
        self.btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_back.clicked.connect(self._go_back)
        self.btn_back.setVisible(False)
        nav_layout.addWidget(self.btn_back)

        self.btn_next = QPushButton(self.t("btn_next"))
        self.btn_next.setObjectName("btnPrimary")
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.clicked.connect(self._go_next)
        nav_layout.addWidget(self.btn_next)

        self.btn_cancel = QPushButton(self.t("btn_cancel"))
        self.btn_cancel.setObjectName("btnNav")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.clicked.connect(self._cancel_install)
        nav_layout.addWidget(self.btn_cancel)

        right_layout.addWidget(nav_bar)
        main_layout.addWidget(right_container, 1)

        self._update_stepper(0)

    # -------------------------------------------------------------
    # Wizard Pages
    # -------------------------------------------------------------
    def _create_welcome_page(self) -> QWidget:
        p = QWidget()
        l = QVBoxLayout(p)
        l.setContentsMargins(28, 20, 28, 16)
        l.setSpacing(12)

        self.lbl_welc_h = QLabel(self.t("welcome_title"))
        self.lbl_welc_h.setObjectName("pageHeading")
        l.addWidget(self.lbl_welc_h)

        self.lbl_welc_b = QLabel(self.t("welcome_body"))
        self.lbl_welc_b.setObjectName("pageBody")
        self.lbl_welc_b.setWordWrap(True)
        l.addWidget(self.lbl_welc_b)

        l.addStretch()
        return p

    def _create_license_page(self) -> QWidget:
        p = QWidget()
        l = QVBoxLayout(p)
        l.setContentsMargins(28, 16, 28, 16)
        l.setSpacing(10)

        self.lbl_lic_h = QLabel(self.t("license_title"))
        self.lbl_lic_h.setObjectName("pageHeading")
        self.lbl_lic_sub = QLabel(self.t("license_subtitle"))
        self.lbl_lic_sub.setObjectName("pageSub")
        l.addWidget(self.lbl_lic_h)
        l.addWidget(self.lbl_lic_sub)

        self.txt_license = QTextEdit()
        self.txt_license.setObjectName("licenseBox")
        self.txt_license.setReadOnly(True)
        self.txt_license.setPlainText(self.t("license_text"))
        if self.current_lang == "ar":
            self.txt_license.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            self.txt_license.setAlignment(Qt.AlignmentFlag.AlignRight)
        l.addWidget(self.txt_license, 1)

        self.radio_accept = QRadioButton(self.t("license_accept"))
        self.radio_accept.setObjectName("radioOption")
        self.radio_accept.setChecked(True)
        self.radio_accept.toggled.connect(self._on_license_toggled)

        self.radio_decline = QRadioButton(self.t("license_decline"))
        self.radio_decline.setObjectName("radioOption")
        self.radio_decline.toggled.connect(self._on_license_toggled)

        self.license_group = QButtonGroup()
        self.license_group.addButton(self.radio_accept)
        self.license_group.addButton(self.radio_decline)

        l.addWidget(self.radio_accept)
        l.addWidget(self.radio_decline)
        return p

    def _create_location_page(self) -> QWidget:
        p = QWidget()
        l = QVBoxLayout(p)
        l.setContentsMargins(28, 20, 28, 16)
        l.setSpacing(14)

        self.lbl_loc_h = QLabel(self.t("loc_title"))
        self.lbl_loc_h.setObjectName("pageHeading")
        self.lbl_loc_sub = QLabel(self.t("loc_subtitle"))
        self.lbl_loc_sub.setObjectName("pageSub")
        self.lbl_loc_desc = QLabel(self.t("loc_desc"))
        self.lbl_loc_desc.setObjectName("pageBody")
        self.lbl_loc_desc.setWordWrap(True)

        l.addWidget(self.lbl_loc_h)
        l.addWidget(self.lbl_loc_sub)
        l.addWidget(self.lbl_loc_desc)

        path_box = QHBoxLayout()
        self.edit_dest = QLineEdit(self.default_dest)
        self.edit_dest.setObjectName("editPath")
        self.edit_dest.textChanged.connect(self._update_disk_space)
        path_box.addWidget(self.edit_dest, 1)

        self.btn_browse = QPushButton(self.t("btn_browse"))
        self.btn_browse.setObjectName("btnSecondary")
        self.btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_browse.clicked.connect(self._browse_destination)
        path_box.addWidget(self.btn_browse)
        l.addLayout(path_box)

        # Space Card
        space_frame = QFrame()
        space_frame.setObjectName("infoCard")
        space_layout = QVBoxLayout(space_frame)
        space_layout.setContentsMargins(14, 10, 14, 10)
        self.lbl_space_req = QLabel(self.t("space_req"))
        self.lbl_space_req.setObjectName("infoText")
        self.lbl_space_avail = QLabel("")
        self.lbl_space_avail.setObjectName("infoText")
        space_layout.addWidget(self.lbl_space_req)
        space_layout.addWidget(self.lbl_space_avail)
        l.addWidget(space_frame)

        l.addStretch()
        return p

    def _create_options_page(self) -> QWidget:
        p = QWidget()
        l = QVBoxLayout(p)
        l.setContentsMargins(28, 20, 28, 16)
        l.setSpacing(12)

        self.lbl_opt_h = QLabel(self.t("opt_title"))
        self.lbl_opt_h.setObjectName("pageHeading")
        self.lbl_opt_sub = QLabel(self.t("opt_subtitle"))
        self.lbl_opt_sub.setObjectName("pageSub")
        self.lbl_opt_desc = QLabel(self.t("opt_desc"))
        self.lbl_opt_desc.setObjectName("pageBody")

        l.addWidget(self.lbl_opt_h)
        l.addWidget(self.lbl_opt_sub)
        l.addWidget(self.lbl_opt_desc)

        self.chk_desktop = QCheckBox(self.t("chk_desktop"))
        self.chk_desktop.setChecked(True)
        self.chk_desktop.setObjectName("chkOption")
        l.addWidget(self.chk_desktop)

        self.chk_startmenu = QCheckBox(self.t("chk_startmenu"))
        self.chk_startmenu.setChecked(True)
        self.chk_startmenu.setObjectName("chkOption")
        l.addWidget(self.chk_startmenu)

        self.chk_launch = QCheckBox(self.t("chk_launch"))
        self.chk_launch.setChecked(True)
        self.chk_launch.setObjectName("chkOption")
        l.addWidget(self.chk_launch)

        l.addStretch()
        return p

    def _create_progress_page(self) -> QWidget:
        p = QWidget()
        l = QVBoxLayout(p)
        l.setContentsMargins(28, 36, 28, 20)
        l.setSpacing(14)

        self.lbl_prog_h = QLabel(self.t("inst_title"))
        self.lbl_prog_h.setObjectName("pageHeading")
        self.lbl_prog_sub = QLabel(self.t("inst_subtitle"))
        self.lbl_prog_sub.setObjectName("pageBody")

        l.addWidget(self.lbl_prog_h)
        l.addWidget(self.lbl_prog_sub)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("installProgress")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        l.addWidget(self.progress_bar)

        self.lbl_prog_status = QLabel(self.t("status_prep"))
        self.lbl_prog_status.setObjectName("statusDetail")
        l.addWidget(self.lbl_prog_status)

        l.addStretch()
        return p

    def _create_finish_page(self) -> QWidget:
        p = QWidget()
        l = QVBoxLayout(p)
        l.setContentsMargins(28, 30, 28, 20)
        l.setSpacing(14)

        self.lbl_fin_h = QLabel(self.t("finish_title"))
        self.lbl_fin_h.setObjectName("pageHeading")
        self.lbl_fin_b = QLabel(self.t("finish_body"))
        self.lbl_fin_b.setObjectName("pageBody")
        self.lbl_fin_b.setWordWrap(True)

        l.addWidget(self.lbl_fin_h)
        l.addWidget(self.lbl_fin_b)

        self.chk_fin_launch = QCheckBox(self.t("chk_finish_launch"))
        self.chk_fin_launch.setChecked(True)
        self.chk_fin_launch.setObjectName("chkOption")
        l.addWidget(self.chk_fin_launch)

        l.addStretch()
        return p

    # -------------------------------------------------------------
    # Navigation & Stepper Controller
    # -------------------------------------------------------------
    def _update_stepper(self, step_idx: int):
        for i, lbl in enumerate(self.step_labels):
            if i == step_idx:
                lbl.setProperty("active", "true")
            elif i < step_idx:
                lbl.setProperty("active", "done")
            else:
                lbl.setProperty("active", "false")
            lbl.style().unpolish(lbl)
            lbl.style().polish(lbl)

        # Update top title bar
        titles = [
            self.t("welcome_title"),
            self.t("license_title"),
            self.t("loc_title"),
            self.t("opt_title"),
            self.t("inst_title"),
            self.t("finish_title")
        ]
        if step_idx < len(titles):
            self.lbl_top_title.setText(titles[step_idx])

    def _go_next(self):
        curr = self.stack.currentIndex()

        if curr == 0:  # Welcome -> License
            self.stack.setCurrentIndex(1)
            self.btn_back.setVisible(True)
            self._update_stepper(1)

        elif curr == 1:  # License -> Location
            if not self.radio_accept.isChecked():
                QMessageBox.warning(self, "License", "Please accept the license agreement to continue.")
                return
            self.stack.setCurrentIndex(2)
            self._update_stepper(2)

        elif curr == 2:  # Location -> Options
            dest = self.edit_dest.text().strip()
            if not dest:
                QMessageBox.warning(self, "Invalid Path", "Please select a valid installation folder.")
                return
            self.stack.setCurrentIndex(3)
            self.btn_next.setText(self.t("btn_install"))
            self._update_stepper(3)

        elif curr == 3:  # Options -> Progress (Start Installation)
            self.btn_back.setVisible(False)
            self.btn_next.setVisible(False)
            self.btn_cancel.setEnabled(False)
            self.btn_lang.setEnabled(False)
            self.stack.setCurrentIndex(4)
            self._update_stepper(4)
            self._start_installation()

        elif curr == 5:  # Finish Page -> Exit & Launch
            if self.chk_fin_launch.isChecked():
                exe_path = os.path.join(self.edit_dest.text().strip(), "SubExtract Studio.exe")
                if os.path.exists(exe_path):
                    subprocess.Popen([exe_path], cwd=self.edit_dest.text().strip())
            self.close()

    def _go_back(self):
        curr = self.stack.currentIndex()
        if curr > 0:
            target = curr - 1
            self.stack.setCurrentIndex(target)
            self._update_stepper(target)
            if target == 0:
                self.btn_back.setVisible(False)
            self.btn_next.setText(self.t("btn_next"))

    def _on_license_toggled(self):
        self.btn_next.setEnabled(self.radio_accept.isChecked())

    def _browse_destination(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            self.t("loc_title"),
            self.edit_dest.text() or self.default_dest
        )
        if folder:
            full_path = os.path.join(folder, "SubExtract Studio") if not folder.endswith("SubExtract Studio") else folder
            self.edit_dest.setText(full_path)

    def _update_disk_space(self):
        path = self.edit_dest.text().strip()
        try:
            drive = os.path.splitdrive(os.path.abspath(path))[0] or "C:"
            total, used, free = shutil.disk_usage(drive)
            free_gb = free / (1024 ** 3)
            self.lbl_space_avail.setText(self.t("space_avail").format(avail=f"{free_gb:.1f}"))
            if free_gb < 0.6:
                self.lbl_space_avail.setStyleSheet("color: #ff4d4d; font-weight: bold;")
            else:
                self.lbl_space_avail.setStyleSheet("color: #94a3b8;")
        except Exception:
            self.lbl_space_avail.setText("")

    def _start_installation(self):
        dest_dir = self.edit_dest.text().strip()
        create_desk = self.chk_desktop.isChecked()
        create_start = self.chk_startmenu.isChecked()

        self.worker = InstallWorker(dest_dir, create_desk, create_start)
        self.worker.progress_changed.connect(self._on_install_progress)
        self.worker.installation_finished.connect(self._on_install_finished)
        self.worker.start()

    def _on_install_progress(self, pct: int, status: str):
        self.progress_bar.setValue(pct)
        self.lbl_prog_status.setText(status)

    def _on_install_finished(self, success: bool, err_msg: str):
        if success:
            self.stack.setCurrentIndex(5)
            self._update_stepper(5)
            self.btn_next.setVisible(True)
            self.btn_next.setText(self.t("btn_finish"))
            self.btn_cancel.setVisible(False)
            self.chk_fin_launch.setChecked(self.chk_launch.isChecked())
        else:
            QMessageBox.critical(
                self,
                self.t("error_title"),
                self.t("error_msg").format(error=err_msg)
            )
            self.btn_cancel.setEnabled(True)
            self.btn_cancel.setText(self.t("btn_finish"))

    def _cancel_install(self):
        ret = QMessageBox.question(
            self,
            self.t("cancel_title"),
            self.t("cancel_msg"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if ret == QMessageBox.StandardButton.Yes:
            self.close()

    def _toggle_language(self):
        self.current_lang = "en" if self.current_lang == "ar" else "ar"
        self._refresh_texts()

    def _refresh_texts(self):
        self.setWindowTitle(self.t("app_name") + " — Setup")
        self.btn_lang.setText(self.t("lang_btn"))
        self.lbl_brand_name.setText(self.t("app_name"))
        self.lbl_brand_dev.setText(self.t("developer"))
        self.lbl_edition.setText(self.t("app_edition"))
        self.lbl_nav_note.setText(self.t("copyright"))

        # Stepper
        steps_keys = ["step_welcome", "step_license", "step_location", "step_options", "step_install", "step_finish"]
        for i, key in enumerate(steps_keys):
            self.step_labels[i].setText(self.t(key))

        # Page 0 (Welcome)
        self.lbl_welc_h.setText(self.t("welcome_title"))
        self.lbl_welc_b.setText(self.t("welcome_body"))

        # Page 1 (License)
        self.lbl_lic_h.setText(self.t("license_title"))
        self.lbl_lic_sub.setText(self.t("license_subtitle"))
        self.txt_license.setPlainText(self.t("license_text"))
        if self.current_lang == "ar":
            self.txt_license.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            self.txt_license.setAlignment(Qt.AlignmentFlag.AlignRight)
        else:
            self.txt_license.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            self.txt_license.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.radio_accept.setText(self.t("license_accept"))
        self.radio_decline.setText(self.t("license_decline"))

        # Page 2 (Location)
        self.lbl_loc_h.setText(self.t("loc_title"))
        self.lbl_loc_sub.setText(self.t("loc_subtitle"))
        self.lbl_loc_desc.setText(self.t("loc_desc"))
        self.btn_browse.setText(self.t("btn_browse"))
        self.lbl_space_req.setText(self.t("space_req"))
        self._update_disk_space()

        # Page 3 (Options)
        self.lbl_opt_h.setText(self.t("opt_title"))
        self.lbl_opt_sub.setText(self.t("opt_subtitle"))
        self.lbl_opt_desc.setText(self.t("opt_desc"))
        self.chk_desktop.setText(self.t("chk_desktop"))
        self.chk_startmenu.setText(self.t("chk_startmenu"))
        self.chk_launch.setText(self.t("chk_launch"))

        # Page 4 (Progress)
        self.lbl_prog_h.setText(self.t("inst_title"))
        self.lbl_prog_sub.setText(self.t("inst_subtitle"))

        # Page 5 (Finish)
        self.lbl_fin_h.setText(self.t("finish_title"))
        self.lbl_fin_b.setText(self.t("finish_body"))
        self.chk_fin_launch.setText(self.t("chk_finish_launch"))

        # Nav Buttons
        self.btn_back.setText(self.t("btn_back"))
        if self.stack.currentIndex() == 3:
            self.btn_next.setText(self.t("btn_install"))
        elif self.stack.currentIndex() == 5:
            self.btn_next.setText(self.t("btn_finish"))
        else:
            self.btn_next.setText(self.t("btn_next"))
        self.btn_cancel.setText(self.t("btn_cancel"))

        # Direction
        if self.current_lang == "ar":
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self._update_stepper(self.stack.currentIndex())

    def _apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #11141c;
            }
            #sidebarFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #161b26, stop:1 #0c0f16);
                border-right: 1px solid #232a3b;
            }
            #sidebarBrandTitle {
                color: #ffbe3b;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI', sans-serif;
            }
            #sidebarBrandSub {
                color: #94a3b8;
                font-size: 11px;
                font-family: 'Segoe UI', sans-serif;
            }
            #sidebarDivider {
                color: #232a3b;
                height: 1px;
                margin: 6px 0px;
            }
            #stepItem {
                color: #64748b;
                font-size: 12px;
                font-weight: 500;
                padding: 4px 6px;
                border-radius: 4px;
            }
            #stepItem[active="true"] {
                color: #ffbe3b;
                font-weight: bold;
                background-color: #21293a;
                border-left: 3px solid #ffbe3b;
            }
            #stepItem[active="done"] {
                color: #22c55e;
            }
            #sidebarEdition {
                color: #475569;
                font-size: 11px;
                font-weight: bold;
            }
            #rightContainer {
                background-color: #11141c;
            }
            #topBar {
                background-color: #161b26;
                border-bottom: 1px solid #232a3b;
            }
            #topBarTitle {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
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
                border-color: #ffbe3b;
            }
            #wizardStack {
                background-color: #11141c;
            }
            #pageHeading {
                color: #ffffff;
                font-size: 17px;
                font-weight: bold;
            }
            #pageSub {
                color: #94a3b8;
                font-size: 12px;
            }
            #pageBody {
                color: #cbd5e1;
                font-size: 13px;
                line-height: 1.5;
            }
            #licenseBox {
                background-color: #161b26;
                color: #e2e8f0;
                border: 1px solid #232a3b;
                border-radius: 8px;
                padding: 14px 16px;
                font-family: 'Segoe UI', 'Cairo', 'Tahoma', sans-serif;
                font-size: 12px;
                line-height: 1.6;
            }
            #radioOption {
                color: #e2e8f0;
                font-size: 13px;
                spacing: 8px;
            }
            #radioOption::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #475569;
                border-radius: 8px;
                background-color: #161b26;
            }
            #radioOption::indicator:checked {
                background-color: #ffbe3b;
                border-color: #ffbe3b;
            }
            #editPath {
                background-color: #161b26;
                color: #ffffff;
                border: 1px solid #2e374d;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }
            #editPath:focus {
                border-color: #ffbe3b;
            }
            #btnSecondary {
                background-color: #222938;
                color: #ffffff;
                border: 1px solid #333e56;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            #btnSecondary:hover {
                background-color: #2c3549;
                border-color: #ffbe3b;
            }
            #infoCard {
                background-color: #161b26;
                border: 1px solid #232a3b;
                border-radius: 6px;
            }
            #infoText {
                color: #94a3b8;
                font-size: 12px;
            }
            #chkOption {
                color: #e2e8f0;
                font-size: 13px;
                spacing: 8px;
            }
            #chkOption::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #475569;
                border-radius: 4px;
                background-color: #161b26;
            }
            #chkOption::indicator:checked {
                background-color: #ffbe3b;
                border-color: #ffbe3b;
            }
            #installProgress {
                background-color: #161b26;
                border: 1px solid #232a3b;
                border-radius: 6px;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
                height: 22px;
            }
            #installProgress::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f59e0b, stop:1 #ffbe3b);
                border-radius: 5px;
            }
            #statusDetail {
                color: #94a3b8;
                font-size: 12px;
                font-family: 'Consolas', monospace;
            }
            #navBar {
                background-color: #141822;
                border-top: 1px solid #232a3b;
            }
            #navNote {
                color: #475569;
                font-size: 11px;
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

    if hasattr(sys, 'frozen'):
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    try:
        if sys.platform == "win32":
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("noyz.subextractstudio.setup")
    except Exception:
        pass

    app = QApplication(sys.argv)
    wizard = InstallerWizard()
    wizard.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
