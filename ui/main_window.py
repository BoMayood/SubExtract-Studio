# SubExtract Studio — Developed by NoYz
# Intellectual Property & Copyright (c) 2026 NoYz. All Rights Reserved.
# Master Desktop Application Window & UI Architecture

import os
import re
import sys
import time
import subprocess
import winsound
from PyQt6.QtCore import Qt, QUrl, pyqtSlot, QThread, pyqtSignal, QEvent, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QFont, QKeySequence, QShortcut, QIcon, QAction, QWheelEvent
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget, QCheckBox,
    QComboBox, QSpinBox, QFileDialog, QMessageBox, QColorDialog, QSplitter,
    QFrame, QProgressBar, QTextEdit, QStatusBar, QAbstractItemView, QLineEdit,
    QScrollArea
)

from core.config_manager import ConfigManager
from core.i18n import I18n
from core.themes import THEMES, generate_stylesheet
from core.taskbar_progress import TaskbarProgress
from core.subtitle_parser import SubtitleCue, SubtitleParser
from core.translator import TranslationWorker, SUPPORTED_LANGUAGES, test_ai_connection
from core.video_processor import VideoProbe, VideoBatchWorker
from core.subtitle_downloader import MediaTitleCleaner, SubtitleDownloader
from ui.preview_widget import SubtitlePreviewWidget
from ui.dialogs import SettingsDialog, FindReplaceDialog, TimeShiftDialog, AboutDialog

VIDEO_EXTENSIONS = {".mkv", ".mp4", ".avi", ".mov", ".webm", ".ts", ".flv", ".wmv", ".m4v"}
SUBTITLE_EXTENSIONS = {".srt", ".ass", ".ssa", ".vtt"}

class OnlineSubtitleSearchWorker(QThread):
    results_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, query: str, lang_code: str = "ar", season: int = None, episode: int = None,
                 video_path: str = None, english_title: str = None, parent=None):
        super().__init__(parent)
        self.query = query
        self.lang_code = lang_code
        self.season = season
        self.episode = episode
        self.video_path = video_path
        self.english_title = english_title

    def run(self):
        try:
            results = SubtitleDownloader.search(
                self.query, self.lang_code, self.season, self.episode,
                video_path=self.video_path, english_title=self.english_title
            )
            self.results_ready.emit(results)
        except Exception as e:
            self.error_occurred.emit(str(e))

class OnlineSubtitleDownloadWorker(QThread):
    download_success = pyqtSignal(dict)
    download_failed = pyqtSignal(str)

    def __init__(self, download_url: str, save_path: str, row_index: int = -1, parent=None):
        super().__init__(parent)
        self.download_url = download_url
        self.save_path = save_path
        self.row_index = row_index

    def run(self):
        try:
            res = SubtitleDownloader.download_and_verify(self.download_url, self.save_path)
            res["row_index"] = self.row_index
            self.download_success.emit(res)
        except Exception as e:
            self.download_failed.emit(str(e))

class HoverScrollStrip(QScrollArea):
    """
    Interactive horizontal strip designed to prevent widget squishing and text truncation.
    When the window is narrow or resized smaller:
    - Moving the mouse across the strip smoothly pans and glides the strip into view.
    - Hovering over any partially visible or hidden widget automatically glides it into full view.
    - Mouse wheel smoothly scrolls horizontally.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        self.setFixedHeight(50)

        self._anim = QPropertyAnimation(self.horizontalScrollBar(), b"value")
        self._anim.setDuration(240)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:horizontal {
                height: 4px;
                background: rgba(0, 0, 0, 0.12);
                border-radius: 2px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: rgba(255, 255, 255, 0.22);
                min-width: 28px;
                border-radius: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #3B82F6;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
                background: transparent;
            }
        """)

    def smooth_scroll_to(self, target_val: int):
        max_v = self.horizontalScrollBar().maximum()
        target_val = max(0, min(max_v, int(target_val)))
        if self._anim.state() == QPropertyAnimation.State.Running:
            self._anim.stop()
        self._anim.setStartValue(self.horizontalScrollBar().value())
        self._anim.setEndValue(target_val)
        self._anim.start()

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y() or event.angleDelta().x()
        self.smooth_scroll_to(self.horizontalScrollBar().value() - delta)
        event.accept()

    def _handle_hover_scroll(self, x: float):
        max_s = self.horizontalScrollBar().maximum()
        if max_s <= 0:
            return
        w = max(1, self.viewport().width())
        # Smooth directional glide when mouse is near viewport edges
        if x > w * 0.70:
            ratio = (x - w * 0.70) / (w * 0.30)
            target = min(max_s, self.horizontalScrollBar().value() + int(ratio * 120))
            self.smooth_scroll_to(target)
        elif x < w * 0.30:
            ratio = (w * 0.30 - x) / (w * 0.30)
            target = max(0, self.horizontalScrollBar().value() - int(ratio * 120))
            self.smooth_scroll_to(target)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        x = event.position().x() if hasattr(event, "position") else event.x()
        self._handle_hover_scroll(x)

    def make_widget_smoothly_visible(self, widget: QWidget):
        if not widget or not self.widget():
            return
        w_rect = widget.geometry()
        val = self.horizontalScrollBar().value()
        vp_w = self.viewport().width()
        left = w_rect.left() - 20
        right = w_rect.right() + 20
        if left < val:
            self.smooth_scroll_to(left)
        elif right > val + vp_w:
            self.smooth_scroll_to(right - vp_w)

    def register_child(self, w: QWidget):
        if w:
            w.installEventFilter(self)
            w.setMouseTracking(True)

    def eventFilter(self, watched, event):
        if event.type() in [QEvent.Type.Enter, QEvent.Type.FocusIn]:
            if isinstance(watched, QWidget):
                self.make_widget_smoothly_visible(watched)
        elif event.type() == QEvent.Type.MouseMove:
            if isinstance(watched, QWidget):
                g_pos = watched.mapToGlobal(event.pos())
                l_pos = self.viewport().mapFromGlobal(g_pos)
                self._handle_hover_scroll(l_pos.x())
        return super().eventFilter(watched, event)


