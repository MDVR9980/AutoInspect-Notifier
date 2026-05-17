from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QRect,
    QEasingCurve, QByteArray, pyqtSignal
)
from PyQt6.QtGui import QColor, QPainter, QFont
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout,
    QProgressBar, QGraphicsDropShadowEffect
)
from PyQt6.QtSvgWidgets import QSvgWidget
from datetime import datetime
from pathlib import Path


# ==========================================================
#  Detect Theme By System Time
# ==========================================================
def detect_theme():
    hour = datetime.now().hour
    if 7 <= hour < 19:
        return "light"
    return "dark"


# ==========================================================
#  Ultra Enterprise Splash
# ==========================================================
class UltraSplash(QWidget):

    finished = pyqtSignal()

    def __init__(self, logo_path):
        super().__init__()

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(480, 400)

        # ------------------ Theme ------------------
        self.theme = detect_theme()

        if self.theme == "dark":
            self.bg_color = QColor(25, 25, 25, 235)
            self.text_color = "#EAEAEA"
            self.progress_bg = "#3A3A3A"
            self.progress_fill = "#1E88E5"
        else:
            self.bg_color = QColor(255, 255, 255, 240)
            self.text_color = "#2A2A2A"
            self.progress_bg = "#E0E0E0"
            self.progress_fill = "#1E88E5"

        # ------------------ Layout ------------------
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(18)

        # ------------------ Logo ------------------
        svg_data = Path(logo_path).read_text(encoding="utf-8")
        svg_data = svg_data.replace('fill="#000000"', '')
        svg_data = svg_data.replace("<svg ", '<svg fill="#1E88E5" ')

        self.logo = QSvgWidget()
        self.logo.load(QByteArray(svg_data.encode("utf-8")))
        self.logo.setFixedSize(160, 160)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 90))
        self.logo.setGraphicsEffect(shadow)

        layout.addWidget(self.logo, alignment=Qt.AlignmentFlag.AlignCenter)

        # ------------------ Title ------------------
        self.title = QLabel("AutoInspect Notifier")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(QFont("Segoe UI", 13))
        self.title.setStyleSheet(f"color:{self.text_color};")
        layout.addWidget(self.title)

        # ------------------ Status Label ------------------
        self.label = QLabel("در حال آماده‌سازی برنامه...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFont(QFont("Segoe UI", 10))
        self.label.setStyleSheet(f"color:{self.text_color};")
        layout.addWidget(self.label)

        # ------------------ Progress Bar ------------------
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)

        self.progress.setStyleSheet(f"""
        QProgressBar {{
            background-color: {self.progress_bg};
            border-radius: 3px;
        }}
        QProgressBar::chunk {{
            background-color: {self.progress_fill};
            border-radius: 3px;
        }}
        """)
        layout.addWidget(self.progress)

        # ------------------ Fade In ------------------
        self.setWindowOpacity(0)
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(800)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)
        self.fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        # ------------------ Logo Scale Animation ------------------
        start_rect = QRect(
            self.logo.x() + 15,
            self.logo.y() + 15,
            self.logo.width() - 30,
            self.logo.height() - 30
        )

        self.scale_anim = QPropertyAnimation(self.logo, b"geometry")
        self.scale_anim.setDuration(900)
        self.scale_anim.setStartValue(start_rect)
        self.scale_anim.setEndValue(self.logo.geometry())
        self.scale_anim.setEasingCurve(QEasingCurve.Type.OutBack)

        # ------------------ Fade Out ------------------
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(700)
        self.fade_out.setStartValue(1)
        self.fade_out.setEndValue(0)
        self.fade_out.setEasingCurve(QEasingCurve.Type.InOutCubic)

        def _final_close():
            self.hide()
            self.deleteLater()
            self.finished.emit()

        self.fade_out.finished.connect(_final_close)

        # ------------------ Progress Timer ------------------
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_progress)

    # ==========================================================
    #  Start Splash
    # ==========================================================
    def start(self):
        self.fade_in.start()
        QTimer.singleShot(200, self.scale_anim.start)
        self.timer.start(35)

    # ==========================================================
    #  Progress Animation
    # ==========================================================
    def _update_progress(self):
        value = self.progress.value() + 1
        self.progress.setValue(value)

        if value == 30:
            self.label.setText("در حال بررسی مجوز...")
        elif value == 55:
            self.label.setText("در حال بارگذاری داده‌ها...")
        elif value == 80:
            self.label.setText("در حال راه‌اندازی سرویس‌ها...")

        if value >= 100:
            self.timer.stop()
            QTimer.singleShot(400, self.close_splash)

    # ==========================================================
    #  Close Splash
    # ==========================================================
    def close_splash(self):
        self.fade_out.start()

    # ==========================================================
    #  Center On Screen
    # ==========================================================
    def center_on_screen(self, app):
        screen = app.primaryScreen().availableGeometry()
        self.move(
            screen.center().x() - self.width() // 2,
            screen.center().y() - self.height() // 2
        )

    # ==========================================================
    #  Paint Rounded Background
    # ==========================================================
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(self.bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 22, 22)
