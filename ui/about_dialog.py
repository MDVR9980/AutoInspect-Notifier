from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QWidget, QApplication, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QPixmap, QFont, QIcon, QPainter
from PyQt6.QtCore import Qt, QT_VERSION_STR
import platform
import os
import settings

class AboutDialog(QDialog):
    def __init__(self, license_info, current_theme="light", parent=None):
        super().__init__(parent)

        self.license_info = license_info
        self.current_theme = current_theme.lower()
        self.is_dark = (self.current_theme == "dark")

        self.setWindowTitle("درباره نرم‌افزار")
        self.setWindowIcon(QIcon(str(settings.APP_ICON_ICO)))
        self.resize(460, 600)

        self.setStyleSheet(
            "background-color: #000000;" if self.is_dark
            else "background-color: #f4f4f4;"
        )

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # -----------------------------
        # Container
        # -----------------------------
        container = QWidget()
        container.setObjectName("container")
        container.setStyleSheet(self.get_stylesheet())

        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(12)

        main_layout.addWidget(container)

        # -----------------------------
        # Header Card
        # -----------------------------
        header_card = QWidget()
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(20, 20, 20, 20)
        header_layout.setSpacing(10)

        if self.is_dark:
            header_style = """
                background: #1c1c1c;
                border-radius: 14px;
                border: 1px solid #2a2a2a;
            """
        else:
            header_style = """
                background: #ffffff;
                border-radius: 14px;
                border: 1px solid #e6e6e6;
            """

        header_card.setStyleSheet(header_style)

        # -----------------------------
        # Logo Section
        # -----------------------------
        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_container = QWidget()
        logo_container.setFixedSize(150, 150)

        logo_container.setStyleSheet(
            """
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #1e1e1e, stop:1 #111
            );
            border-radius: 20px;
            """
            if self.is_dark else
            """
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f2f2f2
            );
            border-radius: 20px;
            """
        )

        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)

        logo_path = (
            settings.MONO_LOGO if self.is_dark
            else settings.PRIMARY_LOGO_PNG
        )

        if os.path.exists(logo_path):

            pixmap = QPixmap(str(logo_path)).scaled(
                120,
                120,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            size = min(pixmap.width(), pixmap.height())

            mask = QPixmap(size, size)
            mask.fill(Qt.GlobalColor.transparent)

            painter = QPainter(mask)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(Qt.GlobalColor.white)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(0, 0, size, size)
            painter.end()

            pixmap.setMask(mask.createMaskFromColor(Qt.GlobalColor.transparent))
            logo.setPixmap(pixmap)

            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(40)
            shadow.setOffset(0, 10)
            shadow.setColor(
                Qt.GlobalColor.white if self.is_dark
                else Qt.GlobalColor.black
            )
            logo.setGraphicsEffect(shadow)

        logo_layout.addWidget(
            logo,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        header_layout.addWidget(
            logo_container,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        # -----------------------------
        # Divider
        # -----------------------------
        divider = QWidget()
        divider.setFixedHeight(2)
        divider.setStyleSheet(
            "background-color: #333;"
            if self.is_dark else
            "background-color: #e2e2e2;"
        )

        header_layout.addWidget(divider)

        # -----------------------------
        # Titles
        # -----------------------------
        title = QLabel("نرم‌افزار یادآور بازرسی خودرو")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Vazirmatn", 15, QFont.Weight.Bold))
        header_layout.addWidget(title)

        version = QLabel("نسخه ۱.۰ • نسخه حرفه‌ای")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setFont(QFont("Vazirmatn", 10))
        header_layout.addWidget(version)

        company = QLabel("AutoInspect Technologies")
        company.setAlignment(Qt.AlignmentFlag.AlignCenter)
        company.setFont(QFont("Vazirmatn", 9))
        header_layout.addWidget(company)

        layout.addWidget(header_card)
        layout.addSpacing(5)

        # -----------------------------
        # License Card
        # -----------------------------
        license_card = self.create_card([
            f"وضعیت لایسنس: {self.license_info['status']}",
            f"تاریخ انقضا: {self.license_info['expiry']}",
            f"نام مشتری: {self.license_info['customer']}"
        ])

        layout.addWidget(license_card)

        # -----------------------------
        # System Info Card
        # -----------------------------
        sys_card = self.create_card([
            f"نسخه پایتون: {platform.python_version()}",
            f"نسخه Qt: {QT_VERSION_STR}",
            f"سیستم‌عامل: {platform.system()} {platform.release()}",
        ], title="اطلاعات سیستم")

        layout.addWidget(sys_card)

        layout.addSpacing(10)

        # -----------------------------
        # Buttons
        # -----------------------------
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        copy_btn = QPushButton("کپی اطلاعات لایسنس")
        support_btn = QPushButton("پشتیبانی")

        for btn in (copy_btn, support_btn):
            btn.setFixedHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        copy_btn.clicked.connect(self.copy_license_info)
        support_btn.clicked.connect(self.contact_support)

        btn_layout.addWidget(copy_btn)
        btn_layout.addWidget(support_btn)

        layout.addLayout(btn_layout)

    # --------------------------------
    # Card Generator
    # --------------------------------
    def create_card(self, items, title=None):
        card = QWidget()
        card_layout = QVBoxLayout(card)

        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(6)

        if self.is_dark:
            style = """
                background: #1c1c1c;
                border-radius: 12px;
                border: 1px solid #2a2a2a;
            """
        else:
            style = """
                background: #ffffff;
                border-radius: 12px;
                border: 1px solid #e6e6e6;
            """

        card.setStyleSheet(style)

        if title:
            title_lbl = QLabel(title)
            title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_lbl.setFont(QFont("Vazirmatn", 11, QFont.Weight.Bold))
            card_layout.addWidget(title_lbl)

        for text in items:
            lbl = QLabel(text)
            lbl.setFont(QFont("Vazirmatn", 10))
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(lbl)

        return card

    # --------------------------------
    # Stylesheet
    # --------------------------------
    def get_stylesheet(self):

        if self.is_dark:
            return """
            #container {
                background: #121212;
                border-radius: 22px;
            }

            QLabel {
                color: #e6e6e6;
                font-family: Vazirmatn;
            }

            QPushButton {
                background: #0a84ff;
                padding: 9px 20px;
                color: white;
                border-radius: 8px;
                font-family: Vazirmatn;
            }

            QPushButton:hover {
                background: #409cff;
            }
            """

        else:
            return """
            #container {
                background: #ffffff;
                border-radius: 22px;
                border: 1px solid #e5e5e5;
            }

            QLabel {
                color: #333;
                font-family: Vazirmatn;
            }

            QPushButton {
                background: #0078D4;
                padding: 9px 20px;
                color: white;
                border-radius: 8px;
                font-family: Vazirmatn;
            }

            QPushButton:hover {
                background: #005a9e;
            }
            """

    # --------------------------------
    # Actions
    # --------------------------------
    def copy_license_info(self):

        text = (
            f"AutoInspect Notifier (نسخه حرفه‌ای)\n"
            f"وضعیت لایسنس: {self.license_info['status']}\n"
            f"تاریخ انقضا: {self.license_info['expiry']}\n"
            f"نام مشتری: {self.license_info['customer']}\n"
        )

        QApplication.clipboard().setText(text)

    def contact_support(self):

        import webbrowser
        webbrowser.open("https://autoinspect-tech.com/support")
