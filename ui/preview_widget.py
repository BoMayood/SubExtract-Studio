# SubExtract Studio — Developed by NoYz
# Intellectual Property & Copyright (c) 2026 NoYz. All Rights Reserved.
# Live Subtitle Video Player Simulation Preview Widget

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPainterPath, QLinearGradient
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider

class SubtitlePreviewWidget(QWidget):
    """Renders a simulated video screen displaying styled subtitles with real-time typography."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(240)

        self.current_text = "SubExtract Studio — Professional Subtitle Engine\nDeveloped by NoYz"
        self.font_family = "Segoe UI"
        self.font_size = 24
        self.font_color = "#FFFFFF"
        self.outline_color = "#000000"
        self.outline_width = 2
        self.font_bold = True
        self.font_italic = False
        self.alignment = "Bottom Center"

    def set_subtitle_text(self, text: str):
        self.current_text = text if text.strip() else "—"
        self.update()

    def update_styles(self, font_family, font_size, font_color, outline_color, outline_width, bold, italic, alignment):
        self.font_family = font_family
        self.font_size = max(10, font_size)
        self.font_color = font_color
        self.outline_color = outline_color
        self.outline_width = outline_width
        self.font_bold = bold
        self.font_italic = italic
        self.alignment = alignment
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w = self.width()
        h = self.height()

        # 1. Draw cinematic gradient backdrop
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, QColor("#14161d"))
        grad.setColorAt(0.5, QColor("#1a1e28"))
        grad.setColorAt(1.0, QColor("#0d0e13"))
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor("#2c3444"), 1))
        painter.drawRoundedRect(0, 0, w - 1, h - 1, 8, 8)

        # 2. Draw subtle 16:9 framing aspect guides
        painter.setPen(QPen(QColor("#333f54"), 1, Qt.PenStyle.DashLine))
        margin_x = int(w * 0.05)
        margin_y = int(h * 0.08)
        painter.drawRect(margin_x, margin_y, w - 2 * margin_x, h - 2 * margin_y)

        # 3. Watermark / Preview Tag
        painter.setPen(QColor("#5a677d"))
        watermark_font = QFont("Segoe UI", 9)
        painter.setFont(watermark_font)
        painter.drawText(margin_x + 8, margin_y + 18, "SubExtract Studio | Live Preview")

        # 4. Prepare subtitle font and path
        sub_font = QFont(self.font_family, max(12, self.font_size))
        sub_font.setBold(self.font_bold)
        sub_font.setItalic(self.font_italic)
        painter.setFont(sub_font)

        # Calculate bounding box for text
        text_rect = QRectF(margin_x + 10, margin_y + 10, w - 2 * margin_x - 20, h - 2 * margin_y - 20)

        flags = Qt.TextFlag.TextWordWrap
        if "Top" in self.alignment:
            flags |= Qt.AlignmentFlag.AlignTop
        elif "Middle" in self.alignment:
            flags |= Qt.AlignmentFlag.AlignVCenter
        else:
            flags |= Qt.AlignmentFlag.AlignBottom

        if "Left" in self.alignment:
            flags |= Qt.AlignmentFlag.AlignLeft
        elif "Right" in self.alignment:
            flags |= Qt.AlignmentFlag.AlignRight
        else:
            flags |= Qt.AlignmentFlag.AlignHCenter

        # Draw high-contrast outline in all 8 directions so outline is vividly visible
        ow = max(1, int(self.outline_width))
        painter.setPen(QPen(QColor(self.outline_color)))
        for dx in range(-ow, ow + 1):
            for dy in range(-ow, ow + 1):
                if dx != 0 or dy != 0:
                    painter.drawText(text_rect.translated(dx, dy), flags, self.current_text)

        # Draw primary text
        painter.setPen(QPen(QColor(self.font_color)))
        painter.drawText(text_rect, flags, self.current_text)
