# SubExtract Studio — Developed by NoYz
# Intellectual Property & Copyright (c) 2026 NoYz. All Rights Reserved.
# Advanced 5-Theme Engine (Modern Sleek, Classic Elegant, Classic Simple, Steam Gaming Style, Discord Vibe)

import os
import sys

# Base directory for assets
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECK_ICON_PATH = os.path.join(BASE_DIR, "assets", "check_white.png").replace("\\", "/")

THEMES = {
    "Modern Sleek": {
        "bg_dark": "#12151c",
        "bg_surface": "#1b202c",
        "bg_card": "#242b3b",
        "bg_input": "#171c26",
        "accent": "#00a8ff",
        "accent_hover": "#26c0ff",
        "accent_active": "#0088cc",
        "text_primary": "#ffffff",
        "text_secondary": "#94a3b8",
        "border": "#2f384c",
        "border_light": "#3b4760",
        "btn_primary_bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #00a8ff, stop:1 #0077cc)",
        "btn_primary_hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #26c0ff, stop:1 #0088dd)",
        "success": "#10b981",
        "error": "#ef4444",
        "warning": "#f59e0b"
    },
    "Steam Gaming Style": {
        "bg_dark": "#171a21",          # Valve Steam deep navy charcoal
        "bg_surface": "#1b2838",       # Steam panel blue
        "bg_card": "#212e3e",          # Steam header / elevated card
        "bg_input": "#12171f",
        "accent": "#66c0f4",          # Signature Steam electric light blue
        "accent_hover": "#80d0ff",
        "accent_active": "#4195c6",
        "text_primary": "#c7d5e0",
        "text_secondary": "#8f98a0",
        "border": "#2a475e",          # Steam signature border
        "border_light": "#385b77",
        "btn_primary_bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #47bfff, stop:1 #1a7fe0)",
        "btn_primary_hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #66cbf9, stop:1 #278ee8)",
        "success": "#a4d007",          # Steam Store green
        "error": "#d9534f",
        "warning": "#f0ad4e"
    },
    "Discord Vibe": {
        "bg_dark": "#202225",          # Discord dark background
        "bg_surface": "#2f3136",       # Discord channel list
        "bg_card": "#36393f",          # Discord chat panel
        "bg_input": "#40444b",         # Discord message input
        "accent": "#5865F2",          # Signature Discord Blurple
        "accent_hover": "#4752c4",
        "accent_active": "#3c45a5",
        "text_primary": "#ffffff",
        "text_secondary": "#dcddde",
        "border": "#4f545c",
        "border_light": "#5d6269",
        "btn_primary_bg": "#5865F2",
        "btn_primary_hover": "#4752c4",
        "success": "#57F287",          # Discord Online green
        "error": "#ED4245",            # Discord Red
        "warning": "#FEE75C"
    },
    "Classic Elegant": {
        "bg_dark": "#121215",
        "bg_surface": "#1a1a20",
        "bg_card": "#24242d",
        "bg_input": "#16161c",
        "accent": "#d4af37",          # Gold / Amber
        "accent_hover": "#e5c158",
        "accent_active": "#b89428",
        "text_primary": "#f8f9fa",
        "text_secondary": "#a0a0a8",
        "border": "#363642",
        "border_light": "#454554",
        "btn_primary_bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d4af37, stop:1 #aa8520)",
        "btn_primary_hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e5c158, stop:1 #c29929)",
        "success": "#2ecc71",
        "error": "#e74c3c",
        "warning": "#e67e22"
    },
    "Classic Simple": {
        "bg_dark": "#1e1e1e",
        "bg_surface": "#252526",
        "bg_card": "#2d2d30",
        "bg_input": "#1a1a1a",
        "accent": "#3794ff",
        "accent_hover": "#4da3ff",
        "accent_active": "#247bd4",
        "text_primary": "#cccccc",
        "text_secondary": "#858585",
        "border": "#3e3e42",
        "border_light": "#4a4a50",
        "btn_primary_bg": "#0e639c",
        "btn_primary_hover": "#1177bb",
        "success": "#4ec9b0",
        "error": "#f14c4c",
        "warning": "#cca700"
    }
}

