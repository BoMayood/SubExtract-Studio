# SubExtract Studio — Developed by NoYz
# Intellectual Property & Copyright (c) 2026 NoYz. All Rights Reserved.
# Modal Dialogs: Settings (API Test & Wipe), Find & Replace, Time Shift, About NoYz

import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QCheckBox, QSpinBox, QComboBox, QFileDialog, QMessageBox, QGroupBox,
    QFrame, QTextBrowser, QApplication
)
from core.i18n import I18n
from core.translator import test_ai_connection

class SettingsDialog(QDialog):
    """Application Settings Dialog with dedicated API key testing and security wipe."""

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.cfg = config_manager
        self.setWindowTitle(I18n.t("settings_dialog_title"))
        self.setMinimumWidth(600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # 1. AI API Configuration Group
        ai_group = QGroupBox(I18n.t("group_ai_api"))
        ai_layout = QVBoxLayout(ai_group)
        ai_layout.setSpacing(10)

        # Provider Selector
        prov_row = QHBoxLayout()
        prov_label = QLabel(I18n.t("lbl_ai_provider"))
        prov_label.setFixedWidth(130)
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["Google Gemini", "OpenAI", "Custom Endpoint"])
        current_prov = self.cfg.get("ai_provider", "Google Gemini")
        self.provider_combo.setCurrentText(current_prov)
        self.provider_combo.currentTextChanged.connect(self._on_provider_changed)
        prov_row.addWidget(prov_label)
        prov_row.addWidget(self.provider_combo)
        ai_layout.addLayout(prov_row)

        # API Key Input + Visibility Toggle
        key_row = QHBoxLayout()
        key_label = QLabel(I18n.t("lbl_ai_api_key"))
        key_label.setFixedWidth(130)
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setText(self.cfg.get("ai_api_key", ""))
        self.api_key_input.setPlaceholderText("Paste your AI API Key here (AIzaSy... or sk-...)")
        self.api_key_input.textChanged.connect(self._auto_detect_provider)
        
        self.btn_show_key = QPushButton("👁")
        self.btn_show_key.setFixedWidth(36)
        self.btn_show_key.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_show_key.clicked.connect(self._toggle_key_visibility)

        key_row.addWidget(key_label)
        key_row.addWidget(self.api_key_input)
        key_row.addWidget(self.btn_show_key)
        ai_layout.addLayout(key_row)

        # Key Action Buttons: Test Key & Security Wipe
        btn_action_row = QHBoxLayout()
        self.btn_test_key = QPushButton(I18n.t("btn_test_api_key"))
        self.btn_test_key.setObjectName("PrimaryButton")
        self.btn_test_key.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_test_key.clicked.connect(self._test_api_key)

        self.btn_clear_key = QPushButton(I18n.t("btn_clear_api_key"))
        self.btn_clear_key.setObjectName("DangerButton")
        self.btn_clear_key.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_key.clicked.connect(self._wipe_api_key)

        btn_action_row.addWidget(self.btn_test_key)
        btn_action_row.addStretch()
        btn_action_row.addWidget(self.btn_clear_key)
        ai_layout.addLayout(btn_action_row)

        # AI Model
        model_row = QHBoxLayout()
        model_label = QLabel(I18n.t("lbl_ai_model"))
        model_label.setFixedWidth(130)
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self._populate_models(self.provider_combo.currentText())
        current_model = self.cfg.get("ai_model", "gemini-3.5-flash")
        # Upgrade any deprecated models to the latest 2026 Gemini 3 series
        deprecated = {"gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-lite"}
        if current_model in deprecated:
            current_model = "gemini-3.5-flash"
        self.model_combo.setCurrentText(current_model)
        model_row.addWidget(model_label)
        model_row.addWidget(self.model_combo)
        ai_layout.addLayout(model_row)

        # Endpoint URL
        endpoint_row = QHBoxLayout()
        endpoint_label = QLabel(I18n.t("lbl_ai_endpoint"))
        endpoint_label.setFixedWidth(130)
        self.endpoint_input = QLineEdit()
        self.endpoint_input.setText(self.cfg.get("ai_endpoint", "https://generativelanguage.googleapis.com/v1beta/openai/"))
        endpoint_row.addWidget(endpoint_label)
        endpoint_row.addWidget(self.endpoint_input)
        ai_layout.addLayout(endpoint_row)

        layout.addWidget(ai_group)

        # 2. General & OCR Settings Group
        gen_group = QGroupBox(I18n.t("group_general"))
        gen_layout = QVBoxLayout(gen_group)
        gen_layout.setSpacing(10)

        # Tesseract path
        tess_row = QHBoxLayout()
        tess_label = QLabel(I18n.t("lbl_tesseract_path"))
        tess_label.setFixedWidth(130)
        self.tess_input = QLineEdit()
        self.tess_input.setText(self.cfg.get("tesseract_path", ""))
        self.tess_input.setPlaceholderText("Optional path to tesseract.exe")

        btn_tess = QPushButton(I18n.t("btn_browse_tesseract"))
        btn_tess.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_tess.clicked.connect(self._browse_tesseract)

        tess_row.addWidget(tess_label)
        tess_row.addWidget(self.tess_input)
        tess_row.addWidget(btn_tess)
        gen_layout.addLayout(tess_row)

        # Sound alerts
        self.chk_sound = QCheckBox(I18n.t("chk_sound_alerts"))
        self.chk_sound.setChecked(self.cfg.get("sound_alerts", True))
        gen_layout.addWidget(self.chk_sound)

        layout.addWidget(gen_group)

        # 3. Action Buttons
        btn_box = QHBoxLayout()
        btn_box.addStretch()

        self.btn_save = QPushButton(I18n.t("btn_save_settings"))
        self.btn_save.setObjectName("PrimaryButton")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.clicked.connect(self._save_and_close)

        self.btn_close = QPushButton(I18n.t("btn_close"))
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.clicked.connect(self.reject)

        btn_box.addWidget(self.btn_save)
        btn_box.addWidget(self.btn_close)
        layout.addLayout(btn_box)

    def _on_provider_changed(self, provider_name: str):
        self._populate_models(provider_name)
        if provider_name == "Google Gemini":
            self.endpoint_input.setText("https://generativelanguage.googleapis.com/v1beta/openai/")
        elif provider_name == "OpenAI":
            self.endpoint_input.setText("https://api.openai.com/v1/")

    def _auto_detect_provider(self, key_text: str):
        key = key_text.strip()
        if key.startswith("AIza") or key.startswith("AQ."):
            if self.provider_combo.currentText() != "Google Gemini":
                self.provider_combo.setCurrentText("Google Gemini")
        elif key.startswith("sk-") and not key.startswith("sk-or-"):
            if self.provider_combo.currentText() != "OpenAI":
                self.provider_combo.setCurrentText("OpenAI")

    def _populate_models(self, provider_name: str):
        self.model_combo.clear()
        if provider_name == "Google Gemini":
            from core.translator import GEMINI_ACTIVE_MODELS
            self.model_combo.addItems(GEMINI_ACTIVE_MODELS)
        elif provider_name == "OpenAI":
            from core.translator import OPENAI_ACTIVE_MODELS
            self.model_combo.addItems(OPENAI_ACTIVE_MODELS)
        else:
            self.model_combo.addItems([
                "gemini-3.5-flash",
                "gpt-4o-mini",
                "deepseek-chat",
                "claude-3-5-sonnet-20241022"
            ])

    def _toggle_key_visibility(self):
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_show_key.setText("🔒")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_show_key.setText("👁")

    def _test_api_key(self):
        key = self.api_key_input.text().strip()
        model = self.model_combo.currentText().strip()
        endpoint = self.endpoint_input.text().strip()

        self.btn_test_key.setEnabled(False)
        self.btn_test_key.setText(I18n.t("btn_testing_key"))
        QApplication.processEvents()

        ok, msg, models_found, best_model = test_ai_connection(key, model, endpoint)

        self.btn_test_key.setEnabled(True)
        self.btn_test_key.setText(I18n.t("btn_test_api_key"))

        # If live models were discovered, update the combo box with actual working models!
        if models_found:
            current_items = [self.model_combo.itemText(i) for i in range(self.model_combo.count())]
            for m in models_found:
                if m not in current_items:
                    self.model_combo.addItem(m)
            if best_model:
                self.model_combo.setCurrentText(best_model)
                self.cfg.set("ai_model", best_model)

        dlg_title = I18n.t("title_test_api_key")
        if ok:
            QMessageBox.information(self, dlg_title, msg)
        else:
            QMessageBox.warning(self, dlg_title, msg)

    def _wipe_api_key(self):
        reply = QMessageBox.question(
            self,
            I18n.t("title_security_wipe"),
            I18n.t("msg_security_wipe"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.api_key_input.clear()
            self.cfg.clear_api_key()
            QMessageBox.information(
                self,
                I18n.t("title_api_cleared"),
                I18n.t("msg_api_cleared")
            )

    def _browse_tesseract(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            I18n.t("title_browse_tesseract"),
            "",
            "Executable Files (*.exe);;All Files (*.*)"
        )
        if path:
            self.tess_input.setText(path)

    def _save_and_close(self):
        self.cfg.set("ai_provider", self.provider_combo.currentText())
        self.cfg.set("ai_api_key", self.api_key_input.text().strip())
        self.cfg.set("ai_model", self.model_combo.currentText().strip())
        self.cfg.set("ai_endpoint", self.endpoint_input.text().strip())
        self.cfg.set("tesseract_path", self.tess_input.text().strip())
        self.cfg.set("sound_alerts", self.chk_sound.isChecked())
        self.cfg.save()
        self.accept()


class FindReplaceDialog(QDialog):
    """Find and Replace Subtitle Text Utility Dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(I18n.t("find_replace_title"))
        self.setMinimumWidth(440)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        find_row = QHBoxLayout()
        find_lbl = QLabel(I18n.t("lbl_find_what"))
        find_lbl.setFixedWidth(110)
        self.find_input = QLineEdit()
        find_row.addWidget(find_lbl)
        find_row.addWidget(self.find_input)
        layout.addLayout(find_row)

        replace_row = QHBoxLayout()
        replace_lbl = QLabel(I18n.t("lbl_replace_with"))
        replace_lbl.setFixedWidth(110)
        self.replace_input = QLineEdit()
        replace_row.addWidget(replace_lbl)
        replace_row.addWidget(self.replace_input)
        layout.addLayout(replace_row)

        opts_row = QHBoxLayout()
        self.chk_case = QCheckBox(I18n.t("chk_match_case"))
        self.chk_whole = QCheckBox(I18n.t("chk_whole_word"))
        opts_row.addWidget(self.chk_case)
        opts_row.addWidget(self.chk_whole)
        opts_row.addStretch()
        layout.addLayout(opts_row)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_replace = QPushButton(I18n.t("btn_replace_all"))
        self.btn_replace.setObjectName("PrimaryButton")
        self.btn_replace.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_replace.clicked.connect(self.accept)

        self.btn_cancel = QPushButton(I18n.t("btn_cancel"))
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.reject)

        btn_row.addWidget(self.btn_replace)
        btn_row.addWidget(self.btn_cancel)
        layout.addLayout(btn_row)

    def get_data(self):
        return {
            "find": self.find_input.text(),
            "replace": self.replace_input.text(),
            "match_case": self.chk_case.isChecked(),
            "whole_word": self.chk_whole.isChecked()
        }


class TimeShiftDialog(QDialog):
    """Subtitle Timestamp Forward / Delay Sync Dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(I18n.t("time_shift_title"))
        self.setMinimumWidth(380)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        info_lbl = QLabel(I18n.t("lbl_shift_hint"))
        info_lbl.setWordWrap(True)
        info_lbl.setStyleSheet("color: #94a3b8; font-size: 11px;")
        layout.addWidget(info_lbl)

        spin_row = QHBoxLayout()
        spin_lbl = QLabel(I18n.t("lbl_shift_amount"))
        self.spin_shift = QSpinBox()
        self.spin_shift.setRange(-3600000, 3600000)
        self.spin_shift.setSingleStep(100)
        self.spin_shift.setValue(1000)
        self.spin_shift.setSuffix(" ms")
        spin_row.addWidget(spin_lbl)
        spin_row.addWidget(self.spin_shift)
        layout.addLayout(spin_row)

        preset_row = QHBoxLayout()
        for text, val in [("-1000ms", -1000), ("-500ms", -500), ("+500ms", 500), ("+1000ms", 1000)]:
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, v=val: self.spin_shift.setValue(v))
            preset_row.addWidget(btn)
        layout.addLayout(preset_row)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_apply = QPushButton(I18n.t("btn_apply_shift"))
        btn_apply.setObjectName("PrimaryButton")
        btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_apply.clicked.connect(self.accept)

        btn_cancel = QPushButton(I18n.t("btn_cancel"))
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)

        btn_row.addWidget(btn_apply)
        btn_row.addWidget(btn_cancel)
        layout.addLayout(btn_row)

    def get_shift_ms(self):
        return self.spin_shift.value()


