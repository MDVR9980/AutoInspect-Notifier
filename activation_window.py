from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QFrame,
    QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QGuiApplication

from license_manager import LicenseManager

class ActivationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.license_manager = LicenseManager()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("فعال‌سازی نرم‌افزار")
        self.setMinimumSize(720, 420)

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        main_layout = QVBoxLayout(self)

        title = QLabel("فعال‌سازی نرم‌افزار")
        title.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        desc = QLabel("برای فعال‌سازی، کد لایسنس صادرشده را وارد کنید.")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)

        code_frame = QFrame()
        code_frame.setFrameShape(QFrame.Shape.StyledPanel)

        code_layout = QVBoxLayout(code_frame)

        code_title = QLabel("شناسه دستگاه")
        code_title.setFont(QFont("Tahoma", 11, QFont.Weight.Bold))

        self.code_box = QLineEdit()
        self.code_box.setReadOnly(True)
        self.code_box.setText(self.license_manager.get_hwid())

        copy_btn = QPushButton("کپی")
        copy_btn.clicked.connect(self.copy_code)

        row = QHBoxLayout()
        row.addWidget(self.code_box)
        row.addWidget(copy_btn)

        code_layout.addWidget(code_title)
        code_layout.addLayout(row)

        key_title = QLabel("کد لایسنس")
        key_title.setFont(QFont("Tahoma", 11, QFont.Weight.Bold))

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("کد لایسنس را اینجا وارد کنید")

        self.activate_btn = QPushButton("فعال‌سازی")
        self.activate_btn.clicked.connect(self.activate)

        main_layout.addWidget(title)
        main_layout.addWidget(desc)
        main_layout.addWidget(code_frame)
        main_layout.addWidget(key_title)
        main_layout.addWidget(self.key_input)
        main_layout.addWidget(self.activate_btn)

    def copy_code(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.code_box.text())
        QMessageBox.information(self, "موفق", "شناسه دستگاه در کلیپ‌بورد کپی شد.")

    def activate(self):
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "خطا", "کد لایسنس را وارد کنید.")
            return

        ok, message = self.license_manager.activate(key)
        if ok:
            QMessageBox.information(self, "موفق", message)
            self.close()
        else:
            QMessageBox.critical(self, "خطا", message)


def show_activation_window():
    """نمایش پنجره فعال‌سازی برای main.py"""
    app = QApplication.instance()
    created_app = False

    if app is None:
        app = QApplication([])
        created_app = True

    window = ActivationWindow()
    window.setWindowModality(Qt.WindowModality.ApplicationModal)
    window.show()

    app.exec()

    if created_app:
        app.quit()