def generate_stylesheet(theme_name: str) -> str:
    """Generates complete, lag-free Qt stylesheet for the chosen theme."""
    t = THEMES.get(theme_name, THEMES["Modern Sleek"])
    btn_bg = t.get("btn_primary_bg", t["accent"])
    btn_hover = t.get("btn_primary_hover", t["accent_hover"])
    
    return f"""
    /* SubExtract Studio Master Theme: {theme_name} */
    
    QWidget {{
        background-color: {t['bg_dark']};
        color: {t['text_primary']};
        font-family: 'Segoe UI', 'Cairo', 'Arial', sans-serif;
        font-size: 13px;
        selection-background-color: {t['accent']};
        selection-color: #ffffff;
    }}
    
    QLabel {{
        background-color: transparent;
        background: transparent;
    }}
    
    QMainWindow {{
        background-color: {t['bg_dark']};
    }}
    
    QDialog {{
        background-color: {t['bg_surface']};
        color: {t['text_primary']};
    }}
    
    /* Top Header Bar */
    QFrame#HeaderBar {{
        background-color: {t['bg_surface']};
        border-bottom: 2px solid {t['border']};
        padding: 6px;
    }}
    
    QFrame#HeaderBar QLabel {{
        background-color: transparent;
        background: transparent;
        color: {t['text_secondary']};
    }}
    
    QLabel#AppTitleLabel {{
        background-color: transparent;
        background: transparent;
        font-size: 18px;
        font-weight: bold;
        color: {t['text_primary']};
    }}
    
    QLabel#BadgeLabel {{
        background-color: {t['bg_card']};
        color: {t['accent']};
        border: 1px solid {t['accent']};
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 11px;
        font-weight: bold;
    }}
    
    /* Tab Widget & Bar */
    QTabWidget::pane {{
        border: 1px solid {t['border']};
        background-color: {t['bg_surface']};
        border-radius: 6px;
        top: -1px;
    }}
    
    QTabBar::tab {{
        background-color: {t['bg_card']};
        color: {t['text_secondary']};
        padding: 9px 22px;
        margin-right: 4px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        border: 1px solid {t['border']};
        border-bottom: none;
        font-weight: 600;
        cursor: pointer;
    }}
    
    QTabBar::tab:selected {{
        background-color: {t['bg_surface']};
        color: {t['accent']};
        border-top: 3px solid {t['accent']};
        border-bottom: 1px solid {t['bg_surface']};
    }}
    
    QTabBar::tab:hover:!selected {{
        background-color: {t['bg_input']};
        color: {t['text_primary']};
    }}
    
    /* Buttons with Rich Mouse Interaction */
    QPushButton {{
        background-color: {t['bg_card']};
        color: {t['text_primary']};
        border: 1px solid {t['border']};
        border-radius: 6px;
        padding: 6px 14px;
        font-weight: 600;
        outline: none;
        cursor: pointer;
    }}
    
    QPushButton:hover {{
        background-color: {t['border_light']};
        border-color: {t['accent']};
        color: #ffffff;
    }}
    
    QPushButton:pressed {{
        background-color: {t['bg_input']};
        border-color: {t['accent_active']};
        padding-top: 7px;
        padding-left: 15px;
    }}
    
    QPushButton:disabled {{
        background-color: {t['bg_input']};
        color: {t['text_secondary']};
        border-color: {t['border']};
    }}
    
    /* Primary Action Buttons (Glow and Interactive) */
    QPushButton#PrimaryButton {{
        background: {btn_bg};
        color: #ffffff;
        border: 1px solid {t['accent']};
        border-radius: 6px;
        font-weight: bold;
        padding: 8px 20px;
        font-size: 13px;
        cursor: pointer;
    }}
    
    QPushButton#PrimaryButton:hover {{
        background: {btn_hover};
        border-color: #ffffff;
    }}
    
    QPushButton#PrimaryButton:pressed {{
        background-color: {t['accent_active']};
        padding-top: 9px;
        padding-left: 21px;
    }}
    
    QPushButton#SecondaryAction {{
        background-color: {t['bg_surface']};
        color: {t['accent']};
        border: 1px solid {t['accent']};
        border-radius: 6px;
        font-weight: 600;
        padding: 8px 16px;
        cursor: pointer;
    }}
    
    QPushButton#SecondaryAction:hover {{
        background-color: {t['bg_card']};
        border-color: {t['accent_hover']};
        color: #ffffff;
    }}
    
    QPushButton#DangerButton {{
        background-color: #8b0000;
        color: #ffffff;
        border: 1px solid {t['error']};
        border-radius: 6px;
        cursor: pointer;
    }}
    
    QPushButton#DangerButton:hover {{
        background-color: {t['error']};
    }}
    
    /* Inputs & Comboboxes */
    QLineEdit, QSpinBox, QComboBox {{
        background-color: {t['bg_input']};
        color: {t['text_primary']};
        border: 1px solid {t['border']};
        border-radius: 5px;
        padding: 6px 10px;
        min-height: 22px;
    }}
    
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
        border: 1px solid {t['accent']};
    }}
    
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 28px;
        border-left: 1px solid {t['border']};
        background-color: transparent;
    }}
    
    QComboBox::drop-down:hover {{
        background-color: {t['bg_card']};
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid {t['text_secondary']};
        width: 0px;
        height: 0px;
    }}
    
    QComboBox::down-arrow:hover {{
        border-top-color: {t['accent']};
    }}
    
    QComboBox::down-arrow:on {{
        border-top: none;
        border-bottom: 6px solid {t['accent']};
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {t['bg_surface']};
        color: {t['text_primary']};
        border: 1px solid {t['border']};
        selection-background-color: {t['accent']};
        selection-color: #ffffff;
        padding: 4px;
    }}
    
    /* Tables */
    QTableWidget {{
        background-color: {t['bg_surface']};
        alternate-background-color: {t['bg_card']};
        color: {t['text_primary']};
        border: 1px solid {t['border']};
        border-radius: 6px;
        gridline-color: {t['border']};
    }}
    
    QHeaderView::section {{
        background-color: {t['bg_card']};
        color: {t['text_secondary']};
        padding: 7px;
        border: none;
        border-right: 1px solid {t['border']};
        border-bottom: 2px solid {t['border']};
        font-weight: bold;
    }}
    
    QTableWidget::item:selected {{
        background-color: {t['accent']};
        color: #ffffff;
    }}
    
    /* Checkboxes with Crisp Checkmark Icon (No more solid block) */
    QCheckBox {{
        spacing: 8px;
        color: {t['text_primary']};
        cursor: pointer;
    }}
    
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 1px solid {t['border_light']};
        border-radius: 4px;
        background-color: {t['bg_input']};
    }}
    
    QCheckBox::indicator:hover {{
        border-color: {t['accent']};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {t['accent']};
        border-color: {t['accent']};
        image: url("{CHECK_ICON_PATH}");
    }}
    
    /* Group Boxes */
    QGroupBox {{
        background-color: {t['bg_surface']};
        border: 1px solid {t['border']};
        border-radius: 6px;
        margin-top: 14px;
        padding-top: 14px;
        font-weight: bold;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 8px;
        color: {t['accent']};
    }}
    
    /* Progress Bar */
    QProgressBar {{
        background-color: {t['bg_input']};
        border: 1px solid {t['border']};
        border-radius: 6px;
        text-align: center;
        color: #ffffff;
        font-weight: bold;
        height: 18px;
    }}
    
    QProgressBar::chunk {{
        background-color: {t['accent']};
        border-radius: 5px;
    }}
    
    /* Scrollbars */
    QScrollBar:vertical {{
        background-color: {t['bg_dark']};
        width: 10px;
        margin: 0px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {t['border_light']};
        min-height: 25px;
        border-radius: 5px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {t['accent']};
    }}
    
    QScrollBar:horizontal {{
        background-color: {t['bg_dark']};
        height: 10px;
        margin: 0px;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {t['border_light']};
        min-width: 25px;
        border-radius: 5px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {t['accent']};
    }}
    
    QScrollBar::add-line, QScrollBar::sub-line {{
        width: 0px;
        height: 0px;
    }}
    
    /* Status & Footer Bar */
    QStatusBar {{
        background-color: {t['bg_dark']};
        border-top: 1px solid {t['border']};
        color: {t['text_secondary']};
    }}
    
    QStatusBar QLabel {{
        color: {t['text_secondary']};
    }}
    
    /* Drag & Drop Visual Zone */
    QFrame#DropZone {{
        background-color: {t['bg_card']};
        border: 2px dashed {t['border_light']};
        border-radius: 8px;
    }}
    
    QFrame#DropZone:hover {{
        border-color: {t['accent']};
        background-color: {t['bg_surface']};
    }}
    """