class MainWindow(QMainWindow):
    """SubExtract Studio Master Desktop Application Window."""

    def __init__(self):
        super().__init__()
        self.cfg = ConfigManager()
        self.taskbar = TaskbarProgress()

        # Initialize Localization
        current_lang = self.cfg.get("language", "ar")  # Default to Arabic if preferred or saved
        I18n.set_language(current_lang)

        # Active Data
        self.video_queue = []
        self.subtitle_queue = []
        self.active_cues = []
        self.active_sub_path = ""
        self.video_worker = None
        self.sub_worker = None

        self.init_window()
        self.init_ui()
        self.init_shortcuts()
        self.apply_theme(self.cfg.get("theme", "Steam Gaming Style"))
        self.apply_language_direction(current_lang)
        self.restore_session()

    def init_window(self):
        self.setWindowTitle(I18n.t("app_title"))
        self.resize(1280, 850)
        self.setMinimumSize(980, 680)
        self.setAcceptDrops(True)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(8)

        # 1. Top Branding Header Bar
        header = self._build_header_bar()
        main_layout.addWidget(header)

        # 2. Main Dual Mode Tabs
        self.tabs = QTabWidget()
        self.video_tab = self._build_video_mode_tab()
        self.subtitle_tab = self._build_subtitle_mode_tab()
        self.online_tab = self._build_online_search_tab()
        self.tabs.addTab(self.video_tab, I18n.t("tab_video_mode"))
        self.tabs.addTab(self.subtitle_tab, I18n.t("tab_subtitle_mode"))
        self.tabs.addTab(self.online_tab, I18n.t("tab_online_search"))
        main_layout.addWidget(self.tabs, stretch=1)

        # 3. Status Console & Progress Bar
        bottom_box = self._build_bottom_console()
        main_layout.addWidget(bottom_box)

        # 4. Status Bar & Footer Branding
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_lbl = QLabel(I18n.t("status_ready"))
        self.status_bar.addWidget(self.status_lbl, 1)

        self.footer_branding = QLabel(I18n.t("footer_text"))
        self.footer_branding.setStyleSheet("color: #66c0f4; font-weight: bold; padding-right: 12px;")
        self.status_bar.addPermanentWidget(self.footer_branding)

    def _build_header_bar(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("HeaderBar")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(12)

        # Title & NoYz Copyright Badge
        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        row1 = QHBoxLayout()
        row1.setSpacing(8)

        self.header_title = QLabel(I18n.t("header_title"))
        self.header_title.setObjectName("AppTitleLabel")
        self.badge = QLabel(I18n.t("branding_badge"))
        self.badge.setObjectName("BadgeLabel")

        row1.addWidget(self.header_title)
        row1.addWidget(self.badge)
        row1.addStretch()

        self.header_sub = QLabel(I18n.t("header_subtitle"))
        self.header_sub.setStyleSheet("color: #8f98a0; font-size: 11px;")
        title_box.addLayout(row1)
        title_box.addWidget(self.header_sub)
        layout.addLayout(title_box)

        layout.addStretch()

        # Theme Selector
        theme_box = QHBoxLayout()
        self.lbl_theme = QLabel(I18n.t("theme_selector"))
        self.lbl_theme.setStyleSheet("background: transparent; background-color: transparent; border: none;")
        self.theme_combo = QComboBox()
        self.theme_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_combo.addItems(list(THEMES.keys()))
        self.theme_combo.setCurrentText(self.cfg.get("theme", "Steam Gaming Style"))
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        theme_box.addWidget(self.lbl_theme)
        theme_box.addWidget(self.theme_combo)
        layout.addLayout(theme_box)

        # Language Switcher
        lang_box = QHBoxLayout()
        self.lbl_lang = QLabel(I18n.t("lang_selector"))
        self.lbl_lang.setStyleSheet("background: transparent; background-color: transparent; border: none;")
        self.lang_combo = QComboBox()
        self.lang_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lang_combo.addItem("العربية", "ar")
        self.lang_combo.addItem("English", "en")
        idx = 0 if self.cfg.get("language", "ar") == "ar" else 1
        self.lang_combo.setCurrentIndex(idx)
        self.lang_combo.currentIndexChanged.connect(self._on_language_changed)
        lang_box.addWidget(self.lbl_lang)
        lang_box.addWidget(self.lang_combo)
        layout.addLayout(lang_box)

        # Settings & About Buttons
        self.btn_settings = QPushButton(f"⚙ {I18n.t('btn_settings')}")
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.clicked.connect(self._open_settings)
        layout.addWidget(self.btn_settings)

        self.btn_about = QPushButton(f"ℹ {I18n.t('btn_about')}")
        self.btn_about.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_about.clicked.connect(self._open_about)
        layout.addWidget(self.btn_about)

        return frame

    # -------------------------------------------------------------
    # Mode A: Video Batch Processing Tab
    # -------------------------------------------------------------
    def _build_video_mode_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Drag & Drop Zone + Browse
        drop_frame = QFrame()
        drop_frame.setObjectName("DropZone")
        drop_layout = QHBoxLayout(drop_frame)
        drop_layout.setContentsMargins(12, 10, 12, 10)

        self.lbl_video_drop = QLabel(f"📁 {I18n.t('drag_drop_video')}")
        self.lbl_video_drop.setStyleSheet("font-size: 13px; font-weight: 500;")
        drop_layout.addWidget(self.lbl_video_drop)
        drop_layout.addStretch()

        self.btn_browse_vid = QPushButton(f"🔍 {I18n.t('btn_browse_videos')}")
        self.btn_browse_vid.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_browse_vid.clicked.connect(self._browse_videos)
        drop_layout.addWidget(self.btn_browse_vid)
        layout.addWidget(drop_frame)

        # Queue Toolbar
        queue_bar = QHBoxLayout()
        self.btn_select_all = QPushButton(I18n.t("btn_select_all"))
        self.btn_select_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_select_all.clicked.connect(lambda: self._set_all_videos_checked(True))

        self.btn_deselect_all = QPushButton(I18n.t("btn_deselect_all"))
        self.btn_deselect_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_deselect_all.clicked.connect(lambda: self._set_all_videos_checked(False))

        self.btn_remove_sel_vid = QPushButton(I18n.t("btn_remove_selected"))
        self.btn_remove_sel_vid.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_remove_sel_vid.clicked.connect(self._remove_selected_videos)

        self.btn_clear_vid_queue = QPushButton(I18n.t("btn_clear_queue"))
        self.btn_clear_vid_queue.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_vid_queue.clicked.connect(self._clear_video_queue)

        queue_bar.addWidget(self.btn_select_all)
        queue_bar.addWidget(self.btn_deselect_all)
        queue_bar.addWidget(self.btn_remove_sel_vid)
        queue_bar.addWidget(self.btn_clear_vid_queue)
        queue_bar.addStretch()
        layout.addLayout(queue_bar)

        # Video Queue Table
        self.video_table = QTableWidget(0, 6)
        self.video_table.setHorizontalHeaderLabels([
            I18n.t("col_select"),
            I18n.t("col_status"),
            I18n.t("col_filename"),
            I18n.t("col_streams"),
            I18n.t("col_duration"),
            I18n.t("col_actions")
        ])
        self.video_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.video_table.setColumnWidth(0, 60)
        self.video_table.setColumnWidth(1, 135)
        self.video_table.setColumnWidth(3, 190) # Track Selector Dropdown
        self.video_table.setColumnWidth(4, 75)
        self.video_table.setColumnWidth(5, 360) # Actions Column - Spacious, never clipped!
        self.video_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.video_table.setAlternatingRowColors(True)
        layout.addWidget(self.video_table, stretch=1)

        # Video Options Strip wrapped in interactive HoverScrollStrip
        opts_box = QFrame()
        opts_box.setStyleSheet("background-color: transparent;")
        opts_layout = QVBoxLayout(opts_box)
        opts_layout.setContentsMargins(0, 2, 0, 2)
        opts_layout.setSpacing(4)

        self.opts_scroll_strip = HoverScrollStrip()
        opts_content = QWidget()
        opts_content.setObjectName("OptsScrollContent")
        row_opts = QHBoxLayout(opts_content)
        row_opts.setContentsMargins(4, 2, 4, 2)
        row_opts.setSpacing(12)

        self.chk_burn_in = QCheckBox(I18n.t("chk_burn_in"))
        self.chk_burn_in.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chk_burn_in.setChecked(self.cfg.get("burn_in_subtitles", False))
        self.chk_burn_in.setToolTip(I18n.t("chk_burn_in"))
        self.chk_burn_in.toggled.connect(lambda v: self.cfg.set("burn_in_subtitles", v))

        self.chk_save_beside = QCheckBox(I18n.t("chk_save_beside"))
        self.chk_save_beside.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chk_save_beside.setChecked(self.cfg.get("save_beside_source", True))
        self.chk_save_beside.setToolTip(I18n.t("chk_save_beside"))
        self.chk_save_beside.toggled.connect(self._toggle_output_dir_options)

        self.btn_output_dir = QPushButton(I18n.t("btn_select_output_dir"))
        self.btn_output_dir.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_output_dir.setEnabled(not self.chk_save_beside.isChecked())
        self.btn_output_dir.setMinimumWidth(150)
        self.btn_output_dir.setToolTip(I18n.t("btn_select_output_dir"))
        self.btn_output_dir.clicked.connect(self._choose_output_directory)

        # Target Translation Language for Video Extraction
        self.lbl_video_target_lang = QLabel(f"🌐 {I18n.t('lbl_target_lang')}")
        self.lbl_video_target_lang.setStyleSheet("font-weight: 600;")
        self.video_target_lang_combo = QComboBox()
        self.video_target_lang_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.video_target_lang_combo.setMinimumWidth(160)
        for code, name in SUPPORTED_LANGUAGES:
            self.video_target_lang_combo.addItem(name, code)
        cur_target = self.cfg.get("target_language", "ar")
        idx = self.video_target_lang_combo.findData(cur_target)
        if idx >= 0:
            self.video_target_lang_combo.setCurrentIndex(idx)
        self.video_target_lang_combo.setToolTip(self.video_target_lang_combo.currentText())
        self.video_target_lang_combo.currentIndexChanged.connect(self._on_video_target_lang_changed)
        self.video_target_lang_combo.currentIndexChanged.connect(
            lambda: self.video_target_lang_combo.setToolTip(self.video_target_lang_combo.currentText())
        )

        # Translation Engine Selector for Video Mode
        self.lbl_video_engine = QLabel(f"⚡ {I18n.t('lbl_engine')}")
        self.lbl_video_engine.setStyleSheet("font-weight: 600;")
        self.video_engine_combo = QComboBox()
        self.video_engine_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.video_engine_combo.setMinimumWidth(155)
        self.video_engine_combo.addItem("Google Translate", "Google Translate")
        self.video_engine_combo.addItem("AI Translation", "AI Translation")
        cur_eng = self.cfg.get("translation_engine", "Google Translate")
        idx_e = self.video_engine_combo.findData(cur_eng)
        if idx_e >= 0:
            self.video_engine_combo.setCurrentIndex(idx_e)
        self.video_engine_combo.setToolTip(self.video_engine_combo.currentText())
        self.video_engine_combo.currentIndexChanged.connect(self._on_video_engine_changed)
        self.video_engine_combo.currentIndexChanged.connect(
            lambda: self.video_engine_combo.setToolTip(self.video_engine_combo.currentText())
        )

        # Subtitle Output Format Selector
        self.lbl_output_format = QLabel(f"📄 {I18n.t('lbl_output_format')}")
        self.lbl_output_format.setStyleSheet("font-weight: 600;")
        self.output_format_combo = QComboBox()
        self.output_format_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.output_format_combo.setMinimumWidth(175)
        self.output_format_combo.addItem(".srt (Player Colors)", ".srt")
        self.output_format_combo.addItem(".ass (Full Styles & Fonts)", ".ass")
        cur_fmt = self.cfg.get("output_format", ".srt")
        idx_f = self.output_format_combo.findData(cur_fmt)
        if idx_f >= 0:
            self.output_format_combo.setCurrentIndex(idx_f)
        self.output_format_combo.setToolTip(self.output_format_combo.currentText())
        self.output_format_combo.currentIndexChanged.connect(
            lambda: self.cfg.set("output_format", self.output_format_combo.currentData())
        )
        self.output_format_combo.currentIndexChanged.connect(
            lambda: self.output_format_combo.setToolTip(self.output_format_combo.currentText())
        )

        row_opts.addWidget(self.chk_burn_in)
        row_opts.addSpacing(10)
        row_opts.addWidget(self.chk_save_beside)
        row_opts.addWidget(self.btn_output_dir)
        row_opts.addSpacing(12)
        row_opts.addWidget(self.lbl_output_format)
        row_opts.addWidget(self.output_format_combo)
        row_opts.addSpacing(12)
        row_opts.addWidget(self.lbl_video_engine)
        row_opts.addWidget(self.video_engine_combo)
        row_opts.addSpacing(12)
        row_opts.addWidget(self.lbl_video_target_lang)
        row_opts.addWidget(self.video_target_lang_combo)
        row_opts.addStretch()

        # Register child widgets for responsive hover glide
        for w in [self.chk_burn_in, self.chk_save_beside, self.btn_output_dir,
                  self.lbl_output_format, self.output_format_combo,
                  self.lbl_video_engine, self.video_engine_combo,
                  self.lbl_video_target_lang, self.video_target_lang_combo]:
            self.opts_scroll_strip.register_child(w)

        self.opts_scroll_strip.setWidget(opts_content)
        opts_layout.addWidget(self.opts_scroll_strip)

        # Interactive Primary Buttons: Extract & Translate vs Extract Only
        action_bar = QHBoxLayout()
        action_bar.setSpacing(10)

        # Primary Button 1: Extract & Translate Directly
        self.btn_extract_and_translate = QPushButton(I18n.t("btn_extract_and_translate"))
        self.btn_extract_and_translate.setObjectName("PrimaryButton")
        self.btn_extract_and_translate.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_extract_and_translate.setMinimumHeight(40)
        self.btn_extract_and_translate.clicked.connect(lambda: self._start_video_batch_processing(mode="extract_and_translate"))

        # Secondary Button 2: Extract Subtitles Only
        self.btn_extract_only = QPushButton(I18n.t("btn_extract_only"))
        self.btn_extract_only.setObjectName("SecondaryAction")
        self.btn_extract_only.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_extract_only.setMinimumHeight(40)
        self.btn_extract_only.clicked.connect(lambda: self._start_video_batch_processing(mode="extract_only"))

        # Cancel Button
        self.btn_cancel_video = QPushButton(I18n.t("btn_cancel"))
        self.btn_cancel_video.setObjectName("DangerButton")
        self.btn_cancel_video.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel_video.setMinimumHeight(40)
        self.btn_cancel_video.setEnabled(False)
        self.btn_cancel_video.clicked.connect(self._cancel_video_batch)

        action_bar.addWidget(self.btn_extract_and_translate, stretch=4)
        action_bar.addWidget(self.btn_extract_only, stretch=3)
        action_bar.addWidget(self.btn_cancel_video, stretch=1)
        opts_layout.addLayout(action_bar)

        layout.addWidget(opts_box)
        return widget

    # -------------------------------------------------------------
    # Mode B: Standalone Subtitle Studio Tab
    # -------------------------------------------------------------
    def _build_subtitle_mode_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        splitter = QSplitter(Qt.Orientation.Vertical)

        # Top Section: Subtitle Queue
        top_container = QWidget()
        top_layout = QVBoxLayout(top_container)
        top_layout.setContentsMargins(0, 0, 0, 4)
        top_layout.setSpacing(6)

        sub_drop = QFrame()
        sub_drop.setObjectName("DropZone")
        sub_drop_layout = QHBoxLayout(sub_drop)
        sub_drop_layout.setContentsMargins(12, 8, 12, 8)

        self.lbl_sub_drop = QLabel(f"📄 {I18n.t('drag_drop_subs')}")
        self.lbl_sub_drop.setStyleSheet("font-size: 13px; font-weight: 500;")
        sub_drop_layout.addWidget(self.lbl_sub_drop)
        sub_drop_layout.addStretch()

        self.btn_browse_subs = QPushButton(f"🔍 {I18n.t('btn_browse_subs')}")
        self.btn_browse_subs.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_browse_subs.clicked.connect(self._browse_subtitles)
        sub_drop_layout.addWidget(self.btn_browse_subs)
        top_layout.addWidget(sub_drop)

        # Controls Strip wrapped in interactive HoverScrollStrip
        self.sub_scroll_strip = HoverScrollStrip()
        ctrl_content = QWidget()
        ctrl_content.setObjectName("SubCtrlContent")
        ctrl_bar = QHBoxLayout(ctrl_content)
        ctrl_bar.setContentsMargins(4, 2, 4, 2)
        ctrl_bar.setSpacing(10)

        self.lbl_engine = QLabel(I18n.t("lbl_engine"))
        self.engine_combo = QComboBox()
        self.engine_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.engine_combo.setMinimumWidth(155)
        self.engine_combo.addItems(["Google Translate", "AI Translation"])
        self.engine_combo.setCurrentText(self.cfg.get("translation_engine", "Google Translate"))
        self.engine_combo.setToolTip(self.engine_combo.currentText())
        self.engine_combo.currentTextChanged.connect(self._on_sub_engine_changed)
        self.engine_combo.currentTextChanged.connect(lambda: self.engine_combo.setToolTip(self.engine_combo.currentText()))
        ctrl_bar.addWidget(self.lbl_engine)
        ctrl_bar.addWidget(self.engine_combo)

        self.lbl_target_lang = QLabel(I18n.t("lbl_target_lang"))
        self.target_lang_combo = QComboBox()
        self.target_lang_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.target_lang_combo.setMinimumWidth(160)
        for code, name in SUPPORTED_LANGUAGES:
            self.target_lang_combo.addItem(name, code)
        ar_idx = self.target_lang_combo.findData(self.cfg.get("target_language", "ar"))
        if ar_idx >= 0:
            self.target_lang_combo.setCurrentIndex(ar_idx)
        self.target_lang_combo.setToolTip(self.target_lang_combo.currentText())
        self.target_lang_combo.currentIndexChanged.connect(self._on_target_lang_changed)
        self.target_lang_combo.currentIndexChanged.connect(lambda: self.target_lang_combo.setToolTip(self.target_lang_combo.currentText()))
        ctrl_bar.addWidget(self.lbl_target_lang)
        ctrl_bar.addWidget(self.target_lang_combo)

        self.btn_batch_trans_sub = QPushButton(f"🌐 {I18n.t('btn_translate_all_subs')}")
        self.btn_batch_trans_sub.setObjectName("PrimaryButton")
        self.btn_batch_trans_sub.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_batch_trans_sub.setMinimumWidth(160)
        self.btn_batch_trans_sub.setToolTip(I18n.t("btn_translate_all_subs"))
        self.btn_batch_trans_sub.clicked.connect(self._start_standalone_subtitle_translation)
        ctrl_bar.addWidget(self.btn_batch_trans_sub)

        self.btn_convert_sub = QPushButton(f"🔄 {I18n.t('btn_convert_format')}")
        self.btn_convert_sub.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_convert_sub.setMinimumWidth(125)
        self.btn_convert_sub.setToolTip(I18n.t("btn_convert_format"))
        self.btn_convert_sub.clicked.connect(self._convert_active_subtitle_format)
        ctrl_bar.addWidget(self.btn_convert_sub)

        self.btn_detect_lang = QPushButton(f"🔍 {I18n.t('btn_detect_lang')}")
        self.btn_detect_lang.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_detect_lang.setMinimumWidth(125)
        self.btn_detect_lang.setToolTip(I18n.t("btn_detect_lang"))
        self.btn_detect_lang.clicked.connect(self._detect_subtitle_language)
        ctrl_bar.addWidget(self.btn_detect_lang)

        self.btn_clear_sub_queue = QPushButton(f"🗑 {I18n.t('btn_clear_sub_queue')}")
        self.btn_clear_sub_queue.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_sub_queue.setMinimumWidth(120)
        self.btn_clear_sub_queue.setToolTip(I18n.t("btn_clear_sub_queue"))
        self.btn_clear_sub_queue.clicked.connect(self._clear_subtitle_studio)
        ctrl_bar.addWidget(self.btn_clear_sub_queue)

        ctrl_bar.addStretch()

        # Register all child widgets for responsive hover glide
        for w in [self.lbl_engine, self.engine_combo, self.lbl_target_lang, self.target_lang_combo,
                  self.btn_batch_trans_sub, self.btn_convert_sub, self.btn_detect_lang, self.btn_clear_sub_queue]:
            self.sub_scroll_strip.register_child(w)

        self.sub_scroll_strip.setWidget(ctrl_content)
        top_layout.addWidget(self.sub_scroll_strip)

        splitter.addWidget(top_container)

        # Bottom Section: Editor & Preview
        bot_container = QWidget()
        bot_layout = QHBoxLayout(bot_container)
        bot_layout.setContentsMargins(0, 4, 0, 0)
        bot_layout.setSpacing(10)

        # Cues Table & Pro Tools
        editor_box = QFrame()
        editor_layout = QVBoxLayout(editor_box)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(6)

        edit_tools = QHBoxLayout()
        self.lbl_editor = QLabel(I18n.t("editor_title"))
        self.lbl_editor.setStyleSheet("font-weight: bold; color: #66c0f4;")
        edit_tools.addWidget(self.lbl_editor)
        edit_tools.addStretch()

        self.btn_find_replace = QPushButton(f"🔍 {I18n.t('btn_find_replace')}")
        self.btn_find_replace.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_find_replace.clicked.connect(self._open_find_replace)

        self.btn_time_shift = QPushButton(f"⏱ {I18n.t('btn_time_shift')}")
        self.btn_time_shift.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_time_shift.clicked.connect(self._open_time_shift)

        self.btn_save_sub = QPushButton(f"💾 {I18n.t('btn_save_subtitle')}")
        self.btn_save_sub.setObjectName("PrimaryButton")
        self.btn_save_sub.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save_sub.clicked.connect(self._save_active_subtitle)

        edit_tools.addWidget(self.btn_find_replace)
        edit_tools.addWidget(self.btn_time_shift)
        edit_tools.addWidget(self.btn_save_sub)
        editor_layout.addLayout(edit_tools)

        # Cues Table
        self.cues_table = QTableWidget(0, 4)
        self.cues_table.setHorizontalHeaderLabels([
            I18n.t("col_cue_idx"),
            I18n.t("col_cue_start"),
            I18n.t("col_cue_end"),
            I18n.t("col_cue_text")
        ])
        self.cues_table.setColumnWidth(0, 50)
        self.cues_table.setColumnWidth(1, 100)
        self.cues_table.setColumnWidth(2, 100)
        self.cues_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.cues_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.cues_table.setAlternatingRowColors(True)
        self.cues_table.itemSelectionChanged.connect(self._on_cue_selected)
        self.cues_table.itemChanged.connect(self._on_cue_item_edited)
        editor_layout.addWidget(self.cues_table, stretch=1)

        bot_layout.addWidget(editor_box, stretch=3)

        # Right Column: Simulated Live Preview & Font Styling
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        self.preview_player = SubtitlePreviewWidget()
        right_layout.addWidget(self.preview_player)

        style_card = self._build_style_customizer_card()
        right_layout.addWidget(style_card)

        bot_layout.addWidget(right_panel, stretch=2)
        splitter.addWidget(bot_container)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)

        layout.addWidget(splitter)
        return widget

    def _build_style_customizer_card(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet("background-color: #171c26; border: 1px solid #2f384c; border-radius: 8px; padding: 6px;")
        layout = QVBoxLayout(card)
        layout.setSpacing(6)

        title_row = QHBoxLayout()
        self.lbl_style_title = QLabel(f"🎨 {I18n.t('style_panel_title')}")
        self.lbl_style_title.setStyleSheet("font-weight: bold; color: #66c0f4;")
        title_row.addWidget(self.lbl_style_title)
        title_row.addStretch()

        self.btn_reset_styles = QPushButton(I18n.t("btn_reset_styles"))
        self.btn_reset_styles.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset_styles.setStyleSheet("font-size: 11px; padding: 3px 8px;")
        self.btn_reset_styles.clicked.connect(self._reset_styles_to_default)
        title_row.addWidget(self.btn_reset_styles)
        layout.addLayout(title_row)

        f_row = QHBoxLayout()
        self.lbl_font_family = QLabel(I18n.t("lbl_font_family"))
        self.font_combo = QComboBox()
        self.font_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.font_combo.addItems([
            "Segoe UI", "Tahoma", "Arial", "Simplified Arabic", "Traditional Arabic",
            "Arabic Typesetting", "Calibri", "Verdana", "Impact", "Georgia", "Consolas"
        ])
        self.font_combo.setCurrentText(self.cfg.get("font_family", "Segoe UI"))
        self.font_combo.currentTextChanged.connect(self._update_preview_from_controls)

        self.lbl_font_size = QLabel(I18n.t("lbl_font_size"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.font_size_spin.setRange(12, 72)
        self.font_size_spin.setValue(self.cfg.get("font_size", 24))
        self.font_size_spin.valueChanged.connect(self._update_preview_from_controls)

        f_row.addWidget(self.lbl_font_family)
        f_row.addWidget(self.font_combo)
        f_row.addWidget(self.lbl_font_size)
        f_row.addWidget(self.font_size_spin)
        layout.addLayout(f_row)

        c_row = QHBoxLayout()
        self.lbl_font_color = QLabel(I18n.t("lbl_font_color"))
        self.btn_color_text = QPushButton()
        self.btn_color_text.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_color_text.setFixedSize(28, 24)
        self.current_text_color = self.cfg.get("font_color", "#FFFFFF")
        self.btn_color_text.setStyleSheet(f"background-color: {self.current_text_color}; border: 2px solid #66c0f4; border-radius: 4px;")
        self.btn_color_text.clicked.connect(self._pick_text_color)

        # Quick Color Swatches
        self.swatch_white = QPushButton("⚪")
        self.swatch_white.setFixedSize(26, 24)
        self.swatch_white.setToolTip("White (#FFFFFF)")
        self.swatch_white.setCursor(Qt.CursorShape.PointingHandCursor)
        self.swatch_white.clicked.connect(lambda: self._set_quick_text_color("#FFFFFF"))

        self.swatch_yellow = QPushButton("🟡")
        self.swatch_yellow.setFixedSize(26, 24)
        self.swatch_yellow.setToolTip("Yellow (#FFD700)")
        self.swatch_yellow.setCursor(Qt.CursorShape.PointingHandCursor)
        self.swatch_yellow.clicked.connect(lambda: self._set_quick_text_color("#FFD700"))

        self.swatch_cyan = QPushButton("🔵")
        self.swatch_cyan.setFixedSize(26, 24)
        self.swatch_cyan.setToolTip("Cyan (#00E5FF)")
        self.swatch_cyan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.swatch_cyan.clicked.connect(lambda: self._set_quick_text_color("#00E5FF"))

        self.lbl_outline_color = QLabel(I18n.t("lbl_outline_color"))
        self.btn_color_outline = QPushButton()
        self.btn_color_outline.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_color_outline.setFixedSize(28, 24)
        self.current_outline_color = self.cfg.get("outline_color", "#000000")
        self.btn_color_outline.setStyleSheet(f"background-color: {self.current_outline_color}; border: 2px solid #555; border-radius: 4px;")
        self.btn_color_outline.clicked.connect(self._pick_outline_color)

        c_row.addWidget(self.lbl_font_color)
        c_row.addWidget(self.btn_color_text)
        c_row.addWidget(self.swatch_white)
        c_row.addWidget(self.swatch_yellow)
        c_row.addWidget(self.swatch_cyan)
        c_row.addSpacing(12)
        c_row.addWidget(self.lbl_outline_color)
        c_row.addWidget(self.btn_color_outline)
        c_row.addStretch()
        layout.addLayout(c_row)

        b_row = QHBoxLayout()
        self.chk_bold = QCheckBox(I18n.t("chk_bold"))
        self.chk_bold.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chk_bold.setChecked(self.cfg.get("font_bold", True))
        self.chk_bold.toggled.connect(self._update_preview_from_controls)

        self.chk_italic = QCheckBox(I18n.t("chk_italic"))
        self.chk_italic.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chk_italic.setChecked(self.cfg.get("font_italic", False))
        self.chk_italic.toggled.connect(self._update_preview_from_controls)

        self.lbl_alignment = QLabel(I18n.t("lbl_alignment"))
        self.align_combo = QComboBox()
        self.align_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.align_combo.addItems(["Bottom Center", "Top Center", "Middle Center", "Bottom Left", "Bottom Right"])
        self.align_combo.setCurrentText(self.cfg.get("subtitle_alignment", "Bottom Center"))
        self.align_combo.currentTextChanged.connect(self._update_preview_from_controls)

        b_row.addWidget(self.chk_bold)
        b_row.addWidget(self.chk_italic)
        b_row.addWidget(self.lbl_alignment)
        b_row.addWidget(self.align_combo)
        layout.addLayout(b_row)

        self._update_preview_from_controls()
        return card

    # -------------------------------------------------------------
    # Mode C: Online Subtitle Search & Download Tab
    # -------------------------------------------------------------
    def _build_online_search_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # 1. Drop Zone for Movie/Series video
        drop_frame = QFrame()
        drop_frame.setObjectName("DropZone")
        drop_layout = QHBoxLayout(drop_frame)
        drop_layout.setContentsMargins(12, 10, 12, 10)

        self.lbl_online_drop = QLabel(f"🎬 {I18n.t('drag_drop_online')}")
        self.lbl_online_drop.setStyleSheet("font-size: 13px; font-weight: 500;")
        drop_layout.addWidget(self.lbl_online_drop)
        drop_layout.addStretch()

        self.btn_browse_movie = QPushButton(f"🔍 {I18n.t('btn_browse_movie')}")
        self.btn_browse_movie.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_browse_movie.clicked.connect(self._browse_online_media_file)
        drop_layout.addWidget(self.btn_browse_movie)
        layout.addWidget(drop_frame)

        # 2. Search Controls Strip
        search_card = QFrame()
        search_card.setStyleSheet("background-color: transparent;")
        search_layout = QVBoxLayout(search_card)
        search_layout.setContentsMargins(0, 4, 0, 4)
        search_layout.setSpacing(6)

        row_query = QHBoxLayout()
        row_query.setSpacing(8)

        self.lbl_search_query = QLabel(I18n.t("lbl_search_query"))
        self.lbl_search_query.setStyleSheet("font-weight: 600;")

        self.online_search_input = QLineEdit()
        self.online_search_input.setPlaceholderText("e.g. Inception 2010, Breaking Bad S01E01, Sekai Saikyou...")
        self.online_search_input.returnPressed.connect(self._start_online_search)

        self.lbl_online_lang = QLabel(I18n.t("lbl_target_lang"))
        self.lbl_online_lang.setStyleSheet("font-weight: 600;")

        self.online_lang_combo = QComboBox()
        self.online_lang_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        for code, name in SUPPORTED_LANGUAGES:
            self.online_lang_combo.addItem(name, code)
        cur_target = self.cfg.get("target_language", "ar")
        idx = self.online_lang_combo.findData(cur_target)
        if idx >= 0:
            self.online_lang_combo.setCurrentIndex(idx)
        self.online_lang_combo.currentIndexChanged.connect(self._on_online_lang_changed)

        self.btn_search_online = QPushButton(f"🔍 {I18n.t('btn_search_online')}")
        self.btn_search_online.setObjectName("PrimaryButton")
        self.btn_search_online.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_search_online.setMinimumHeight(36)
        self.btn_search_online.clicked.connect(self._start_online_search)

        self.btn_clear_online_results = QPushButton(f"🗑 {I18n.t('btn_clear_online_results')}")
        self.btn_clear_online_results.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_online_results.setMinimumHeight(36)
        self.btn_clear_online_results.clicked.connect(self._clear_online_search)

        row_query.addWidget(self.lbl_search_query)
        row_query.addWidget(self.online_search_input, stretch=3)
        row_query.addWidget(self.lbl_online_lang)
        row_query.addWidget(self.online_lang_combo)
        row_query.addWidget(self.btn_search_online)
        row_query.addWidget(self.btn_clear_online_results)
        search_layout.addLayout(row_query)

        # Detected media banner (if file was dropped or selected)
        self.lbl_online_detected = QLabel("")
        self.lbl_online_detected.setStyleSheet("color: #66c0f4; font-size: 12px; font-weight: bold; padding: 2px;")
        self.lbl_online_detected.setVisible(False)
        search_layout.addWidget(self.lbl_online_detected)

        layout.addWidget(search_card)

        # 3. Results Table
        self.online_results_table = QTableWidget(0, 6)
        self.online_results_table.setHorizontalHeaderLabels([
            I18n.t("col_match"),
            I18n.t("col_release"),
            I18n.t("col_title_year"),
            I18n.t("col_lang"),
            I18n.t("col_downloads"),
            I18n.t("col_download_action")
        ])
        self.online_results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.online_results_table.setColumnWidth(0, 85)
        self.online_results_table.setColumnWidth(2, 180)
        self.online_results_table.setColumnWidth(3, 90)
        self.online_results_table.setColumnWidth(4, 140)
        self.online_results_table.setColumnWidth(5, 175)
        self.online_results_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.online_results_table.setAlternatingRowColors(True)
        layout.addWidget(self.online_results_table, stretch=1)

        self.current_online_video_path = ""
        self.online_search_results = []
        self.search_worker = None
        self.download_worker = None

        return widget

    def _on_online_lang_changed(self, idx: int):
        code = self.online_lang_combo.currentData()
        if code:
            self.cfg.set("target_language", code)
            if hasattr(self, "video_target_lang_combo"):
                v_idx = self.video_target_lang_combo.findData(code)
                if v_idx >= 0 and v_idx != self.video_target_lang_combo.currentIndex():
                    self.video_target_lang_combo.blockSignals(True)
                    self.video_target_lang_combo.setCurrentIndex(v_idx)
                    self.video_target_lang_combo.blockSignals(False)
            if hasattr(self, "target_lang_combo"):
                s_idx = self.target_lang_combo.findData(code)
                if s_idx >= 0 and s_idx != self.target_lang_combo.currentIndex():
                    self.target_lang_combo.blockSignals(True)
                    self.target_lang_combo.setCurrentIndex(s_idx)
                    self.target_lang_combo.blockSignals(False)

    def _browse_online_media_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            I18n.t("btn_browse_movie"),
            "",
            "Video Files (*.mkv *.mp4 *.avi *.mov *.webm *.ts *.flv);;All Files (*.*)"
        )
        if file:
            self._set_online_video_search_target(file)
            self._start_online_search()

    def _set_online_video_search_target(self, video_path: str):
        self.current_online_video_path = video_path
        info = MediaTitleCleaner.clean(video_path)
        self.online_search_input.setText(info["search_query"])

        detail_parts = [f"🎬 {info['clean_title']}"]
        if info.get('english_title'):
            detail_parts.append(f"({info['english_title']})")
        if info['year']:
            detail_parts.append(f"{info['year']}")
        if info['season'] is not None and info['episode'] is not None:
            detail_parts.append(f"S{info['season']:02d}E{info['episode']:02d}")

        self.lbl_online_detected.setText(f"{I18n.t('lbl_detected_media')} {' | '.join(detail_parts)}")
        self.lbl_online_detected.setVisible(True)

    def _search_online_for_video(self, video_path: str):
        self.tabs.setCurrentIndex(2)
        self._set_online_video_search_target(video_path)
        self._start_online_search()

    def _start_online_search(self):
        query = self.online_search_input.text().strip()
        if not query:
            return

        lang_code = self.online_lang_combo.currentData() or "ar"
        self.btn_search_online.setEnabled(False)
        self.status_lbl.setText(I18n.t("status_searching"))
        self.log_message("info", f"Searching online subtitles for [{query}] in [{lang_code}]...")

        season, episode, english_title = None, None, None
        video_path = None
        if self.current_online_video_path:
            info = MediaTitleCleaner.clean(self.current_online_video_path)
            season = info.get("season")
            episode = info.get("episode")
            english_title = info.get("english_title", "")
            video_path = self.current_online_video_path

        self.search_worker = OnlineSubtitleSearchWorker(
            query, lang_code, season, episode,
            video_path=video_path, english_title=english_title
        )
        self.search_worker.results_ready.connect(self._on_online_search_results)
        self.search_worker.error_occurred.connect(self._on_online_search_error)
        self.search_worker.start()

    def _on_online_search_results(self, results: list):
        self.btn_search_online.setEnabled(True)
        self.status_lbl.setText(I18n.t("status_ready"))
        self.online_search_results = results

        self.online_results_table.setRowCount(len(results))
        if not results:
            self.log_message("warning", "No online subtitles found matching this query.")
            return

        self.log_message("success", f"Found {len(results)} matching subtitle(s) online!")

        for row, item in enumerate(results):
            score = item.get("match_score", 50)
            score_item = QTableWidgetItem(f"⭐ {int(score)}%")
            score_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            score_color = "#10b981" if score >= 80 else ("#f59e0b" if score >= 60 else "#94a3b8")
            score_item.setForeground(QColor(score_color))
            self.online_results_table.setItem(row, 0, score_item)

            rel_item = QTableWidgetItem(item.get("release_name") or item.get("sub_filename"))
            rel_item.setToolTip(item.get("sub_filename"))
            self.online_results_table.setItem(row, 1, rel_item)

            title_item = QTableWidgetItem(item.get("movie_name", ""))
            title_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.online_results_table.setItem(row, 2, title_item)

            lang_item = QTableWidgetItem(item.get("language", ""))
            lang_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.online_results_table.setItem(row, 3, lang_item)

            dl_cnt = item.get("downloads", 0)
            rating = item.get("rating", 0.0)
            dl_desc = f"⬇ {dl_cnt:,}"
            if rating > 0:
                dl_desc += f"  (★ {rating:.1f})"
            dl_item = QTableWidgetItem(dl_desc)
            dl_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.online_results_table.setItem(row, 4, dl_item)

            btn_dl = QPushButton(f"⬇ {I18n.t('btn_download_verify')}")
            btn_dl.setObjectName("PrimaryButton")
            btn_dl.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_dl.setStyleSheet("padding: 3px 8px; font-size: 11px;")
            btn_dl.clicked.connect(lambda _, r=row: self._download_online_subtitle(r))
            self.online_results_table.setCellWidget(row, 5, btn_dl)

    def _on_online_search_error(self, err_msg: str):
        self.btn_search_online.setEnabled(True)
        self.status_lbl.setText(I18n.t("status_ready"))
        self.log_message("error", f"Online search failed: {err_msg}")

    def _download_online_subtitle(self, row_idx: int):
        if row_idx >= len(self.online_search_results):
            return

        item = self.online_search_results[row_idx]
        download_url = item.get("download_url")
        if not download_url:
            self.log_message("error", "No download URL available for this subtitle.")
            return

        lang_code = item.get("lang_code", "ar")
        ext = f".{item.get('format', 'srt')}"

        if self.current_online_video_path and os.path.exists(self.current_online_video_path):
            base_no_ext = os.path.splitext(self.current_online_video_path)[0]
            save_path = f"{base_no_ext}.{lang_code}{ext}"
        else:
            desktop = os.path.expanduser("~/Desktop")
            safe_name = re.sub(r'[^a-zA-Z0-9_\-\. ]', '_', item.get("sub_filename") or "subtitle.srt")
            save_path = os.path.join(desktop, safe_name)

        self.log_message("info", f"Downloading subtitle for [{item.get('movie_name')}]...")
        self.status_lbl.setText(I18n.t("status_downloading"))

        self.download_worker = OnlineSubtitleDownloadWorker(download_url, save_path, row_index=row_idx)
        self.download_worker.download_success.connect(self._on_online_download_success)
        self.download_worker.download_failed.connect(self._on_online_download_failed)
        self.download_worker.start()

    def _on_online_download_success(self, res: dict):
        save_path = res["save_path"]
        cue_count = res["cue_count"]
        row_idx = res.get("row_index", -1)

        msg = I18n.t("msg_sub_downloaded").format(count=cue_count)
        self.log_message("success", f"{msg} -> {os.path.basename(save_path)}")
        self.status_lbl.setText(I18n.t("status_ready"))

        if self.cfg.get("play_sound_alerts", True):
            try:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except Exception:
                pass

        if 0 <= row_idx < self.online_results_table.rowCount():
            cell_widget = QWidget()
            layout = QHBoxLayout(cell_widget)
            layout.setContentsMargins(2, 2, 2, 2)
            layout.setSpacing(4)
            lbl_verified = QLabel(f"✅ {I18n.t('verified_valid')}")
            lbl_verified.setStyleSheet("color: #10b981; font-weight: bold; font-size: 11px;")
            btn_open = QPushButton("📂")
            btn_open.setToolTip(I18n.t("btn_open_saved_sub"))
            btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_open.setStyleSheet("padding: 2px 6px;")
            btn_open.clicked.connect(lambda _, p=save_path: self._open_containing_folder(p))

            btn_view = QPushButton("👁")
            btn_view.setToolTip("View in Editor / Preview Player")
            btn_view.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_view.setStyleSheet("padding: 2px 6px;")
            btn_view.clicked.connect(lambda _, p=save_path: self._load_downloaded_into_editor(p))

            layout.addWidget(lbl_verified)
            layout.addWidget(btn_open)
            layout.addWidget(btn_view)
            self.online_results_table.setCellWidget(row_idx, 5, cell_widget)

        QMessageBox.information(
            self,
            "SubExtract Studio",
            f"{msg}\n\n📁 {save_path}\n⏱ {res['first_cue_time']} ➔ {res['last_cue_time']}"
        )

    def _on_online_download_failed(self, err_msg: str):
        self.status_lbl.setText(I18n.t("status_ready"))
        self.log_message("error", f"{I18n.t('msg_sub_failed')}: {err_msg}")
        QMessageBox.critical(self, "Download Failed", f"{I18n.t('msg_sub_failed')}\n{err_msg}")

    def _load_downloaded_into_editor(self, sub_path: str):
        if os.path.exists(sub_path):
            self._load_subtitles([sub_path])
            self.tabs.setCurrentIndex(1)

    def _clear_online_search(self):
        self.online_search_input.clear()
        self.online_results_table.setRowCount(0)
        self.online_search_results.clear()
        self.current_online_video_path = ""
        self.lbl_online_detected.setText("")
        self.lbl_online_detected.setVisible(False)
        self.status_lbl.setText(I18n.t("status_ready"))
        self.log_message("info", "Online subtitle search results cleared.")

    def _clear_subtitle_studio(self):
        self.subtitle_queue.clear()
        self.active_cues.clear()
        self.active_sub_path = ""
        self.cues_table.setRowCount(0)
        self.preview_player.set_subtitle_text("Sub Studio — Developed by NoYz")
        self.status_lbl.setText(I18n.t("status_ready"))
        self.log_message("info", "Subtitle workspace and queue cleared.")

    # -------------------------------------------------------------
    # Bottom Console & Status
    # -------------------------------------------------------------
    def _build_bottom_console(self) -> QWidget:
        box = QWidget()
        layout = QVBoxLayout(box)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        self.console_log = QTextEdit()
        self.console_log.setMaximumHeight(85)
        self.console_log.setReadOnly(True)
        self.console_log.setStyleSheet(
            "background-color: #12151c; border: 1px solid #282f3d; font-family: 'Consolas', monospace; font-size: 11px;"
        )
        layout.addWidget(self.console_log)
        return box

    # -------------------------------------------------------------
    # Drag & Drop Handling (Global)
    # -------------------------------------------------------------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        files = [u.toLocalFile() for u in urls if u.isLocalFile()]
        if not files:
            return

        videos = [f for f in files if os.path.splitext(f)[1].lower() in VIDEO_EXTENSIONS]
        subtitles = [f for f in files if os.path.splitext(f)[1].lower() in SUBTITLE_EXTENSIONS]

        if self.tabs.currentIndex() == 2 and videos:
            self._set_online_video_search_target(videos[0])
            self._start_online_search()
        elif videos:
            self._add_videos_to_queue(videos)
            self.tabs.setCurrentIndex(0)
        if subtitles:
            self._load_subtitles(subtitles)
            self.tabs.setCurrentIndex(1)

        event.acceptProposedAction()

    # -------------------------------------------------------------
    # Keyboard Shortcuts
    # -------------------------------------------------------------
    def init_shortcuts(self):
        sc_open = QShortcut(QKeySequence("Ctrl+O"), self)
        sc_open.activated.connect(self._handle_shortcut_open)

        sc_start = QShortcut(QKeySequence("Ctrl+Return"), self)
        sc_start.activated.connect(lambda: self._start_video_batch_processing(mode="extract_and_translate"))

        sc_del = QShortcut(QKeySequence("Delete"), self)
        sc_del.activated.connect(self._remove_selected_videos)

        sc_save = QShortcut(QKeySequence("Ctrl+S"), self)
        sc_save.activated.connect(self._save_active_subtitle)

        sc_find = QShortcut(QKeySequence("Ctrl+F"), self)
        sc_find.activated.connect(self._open_find_replace)

    def _handle_shortcut_open(self):
        if self.tabs.currentIndex() == 0:
            self._browse_videos()
        elif self.tabs.currentIndex() == 1:
            self._browse_subtitles()
        elif self.tabs.currentIndex() == 2:
            self._browse_online_media_file()

    # -------------------------------------------------------------
    # Video Batch Logic
    # -------------------------------------------------------------
    def _browse_videos(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Video Files",
            "",
            "Video Files (*.mkv *.mp4 *.avi *.mov *.webm *.ts *.flv);;All Files (*.*)"
        )
        if files:
            self._add_videos_to_queue(files)

    def _add_videos_to_queue(self, paths: list[str]):
        existing_paths = {item["path"] for item in self.video_queue}
        added_count = 0
        for path in paths:
            if path not in existing_paths and os.path.exists(path):
                meta = VideoProbe.probe_file(path)
                sub_list = meta.get("subtitles", [])
                default_track = 0
                for s_i, s in enumerate(sub_list):
                    if s.get("language") in ["ara", "ar", "arabic"]:
                        default_track = s_i
                        break
                item = {
                    "path": path,
                    "filename": os.path.basename(path),
                    "translate": True,
                    "status": "waiting",
                    "status_msg": "⏳ بانتظار البدء" if I18n.current_lang == "ar" else "⏳ Waiting",
                    "sub_streams": sub_list,
                    "selected_stream_index": default_track,
                    "duration": meta.get("duration", 0),
                    "extracted_path": "",
                    "burned_path": ""
                }
                self.video_queue.append(item)
                added_count += 1

        if added_count > 0:
            self._refresh_video_table()
            self.log_message("info", f"Added {added_count} video file(s) to queue.")

    def _refresh_video_table(self):
        self.video_table.blockSignals(True)
        self.video_table.setRowCount(len(self.video_queue))

        is_ar = I18n.current_lang == "ar"
        status_map = {
            "waiting": ("⏳ بانتظار البدء" if is_ar else "⏳ Waiting", "#94a3b8"),
            "extracting": ("🔄 جاري الاستخراج..." if is_ar else "🔄 Extracting...", "#00a8ff"),
            "extracted": ("📥 تم الاستخراج بنجاح" if is_ar else "📥 Extracted", "#10b981"),
            "translating": ("🌐 جاري الترجمة..." if is_ar else "🌐 Translating...", "#f59e0b"),
            "success": ("✅ تم الاستخراج والترجمة" if is_ar else "✅ Extracted & Translated", "#10b981"),
            "burned": ("🎬 مكتمل (حرق)" if is_ar else "🎬 Burned & Done", "#a4d007"),
            "error": ("❌ فشل" if is_ar else "❌ Error", "#ef4444")
        }

        for row, item in enumerate(self.video_queue):
            # 0: Checkbox
            chk = QCheckBox()
            chk.setCursor(Qt.CursorShape.PointingHandCursor)
            chk.setChecked(item.get("translate", True))
            chk.toggled.connect(lambda val, r=row: self._on_video_translate_toggled(r, val))
            chk_widget = QWidget()
            chk_layout = QHBoxLayout(chk_widget)
            chk_layout.addWidget(chk)
            chk_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chk_layout.setContentsMargins(0, 0, 0, 0)
            self.video_table.setCellWidget(row, 0, chk_widget)

            # 1: Status Icon with Accurate Message
            st_key = item.get("status", "waiting")
            text, color = status_map.get(st_key, ("⏳ Waiting" if not is_ar else "⏳ بانتظار البدء", "#94a3b8"))
            if st_key == "error" and item.get("status_msg"):
                text = item["status_msg"]
            status_item = QTableWidgetItem(text)
            status_item.setForeground(QColor(color))
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.video_table.setItem(row, 1, status_item)

            # 2: File Name
            name_item = QTableWidgetItem(item["filename"])
            name_item.setToolTip(item["path"])
            self.video_table.setItem(row, 2, name_item)

            # 3: Subtitle Stream Track Selector Dropdown
            streams = item.get("sub_streams", [])
            stream_combo = QComboBox()
            stream_combo.setCursor(Qt.CursorShape.PointingHandCursor)
            if streams:
                for s_i, s in enumerate(streams):
                    lang = s.get("language", "und").upper()
                    codec = s.get("codec", "")
                    title = s.get("title", "")
                    display_txt = f"#{s_i+1} [{lang}] {codec}"
                    if title and title != f"Track {s_i+1}":
                        display_txt = f"#{s_i+1} [{lang}] {title[:10]}"
                    stream_combo.addItem(display_txt, s_i)
                sel_idx = item.get("selected_stream_index", 0)
                if 0 <= sel_idx < stream_combo.count():
                    stream_combo.setCurrentIndex(sel_idx)
                stream_combo.currentIndexChanged.connect(lambda c_idx, r=row: self._on_video_stream_changed(r, c_idx))
            else:
                stream_combo.addItem("None (OCR)", 0)
                stream_combo.setEnabled(False)
            self.video_table.setCellWidget(row, 3, stream_combo)

            # 4: Duration
            sec = int(item.get("duration", 0))
            dur_str = f"{sec // 60:02d}:{sec % 60:02d}"
            dur_item = QTableWidgetItem(dur_str)
            dur_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.video_table.setItem(row, 4, dur_item)

            # 5: Action Buttons (Quick Extract & Translate + Search Online + Open Folder)
            action_widget = QWidget()
            act_layout = QHBoxLayout(action_widget)
            act_layout.setContentsMargins(4, 2, 4, 2)
            act_layout.setSpacing(6)

            btn_quick = QPushButton(f"⚡ {I18n.t('btn_quick_extract_trans')}")
            btn_quick.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_quick.setStyleSheet("padding: 3px 8px; font-size: 11px; font-weight: bold;")
            btn_quick.setToolTip(I18n.t("btn_extract_and_translate"))
            btn_quick.clicked.connect(lambda _, r=row: self._start_single_video_action(r))

            btn_search = QPushButton(f"🌐 {I18n.t('btn_search_row')}")
            btn_search.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_search.setStyleSheet("padding: 3px 8px; font-size: 11px;")
            btn_search.setToolTip(I18n.t("tab_online_search"))
            btn_search.clicked.connect(lambda _, p=item["path"]: self._search_online_for_video(p))

            btn_open = QPushButton(f"📁 {I18n.t('btn_open_folder')}")
            btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_open.setStyleSheet("padding: 3px 8px; font-size: 11px;")
            btn_open.setToolTip(I18n.t("btn_open_folder"))
            btn_open.clicked.connect(lambda _, p=item["path"]: self._open_containing_folder(p))

            act_layout.addWidget(btn_quick)
            act_layout.addWidget(btn_search)
            act_layout.addWidget(btn_open)
            self.video_table.setCellWidget(row, 5, action_widget)

        self.video_table.blockSignals(False)

    def _on_video_stream_changed(self, row: int, stream_idx: int):
        if 0 <= row < len(self.video_queue):
            self.video_queue[row]["selected_stream_index"] = stream_idx
            stream_list = self.video_queue[row].get("sub_streams", [])
            if 0 <= stream_idx < len(stream_list):
                lang = stream_list[stream_idx].get("language", "und")
                self.log_message("info", f"Selected Track #{stream_idx + 1} ({lang}) for '{self.video_queue[row]['filename']}'")

    def _on_video_translate_toggled(self, row: int, val: bool):
        if row < len(self.video_queue):
            self.video_queue[row]["translate"] = val

    def _set_all_videos_checked(self, checked: bool):
        for item in self.video_queue:
            item["translate"] = checked
        self._refresh_video_table()

    def _remove_selected_videos(self):
        selected_rows = sorted(set(idx.row() for idx in self.video_table.selectedIndexes()), reverse=True)
        for r in selected_rows:
            if r < len(self.video_queue):
                del self.video_queue[r]
        self._refresh_video_table()

    def _clear_video_queue(self):
        self.video_queue.clear()
        self._refresh_video_table()

    def _toggle_output_dir_options(self, beside_checked: bool):
        self.cfg.set("save_beside_source", beside_checked)
        self.btn_output_dir.setEnabled(not beside_checked)

    def _choose_output_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.cfg.set("custom_output_dir", dir_path)
            self.log_message("info", f"Output folder set to: {dir_path}")

    def _start_video_batch_processing(self, mode: str = "extract_and_translate"):
        """Starts batch processing with chosen mode ('extract_and_translate' or 'extract_only')."""
        if not self.video_queue:
            QMessageBox.information(self, "Queue Empty", "Please add video files before starting processing.")
            return

        if mode == "extract_and_translate":
            engine = self.video_engine_combo.currentData() if hasattr(self, "video_engine_combo") else self.cfg.get("translation_engine", "Google Translate")
            if engine == "AI Translation":
                api_key = self.cfg.get("ai_api_key", "").strip()
                if not api_key:
                    reply = QMessageBox.warning(
                        self,
                        I18n.t("settings_dialog_title"),
                        "⚠️ لم يتم تعيين مفتاح API للذكاء الاصطناعي في الإعدادات!\nهل ترغب بالتبديل تلقائياً إلى ترجمة Google المجانية السريعة والمتابعة؟\n\n(No AI API key set. Switch to free Google Translate and proceed?)",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.Yes:
                        if hasattr(self, "video_engine_combo"):
                            self.video_engine_combo.setCurrentText("Google Translate")
                        self.cfg.set("translation_engine", "Google Translate")
                    else:
                        return

        self.btn_extract_and_translate.setEnabled(False)
        self.btn_extract_only.setEnabled(False)
        self.btn_cancel_video.setEnabled(True)
        self.progress_bar.setValue(0)
        self.taskbar.set_state(self.winId(), "normal")

        self.video_worker = VideoBatchWorker(self.video_queue, self.cfg.data, mode=mode)
        self.video_worker.progress_changed.connect(self._on_worker_progress)
        self.video_worker.item_status_changed.connect(self._on_video_item_status)
        self.video_worker.item_finished.connect(self._on_video_item_finished)
        self.video_worker.log_message.connect(self.log_message)
        self.video_worker.all_completed.connect(self._on_video_batch_finished)
        self.video_worker.start()

    def _start_single_video_action(self, row: int):
        """Quickly extracts and translates a single video item from the table row."""
        if row < len(self.video_queue):
            single_item = [self.video_queue[row]]
            engine = self.video_engine_combo.currentData() if hasattr(self, "video_engine_combo") else self.cfg.get("translation_engine", "Google Translate")
            if engine == "AI Translation" and not self.cfg.get("ai_api_key", "").strip():
                reply = QMessageBox.warning(
                    self,
                    I18n.t("settings_dialog_title"),
                    "⚠️ لم يتم تعيين مفتاح API للذكاء الاصطناعي في الإعدادات!\nهل ترغب بالتبديل تلقائياً إلى ترجمة Google المجانية السريعة والمتابعة؟\n\n(No AI API key set. Switch to free Google Translate and proceed?)",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    if hasattr(self, "video_engine_combo"):
                        self.video_engine_combo.setCurrentText("Google Translate")
                    self.cfg.set("translation_engine", "Google Translate")
                else:
                    return

            self.btn_extract_and_translate.setEnabled(False)
            self.btn_cancel_video.setEnabled(True)

            self.video_worker = VideoBatchWorker(single_item, self.cfg.data, mode="extract_and_translate")
            self.video_worker.progress_changed.connect(self._on_worker_progress)
            self.video_worker.item_status_changed.connect(lambda r, st, msg: self._on_video_item_status(row, st, msg))
            self.video_worker.item_finished.connect(lambda r, ext, brn: self._on_video_item_finished(row, ext, brn))
            self.video_worker.log_message.connect(self.log_message)
            self.video_worker.all_completed.connect(self._on_video_batch_finished)
            self.video_worker.start()

    def _cancel_video_batch(self):
        if self.video_worker and self.video_worker.isRunning():
            self.video_worker.cancel()
            self.log_message("warning", "Cancelling batch processing...")

    def _on_worker_progress(self, current: int, total: int, msg: str):
        pct = int((current / max(1, total)) * 100)
        self.progress_bar.setValue(pct)
        self.status_lbl.setText(msg)
        self.taskbar.set_value(self.winId(), pct, 100)

    def _on_video_item_status(self, row: int, status_key: str, message: str):
        if row < len(self.video_queue):
            self.video_queue[row]["status"] = status_key
            self.video_queue[row]["status_msg"] = message
            self._refresh_video_table()

    def _on_video_item_finished(self, row: int, extracted_path: str, burned_path: str):
        if row < len(self.video_queue):
            self.video_queue[row]["extracted_path"] = extracted_path
            self.video_queue[row]["burned_path"] = burned_path
            if extracted_path and os.path.exists(extracted_path) and not self.active_cues:
                self._load_subtitles([extracted_path])

    def _on_video_batch_finished(self, success_count: int = 0, fail_count: int = 0):
        self.btn_extract_and_translate.setEnabled(True)
        self.btn_extract_only.setEnabled(True)
        self.btn_cancel_video.setEnabled(False)
        self.progress_bar.setValue(100)
        self.taskbar.clear(self.winId())

        if success_count == 0 and fail_count > 0:
            self.log_message("error", I18n.t("status_batch_failed"))
            QMessageBox.critical(
                self,
                I18n.t("col_status"),
                I18n.t("msg_batch_failed_desc")
            )
        elif fail_count > 0:
            msg = I18n.t("status_batch_partial").format(success=success_count, failed=fail_count)
            self.log_message("warning", msg)
            QMessageBox.warning(self, I18n.t("col_status"), msg)
        else:
            self.log_message("success", I18n.t("status_completed"))
            if self.cfg.get("sound_alerts", True):
                try:
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                except Exception:
                    pass
            QMessageBox.information(self, I18n.t("col_status"), I18n.t("status_completed"))

    # -------------------------------------------------------------
    # Mode B: Standalone Subtitle Logic & Editor
    # -------------------------------------------------------------
    def _browse_subtitles(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Subtitle Files",
            "",
            "Subtitle Files (*.srt *.ass *.ssa *.vtt);;All Files (*.*)"
        )
        if files:
            self._load_subtitles(files)

    def _load_subtitles(self, paths: list[str]):
        if not paths:
            return
        self.subtitle_queue = paths
        self.active_sub_path = paths[0]
        try:
            self.active_cues = SubtitleParser.parse_file(self.active_sub_path)
        except Exception as e:
            self.log_message("error", f"Error parsing subtitle file: {e}")
            self.active_cues = []

        if not self.active_cues:
            self.log_message("warning", f"No subtitle cues found in '{os.path.basename(self.active_sub_path)}'. The file may be empty, corrupted, or in an unsupported format.")
        else:
            self.log_message("info", f"Loaded subtitle '{os.path.basename(self.active_sub_path)}' ({len(self.active_cues)} lines).")

        self._refresh_cues_table()

        if self.active_cues:
            self.preview_player.set_subtitle_text(self.active_cues[0].text)

    def _refresh_cues_table(self):
        self.cues_table.blockSignals(True)
        self.cues_table.setRowCount(len(self.active_cues))

        for r, cue in enumerate(self.active_cues):
            idx_item = QTableWidgetItem(str(cue.index))
            idx_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            idx_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cues_table.setItem(r, 0, idx_item)

            start_item = QTableWidgetItem(cue.start_str_srt)
            start_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            start_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cues_table.setItem(r, 1, start_item)

            end_item = QTableWidgetItem(cue.end_str_srt)
            end_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            end_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cues_table.setItem(r, 2, end_item)

            text_item = QTableWidgetItem(cue.text)
            f_fam = self.cfg.get("font_family", "Segoe UI")
            f_sz = self.cfg.get("font_size", 24)
            tbl_font = QFont(f_fam, max(11, min(16, int(f_sz * 0.6))))
            tbl_font.setBold(self.cfg.get("font_bold", True))
            tbl_font.setItalic(self.cfg.get("font_italic", False))
            text_item.setFont(tbl_font)
            text_item.setForeground(QColor(self.current_text_color if hasattr(self, "current_text_color") else "#FFFFFF"))
            self.cues_table.setItem(r, 3, text_item)

        self.cues_table.blockSignals(False)

    def _on_cue_selected(self):
        selected = self.cues_table.selectedIndexes()
        if selected:
            row = selected[0].row()
            if row < len(self.active_cues):
                self.preview_player.set_subtitle_text(self.active_cues[row].text)

    def _on_cue_item_edited(self, item: QTableWidgetItem):
        row = item.row()
        col = item.column()
        if col == 3 and row < len(self.active_cues):
            self.active_cues[row].text = item.text()
            self.preview_player.set_subtitle_text(item.text())

    def _on_video_engine_changed(self, idx: int):
        val = self.video_engine_combo.currentData()
        if val:
            self.cfg.set("translation_engine", val)
            if hasattr(self, "engine_combo"):
                eng_idx = self.engine_combo.findText(val)
                if eng_idx >= 0 and eng_idx != self.engine_combo.currentIndex():
                    self.engine_combo.blockSignals(True)
                    self.engine_combo.setCurrentIndex(eng_idx)
                    self.engine_combo.blockSignals(False)

    def _on_sub_engine_changed(self, val: str):
        if val:
            self.cfg.set("translation_engine", val)
            if hasattr(self, "video_engine_combo"):
                v_idx = self.video_engine_combo.findData(val)
                if v_idx >= 0 and v_idx != self.video_engine_combo.currentIndex():
                    self.video_engine_combo.blockSignals(True)
                    self.video_engine_combo.setCurrentIndex(v_idx)
                    self.video_engine_combo.blockSignals(False)

    def _on_target_lang_changed(self, idx: int):
        code = self.target_lang_combo.currentData()
        if code:
            self.cfg.set("target_language", code)
            if hasattr(self, "video_target_lang_combo"):
                vid_idx = self.video_target_lang_combo.findData(code)
                if vid_idx >= 0 and vid_idx != self.video_target_lang_combo.currentIndex():
                    self.video_target_lang_combo.blockSignals(True)
                    self.video_target_lang_combo.setCurrentIndex(vid_idx)
                    self.video_target_lang_combo.blockSignals(False)
            if hasattr(self, "online_lang_combo"):
                on_idx = self.online_lang_combo.findData(code)
                if on_idx >= 0 and on_idx != self.online_lang_combo.currentIndex():
                    self.online_lang_combo.blockSignals(True)
                    self.online_lang_combo.setCurrentIndex(on_idx)
                    self.online_lang_combo.blockSignals(False)

    def _on_video_target_lang_changed(self, idx: int):
        code = self.video_target_lang_combo.currentData()
        if code:
            self.cfg.set("target_language", code)
            if hasattr(self, "target_lang_combo"):
                sub_idx = self.target_lang_combo.findData(code)
                if sub_idx >= 0 and sub_idx != self.target_lang_combo.currentIndex():
                    self.target_lang_combo.blockSignals(True)
                    self.target_lang_combo.setCurrentIndex(sub_idx)
                    self.target_lang_combo.blockSignals(False)
            if hasattr(self, "online_lang_combo"):
                on_idx = self.online_lang_combo.findData(code)
                if on_idx >= 0 and on_idx != self.online_lang_combo.currentIndex():
                    self.online_lang_combo.blockSignals(True)
                    self.online_lang_combo.setCurrentIndex(on_idx)
                    self.online_lang_combo.blockSignals(False)

    def _start_standalone_subtitle_translation(self):
        if not self.active_cues:
            QMessageBox.information(self, "No Subtitles", "Please load a subtitle file to translate.")
            return

        engine = self.engine_combo.currentText()
        if engine == "AI Translation":
            api_key = self.cfg.get("ai_api_key", "").strip()
            if not api_key:
                reply = QMessageBox.warning(
                    self,
                    I18n.t("settings_dialog_title"),
                    "⚠️ لم يتم تعيين مفتاح API للذكاء الاصطناعي في الإعدادات!\nهل ترغب بالتبديل تلقائياً إلى ترجمة Google المجانية السريعة والمتابعة؟\n\n(No AI API key set. Switch to free Google Translate and proceed?)",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.engine_combo.setCurrentText("Google Translate")
                    engine = "Google Translate"
                    self.cfg.set("translation_engine", "Google Translate")
                else:
                    return

        target_lang = self.target_lang_combo.currentData()
        src_lang = self.cfg.get("source_language", "auto")

        if self.active_sub_path:
            dir_name = os.path.dirname(self.active_sub_path)
            base_name = os.path.splitext(os.path.basename(self.active_sub_path))[0]
            ext = os.path.splitext(self.active_sub_path)[1]
            out_path = os.path.join(dir_name, f"{base_name}.{target_lang}{ext}")
        else:
            out_path = ""

        self.btn_batch_trans_sub.setEnabled(False)
        self.progress_bar.setValue(0)
        self.taskbar.set_state(self.winId(), "normal")

        self.sub_worker = TranslationWorker(
            cues=self.active_cues,
            engine=engine,
            source_lang=src_lang,
            target_lang=target_lang,
            config=self.cfg.data,
            output_path=out_path
        )
        self.sub_worker.progress_changed.connect(self._on_worker_progress)
        self.sub_worker.cue_translated.connect(self._on_cue_translated_live)
        self.sub_worker.batch_completed.connect(self._on_sub_translation_completed)
        self.sub_worker.error_occurred.connect(self._on_sub_translation_error)
        self.sub_worker.log_message.connect(self.log_message)
        self.sub_worker.start()

    def _on_sub_translation_error(self, err_msg: str):
        self.btn_batch_trans_sub.setEnabled(True)
        self.progress_bar.setValue(0)
        self.taskbar.clear(self.winId())
        QMessageBox.warning(self, "خطأ في الترجمة / Translation Error", f"حدث خطأ أثناء الترجمة:\n{err_msg}")

    def _on_cue_translated_live(self, cue_idx: int, translated_text: str):
        target_row = -1
        for r, cue in enumerate(self.active_cues):
            if cue.index == cue_idx:
                target_row = r
                break
        if target_row == -1 and 0 <= (cue_idx - 1) < len(self.active_cues):
            target_row = cue_idx - 1

        if 0 <= target_row < len(self.active_cues):
            self.active_cues[target_row].text = translated_text
            self.cues_table.blockSignals(True)
            self.cues_table.setItem(target_row, 3, QTableWidgetItem(translated_text))
            self.cues_table.blockSignals(False)

    def _on_sub_translation_completed(self, translated_cues: list, out_path: str):
        self.btn_batch_trans_sub.setEnabled(True)
        self.progress_bar.setValue(100)
        self.taskbar.clear(self.winId())

        if translated_cues:
            self.active_cues = translated_cues
            self._refresh_cues_table()
            if self.active_cues:
                self.preview_player.set_subtitle_text(self.active_cues[0].text)

        if self.cfg.get("sound_alerts", True):
            winsound.MessageBeep(winsound.MB_ICONASTERISK)

        QMessageBox.information(
            self,
            "Translation Complete",
            f"Successfully translated {len(translated_cues)} lines!\nSaved to: {out_path}"
        )

    def _convert_active_subtitle_format(self):
        if not self.active_cues:
            QMessageBox.information(self, "No Subtitle", "Load a subtitle file first.")
            return

        out_path, _ = QFileDialog.getSaveFileName(
            self,
            "Convert & Export Subtitle",
            "",
            "SubRip (*.srt);;Advanced SubStation (*.ass);;WebVTT (*.vtt)"
        )
        if out_path:
            save_ok = SubtitleParser.save_cues(self.active_cues, out_path, self.cfg.data)
            if save_ok:
                self.log_message("success", f"Converted & saved subtitle to: {out_path}")
                QMessageBox.information(self, "Converted", f"Subtitle converted successfully:\n{out_path}")
            else:
                self.log_message("error", f"Failed to convert subtitle: {out_path}")

    def _detect_subtitle_language(self):
        if not self.active_cues:
            QMessageBox.information(self, "No Subtitle", "Load a subtitle file first.")
            return

        detected = SubtitleParser.detect_language(self.active_cues)
        self.log_message("info", f"Detected Language: {detected}")
        QMessageBox.information(self, "Language Detection", f"Detected Language of Subtitle:\n{detected}")

    def _save_active_subtitle(self):
        if not self.active_cues:
            return

        if not self.active_sub_path:
            self._convert_active_subtitle_format()
            return

        save_ok = SubtitleParser.save_cues(self.active_cues, self.active_sub_path, self.cfg.data)
        if save_ok:
            self.log_message("success", f"Saved subtitle changes to: {self.active_sub_path}")
            QMessageBox.information(self, "Saved", f"Subtitle saved successfully to:\n{self.active_sub_path}")
        else:
            self.log_message("error", f"Failed to save subtitle: {self.active_sub_path}")

    # -------------------------------------------------------------
    # Dialogs & Pro Tools
    # -------------------------------------------------------------
    def _open_find_replace(self):
        if not self.active_cues:
            QMessageBox.information(self, "Notice", "Load a subtitle file first.")
            return

        dlg = FindReplaceDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            count, self.active_cues = SubtitleParser.find_and_replace(
                self.active_cues,
                find_str=data["find"],
                replace_str=data["replace"],
                match_case=data["match_case"],
                whole_word=data["whole_word"]
            )
            self._refresh_cues_table()
            self.log_message("info", f"Find & Replace: replaced {count} occurrence(s).")
            QMessageBox.information(self, "Find & Replace", f"Replaced {count} occurrence(s).")

    def _open_time_shift(self):
        if not self.active_cues:
            QMessageBox.information(self, "Notice", "Load a subtitle file first.")
            return

        dlg = TimeShiftDialog(self)
        if dlg.exec():
            shift_ms = dlg.get_shift_ms()
            self.active_cues = SubtitleParser.shift_timestamps(self.active_cues, shift_ms)
            self._refresh_cues_table()
            self.log_message("info", f"Shifted timestamps by {shift_ms} ms.")
            QMessageBox.information(self, "Time Shift", f"Successfully shifted all timestamps by {shift_ms} ms.")

    def _open_settings(self):
        dlg = SettingsDialog(self.cfg, self)
        dlg.exec()

    def _open_about(self):
        dlg = AboutDialog(self)
        dlg.exec()

    def _open_containing_folder(self, file_path: str):
        if not file_path:
            return
        folder = os.path.dirname(os.path.abspath(file_path))
        if os.path.exists(file_path) and sys.platform == "win32":
            subprocess.Popen(f'explorer /select,"{os.path.normpath(file_path)}"')
        elif os.path.exists(folder):
            if sys.platform == "win32":
                os.startfile(folder)
            else:
                subprocess.Popen(["xdg-open", folder])

    # -------------------------------------------------------------
    # Subtitle Styling & Font Customization
    # -------------------------------------------------------------
    def _set_quick_text_color(self, hex_color: str):
        self.current_text_color = hex_color
        self.btn_color_text.setStyleSheet(f"background-color: {self.current_text_color}; border: 2px solid #66c0f4; border-radius: 4px;")
        self.cfg.set("font_color", self.current_text_color)
        self._update_preview_from_controls()

    def _pick_text_color(self):
        color = QColorDialog.getColor(QColor(self.current_text_color), self, "Select Subtitle Text Color")
        if color.isValid():
            self.current_text_color = color.name()
            self.btn_color_text.setStyleSheet(f"background-color: {self.current_text_color}; border: 2px solid #66c0f4; border-radius: 4px;")
            self.cfg.set("font_color", self.current_text_color)
            self._update_preview_from_controls()

    def _pick_outline_color(self):
        color = QColorDialog.getColor(QColor(self.current_outline_color), self, "Select Subtitle Outline Color")
        if color.isValid():
            self.current_outline_color = color.name()
            self.btn_color_outline.setStyleSheet(f"background-color: {self.current_outline_color}; border: 2px solid #888; border-radius: 4px;")
            self.cfg.set("outline_color", self.current_outline_color)
            self._update_preview_from_controls()

    def _update_preview_from_controls(self):
        font_family = self.font_combo.currentText()
        font_size = self.font_size_spin.value()
        bold = self.chk_bold.isChecked()
        italic = self.chk_italic.isChecked()
        align = self.align_combo.currentText()

        self.cfg.set("font_family", font_family)
        self.cfg.set("font_size", font_size)
        self.cfg.set("font_bold", bold)
        self.cfg.set("font_italic", italic)
        self.cfg.set("subtitle_alignment", align)

        self.preview_player.update_styles(
            font_family=font_family,
            font_size=font_size,
            font_color=self.current_text_color,
            outline_color=self.current_outline_color,
            outline_width=2,
            bold=bold,
            italic=italic,
            alignment=align
        )

        # Update cues table editor text in real time with the selected font typography
        if hasattr(self, "cues_table") and self.cues_table.rowCount() > 0:
            tbl_font = QFont(font_family, max(11, min(16, int(font_size * 0.6))))
            tbl_font.setBold(bold)
            tbl_font.setItalic(italic)
            text_qcolor = QColor(self.current_text_color)

            self.cues_table.blockSignals(True)
            for r in range(self.cues_table.rowCount()):
                item = self.cues_table.item(r, 3)
                if item:
                    item.setFont(tbl_font)
                    item.setForeground(text_qcolor)
            self.cues_table.blockSignals(False)

    def _reset_styles_to_default(self):
        self.cfg.reset_styles_to_default()
        self.font_combo.setCurrentText(self.cfg.get("font_family", "Segoe UI"))
        self.font_size_spin.setValue(self.cfg.get("font_size", 24))
        self.current_text_color = self.cfg.get("font_color", "#FFFFFF")
        self.btn_color_text.setStyleSheet(f"background-color: {self.current_text_color}; border: 1px solid #888;")
        self.current_outline_color = self.cfg.get("outline_color", "#000000")
        self.btn_color_outline.setStyleSheet(f"background-color: {self.current_outline_color}; border: 1px solid #888;")
        self.chk_bold.setChecked(self.cfg.get("font_bold", True))
        self.chk_italic.setChecked(self.cfg.get("font_italic", False))
        self.align_combo.setCurrentText(self.cfg.get("subtitle_alignment", "Bottom Center"))
        self._update_preview_from_controls()
        self.log_message("info", I18n.t("status_styles_reset"))

    # -------------------------------------------------------------
    # Themes & Bilingual Localization
    # -------------------------------------------------------------
    def _on_theme_changed(self, theme_name: str):
        self.cfg.set("theme", theme_name)
        self.apply_theme(theme_name)
        self.log_message("info", f"Theme switched to [{theme_name}]")

    def apply_theme(self, theme_name: str):
        qss = generate_stylesheet(theme_name)
        self.setStyleSheet(qss)

    def _on_language_changed(self, index: int):
        code = self.lang_combo.currentData()
        self.cfg.set("language", code)
        I18n.set_language(code)
        self.apply_language_direction(code)
        self.retranslate_ui()
        self.log_message("info", f"Language switched to [{'Arabic (العربية)' if code == 'ar' else 'English'}]")

    def apply_language_direction(self, lang_code: str):
        # Maintain consistent Left-to-Right layout across all languages as requested
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

    def retranslate_ui(self):
        self.setWindowTitle(I18n.t("app_title"))
        self.header_title.setText(I18n.t("header_title"))
        self.badge.setText(I18n.t("branding_badge"))
        self.header_sub.setText(I18n.t("header_subtitle"))
        self.footer_branding.setText(I18n.t("footer_text"))

        self.tabs.setTabText(0, I18n.t("tab_video_mode"))
        self.tabs.setTabText(1, I18n.t("tab_subtitle_mode"))
        self.tabs.setTabText(2, I18n.t("tab_online_search"))

        self.lbl_video_drop.setText(f"📁 {I18n.t('drag_drop_video')}")
        self.btn_browse_vid.setText(f"🔍 {I18n.t('btn_browse_videos')}")
        self.btn_select_all.setText(I18n.t("btn_select_all"))
        self.btn_deselect_all.setText(I18n.t("btn_deselect_all"))
        self.btn_remove_sel_vid.setText(I18n.t("btn_remove_selected"))
        self.btn_clear_vid_queue.setText(I18n.t("btn_clear_queue"))

        self.chk_burn_in.setText(I18n.t("chk_burn_in"))
        self.chk_burn_in.setToolTip(I18n.t("chk_burn_in"))
        self.chk_save_beside.setText(I18n.t("chk_save_beside"))
        self.chk_save_beside.setToolTip(I18n.t("chk_save_beside"))
        self.btn_output_dir.setText(I18n.t("btn_select_output_dir"))
        self.btn_output_dir.setToolTip(I18n.t("btn_select_output_dir"))
        if hasattr(self, "lbl_output_format"):
            self.lbl_output_format.setText(f"📄 {I18n.t('lbl_output_format')}")
        if hasattr(self, "lbl_video_engine"):
            self.lbl_video_engine.setText(f"⚡ {I18n.t('lbl_engine')}")
        self.lbl_video_target_lang.setText(f"🌐 {I18n.t('lbl_target_lang')}")
        if hasattr(self, "output_format_combo"):
            self.output_format_combo.setToolTip(self.output_format_combo.currentText())
        if hasattr(self, "video_engine_combo"):
            self.video_engine_combo.setToolTip(self.video_engine_combo.currentText())
        if hasattr(self, "video_target_lang_combo"):
            self.video_target_lang_combo.setToolTip(self.video_target_lang_combo.currentText())
        self.btn_extract_and_translate.setText(I18n.t("btn_extract_and_translate"))
        self.btn_extract_only.setText(I18n.t("btn_extract_only"))
        self.btn_cancel_video.setText(I18n.t("btn_cancel"))

        self.lbl_sub_drop.setText(f"📄 {I18n.t('drag_drop_subs')}")
        self.btn_browse_subs.setText(f"🔍 {I18n.t('btn_browse_subs')}")
        self.lbl_engine.setText(I18n.t("lbl_engine"))
        if hasattr(self, "engine_combo"):
            self.engine_combo.setToolTip(self.engine_combo.currentText())
        self.lbl_target_lang.setText(I18n.t("lbl_target_lang"))
        if hasattr(self, "target_lang_combo"):
            self.target_lang_combo.setToolTip(self.target_lang_combo.currentText())
        self.btn_clear_sub_queue.setText(f"🗑 {I18n.t('btn_clear_sub_queue')}")
        self.btn_batch_trans_sub.setText(f"🌐 {I18n.t('btn_translate_all_subs')}")
        self.btn_convert_sub.setText(f"🔄 {I18n.t('btn_convert_format')}")
        self.btn_detect_lang.setText(f"🔍 {I18n.t('btn_detect_lang')}")

        self.lbl_online_drop.setText(f"🎬 {I18n.t('drag_drop_online')}")
        self.btn_browse_movie.setText(f"🔍 {I18n.t('btn_browse_movie')}")
        self.btn_clear_online_results.setText(f"🗑 {I18n.t('btn_clear_online_results')}")
        self.lbl_search_query.setText(I18n.t("lbl_search_query"))
        self.lbl_online_lang.setText(I18n.t("lbl_target_lang"))
        self.btn_search_online.setText(f"🔍 {I18n.t('btn_search_online')}")
        self.online_results_table.setHorizontalHeaderLabels([
            I18n.t("col_match"),
            I18n.t("col_release"),
            I18n.t("col_title_year"),
            I18n.t("col_lang"),
            I18n.t("col_downloads"),
            I18n.t("col_download_action")
        ])

        self.lbl_editor.setText(I18n.t("editor_title"))
        self.btn_find_replace.setText(f"🔍 {I18n.t('btn_find_replace')}")
        self.btn_time_shift.setText(f"⏱ {I18n.t('btn_time_shift')}")
        self.btn_save_sub.setText(f"💾 {I18n.t('btn_save_subtitle')}")

        self.lbl_style_title.setText(f"🎨 {I18n.t('style_panel_title')}")
        self.btn_reset_styles.setText(I18n.t("btn_reset_styles"))
        self.lbl_font_family.setText(I18n.t("lbl_font_family"))
        self.lbl_font_size.setText(I18n.t("lbl_font_size"))
        self.lbl_font_color.setText(I18n.t("lbl_font_color"))
        self.lbl_outline_color.setText(I18n.t("lbl_outline_color"))
        self.chk_bold.setText(I18n.t("chk_bold"))
        self.chk_italic.setText(I18n.t("chk_italic"))
        self.lbl_alignment.setText(I18n.t("lbl_alignment"))

        self.btn_settings.setText(f"⚙ {I18n.t('btn_settings')}")
        self.btn_about.setText(f"ℹ {I18n.t('btn_about')}")
        self.lbl_theme.setText(I18n.t("theme_selector"))
        self.lbl_lang.setText(I18n.t("lang_selector"))
        self.status_lbl.setText(I18n.t("status_ready"))

        self.video_table.setHorizontalHeaderLabels([
            I18n.t("col_select"),
            I18n.t("col_status"),
            I18n.t("col_filename"),
            I18n.t("col_streams"),
            I18n.t("col_duration"),
            I18n.t("col_actions")
        ])

        self.cues_table.setHorizontalHeaderLabels([
            I18n.t("col_cue_idx"),
            I18n.t("col_cue_start"),
            I18n.t("col_cue_end"),
            I18n.t("col_cue_text")
        ])

        self._refresh_video_table()

    # -------------------------------------------------------------
    # Status Logging
    # -------------------------------------------------------------
    @pyqtSlot(str, str)
    def log_message(self, level: str, message: str):
        color_map = {
            "info": "#66c0f4",
            "success": "#57F287",
            "warning": "#FEE75C",
            "error": "#ED4245"
        }
        color = color_map.get(level.lower(), "#cccccc")
        tag = level.upper()
        html = f"<span style='color: #64748b;'>[{time.strftime('%H:%M:%S')}]</span> <span style='color: {color}; font-weight: bold;'>[{tag}]</span> {message}"
        self.console_log.append(html)

    # -------------------------------------------------------------
    # Session Auto-Save & Restore
    # -------------------------------------------------------------
    def restore_session(self):
        last_videos = self.cfg.get("last_video_queue", [])
        if last_videos:
            existing = [v for v in last_videos if os.path.exists(v)]
            if existing:
                self._add_videos_to_queue(existing)

    def closeEvent(self, event):
        v_paths = [item["path"] for item in self.video_queue if os.path.exists(item["path"])]
        self.cfg.set("last_video_queue", v_paths[:20])
        self.cfg.save()
        self.taskbar.clear(self.winId())
        event.accept()
