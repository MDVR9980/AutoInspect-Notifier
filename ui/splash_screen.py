from PyQt6.QtCore import (
    Qt,
    QTimer,
    QPropertyAnimation,
    QRect,
    QEasingCurve,
    QByteArray,
    pyqtSignal
)
from PyQt6.QtGui import QColor, QPainter, QFont
from PyQt6.QtWidgets import QWidget, QGraphicsDropShadowEffect, QLabel
from PyQt6.QtSvgWidgets import QSvgWidget
from pathlib import Path


class CustomSplash(QWidget):

    finished = pyqtSignal()  # اسپلش پایان یافت و پنجره اصلی اجرا شود

    def __init__(self, logo_path):
        super().__init__()

        # تنظیمات پنجره
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(460, 380)

        # -------------------------------
        #   لوگو SVG + تغییر رنگ
        # -------------------------------
        svg_path = Path(logo_path)
        svg_data = svg_path.read_text(encoding="utf-8")

        # تمام fillهای مشکی را حذف می‌کنیم و رنگ برند را روی svg ست می‌کنیم
        svg_data = svg_data.replace('fill="#000000"', '')
        svg_data = svg_data.replace("<svg ", '<svg fill="#1E88E5" ')

        self.logo = QSvgWidget(self)
        self.logo.load(QByteArray(svg_data.encode("utf-8")))
        self.logo.setFixedSize(170, 170)
        self.logo.move((self.width() - 170) // 2, 55)

        # سایه زیر لوگو
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.logo.setGraphicsEffect(shadow)

        # -------------------------------
        #   متن بارگذاری
        # -------------------------------
        self.label = QLabel("در حال آماده‌سازی…", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFont(QFont("IRANSans", 11))
        self.label.resize(self.width(), 40)
        self.label.move(0, 260)

        # -------------------------------
        #   انیمیشن ورود (Fade + Zoom)
        # -------------------------------
        self.setWindowOpacity(0)

        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(900)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)
        self.fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        # بزرگ شدن لوگو
        start_rect = QRect(
            self.logo.x() + 10, self.logo.y() + 10,
            self.logo.width() - 20, self.logo.height() - 20
        )
        end_rect = self.logo.geometry()

        self.logo_zoom = QPropertyAnimation(self.logo, b"geometry")
        self.logo_zoom.setDuration(700)
        self.logo_zoom.setStartValue(start_rect)
        self.logo_zoom.setEndValue(end_rect)
        self.logo_zoom.setEasingCurve(QEasingCurve.Type.OutBack)

        # -------------------------------
        #   متن مرحله‌ای (سفارشی)
        # -------------------------------
        self.steps = [
            "در حال آماده‌سازی برنامه…",
            "در حال بررسی مجوز…",
            "در حال بارگذاری داده‌ها…",
            "در حال راه‌اندازی سرویس‌ها…",
            "در حال تکمیل راه‌اندازی…"
        ]
        self.step_index = 0

        # -------------------------------
        #   انیمیشن خروج (Fade Out)
        # -------------------------------
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(650)
        self.fade_out.setStartValue(1)
        self.fade_out.setEndValue(0)
        self.fade_out.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.fade_out.finished.connect(self.finished)

    # ==============================================================================
    #   شروع اسپلش
    # ==============================================================================
    def start(self):
        self.fade_in.start()
        self.logo_zoom.start()
        self._start_step_texts()

    # ==============================================================================
    #   تغییر متون مرحله‌ای
    # ==============================================================================
    def _start_step_texts(self):
        def update():
            if self.step_index < len(self.steps):
                self.label.setText(self.steps[self.step_index])
                self.step_index += 1
                QTimer.singleShot(550, update)  # تغییر متن هر نیم ثانیه
        update()

    # ==============================================================================
    #   نمایش متن دلخواه از main.py
    # ==============================================================================
    def show_message(self, text):
        self.label.setText(text)

    # ==============================================================================
    #   پایان اسپلش با انیمیشن
    # ==============================================================================
    def close_with_fade(self):
        self.fade_out.start()

    # ==============================================================================
    #   مرکز کردن روی صفحه
    # ==============================================================================
    def center_on_screen(self, app):
        screen = app.primaryScreen().availableGeometry()
        self.move(
            screen.center().x() - self.width() // 2,
            screen.center().y() - self.height() // 2
        )

    # ==============================================================================
    #   رسم پس‌زمینه گرد
    # ==============================================================================
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(255, 255, 255, 245))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 22, 22)