class AboutDialog(QDialog):
    """About Dialog displaying NoYz copyright branding and intellectual property."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(I18n.t("about_title"))
        self.setFixedSize(520, 420)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        brand_box = QFrame()
        brand_box.setStyleSheet("background-color: #1a1e28; border: 1px solid #2f384c; border-radius: 8px; padding: 12px;")
        brand_layout = QVBoxLayout(brand_box)
        brand_layout.setSpacing(6)

        title = QLabel(I18n.t("about_heading"))
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #00a8ff;")
        
        ver = QLabel(I18n.t("about_version"))
        ver.setStyleSheet("font-size: 13px; font-weight: bold; color: #10b981;")

        cpr = QLabel(I18n.t("about_copyright"))
        cpr.setStyleSheet("font-size: 12px; color: #f59e0b; font-weight: bold;")

        brand_layout.addWidget(title)
        brand_layout.addWidget(ver)
        brand_layout.addWidget(cpr)
        layout.addWidget(brand_box)

        desc = QTextBrowser()
        desc.setPlainText(I18n.t("about_description"))
        desc.setStyleSheet("background-color: transparent; border: none; font-size: 12px; color: #cccccc;")
        layout.addWidget(desc)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_close = QPushButton(I18n.t("btn_close"))
        btn_close.setObjectName("PrimaryButton")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)
