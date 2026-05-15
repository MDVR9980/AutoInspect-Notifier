import base64
import json
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QFormLayout,
    QMessageBox,
    QSpinBox
)
from PyQt6.QtCore import Qt

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


PRIVATE_KEY_PEM = b"""-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCx8ffnIQ0st5pi
no1tM1ajLz7dRHTkgP2Ig1Yye0HDkQzYcs7Z/t2LZPk7Co7GL4sqhMde4TlEGXQB
PNBVx3bFtZsIMJdfztkwY6eyBUrTQufKBY4W+5ganb+305oJOlAc1jpCMW5wFzYA
U7IwK0N+Rd7qxnXXDnJjZVxDVFUiIuBOfGI9EOwApA6yalI1ILwHggGz7D2ppzoH
kzHkliXJYXfHE0LsH9CMCfjnPIgP57IfEDaCCmaROwsPbT395zy/KHe3+T+8dSaJ
8VP6WG6DqnV+VUpLNnY5aH8D7Ll0XxQ1Cu1ZWTWSfAYHOQpSfEMVrf/qMv6fMOxI
fsrgPTrXAgMBAAECggEAEI/3S7J8vokQta9dqRvXRQhy0l2t5mgHirGN9m3lgM8b
G6xeV29mIU4F92DAsDttn+JmIia8nnuJNUvhQkXdM4LECf7OObMph1wtmB+I+uF/
0ukyDZT5iWsRLj19cvCg00ZKe62/jzxOoOvC91vKt1HIJIcE7qR5sVZ8wDsoH2Cb
+1pXR2PpMAA4AZzDSnFqk+rKbTIK5wc5GCPPyoYrdn8ZA6AydgH6xnGx67Y1NYaZ
fASgd9lAyuf3ZqWA7RZwg75DPkN6vZRSRKS65WriY2rT6foKhecyl6jWRSR6/rxj
QOKus1v4MmQ0ZuXxAhO7VOm2P6UfebHftyb+P2xKGQKBgQD7Qc5VrZfsyUJyFS24
TaSnnTIJ2Z50BM0fsXfuwuDl8JijIj0BnYW/klQG2FOmNLcg6ESm8/OTR7+Udv91
QZUYZesS1LpOvZ/I0PcQEskaa+BraWVbefNzOJD7/kkdNaNXPeyI6Aj02co3MEG6
dwGIsecxyDU1QwlkZfotAwgQ+QKBgQC1TeJrYrbc3XgQdgo9VMkcZ5Gps2FCyAUe
eMR89Bt5sU2A2YxTM7LdqQhrCwONTmdhjwpkOFKaSbb+kzhudXa1YcoliCY+PCIk
9mOpahw5DqB/jLyLDtCyD8TCYb+FiAXKe/qsjvtahVFAsKsk5fHMjkejz1lvaeNx
D8R4h11uTwKBgA8KQmKokIaRCZQwplr48tlBtKQYTb7eJrU191roeXPqMgjZ3NMC
7eWoybTbMC6ryyaCINHpmnP/gH1Pnj0Tnuwl9atb5oceHLl1oMRqi3U0beugFHwk
UaldAnjDIPdJpaxsPYN4eEjH3K3vCpAx3XqkQ5WcSWsVxzMmU5JsMwhpAoGBAI8E
+2Feo4WjJv1FQFqVMXg4sw09NbIqeu9IsScooSvkE5FbC3juxWBZ4QwfyhOED8VD
wxy/2VlgYPx9QfzQqG340C+/MPvTD9Q8kO2piM3xneZALNM9Qp/UFJCJ7zz0yiyq
lFnfCKSlmiz/sGIRCick7ZppDNH4o7QijgfOMIO9AoGALP5yE0tMwZtM9aTiMAIa
0MNpdV7rJVNZ594D8HSk4IXJ68Q0GUQWT+6Gm25eJvipnxFtz8epRgPqzsLyg0N0
0TrFIpdbX7smaD+RM6K/OsnUrGgRyK50fc6OphkYgI+/HOiIXtomIPGyKyQeU2bO
9HZdeOXwl294esmBpmStlNM=
-----END PRIVATE KEY-----"""


def load_private_key():
    return serialization.load_pem_private_key(PRIVATE_KEY_PEM, password=None)


def generate_license(customer, hwid, expires, max_users):
    private_key = load_private_key()

    payload = {
        "customer": customer,
        "hwid": hwid,
        "expires": expires,
        "max_users": max_users,
        "issued_at": datetime.now().strftime("%Y-%m-%d"),
        "last_valid_date": datetime.now().strftime("%Y-%m-%d")
    }

    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    signature = private_key.sign(
        raw,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    license_obj = {
        "data": base64.b64encode(raw).decode("utf-8"),
        "signature": base64.b64encode(signature).decode("utf-8")
    }

    final = base64.b64encode(
        json.dumps(license_obj, ensure_ascii=False).encode("utf-8")
    ).decode("utf-8")

    return final


class GeneratorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("تولید لایسنس")
        self.setMinimumSize(760, 520)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.customer = QLineEdit()
        self.hwid = QLineEdit()
        self.expires = QLineEdit()
        self.max_users = QSpinBox()
        self.max_users.setRange(1, 3)
        self.max_users.setValue(1)

        self.output = QTextEdit()
        self.output.setReadOnly(True)

        self.btn = QPushButton("تولید لایسنس")
        self.btn.clicked.connect(self.create)

        form = QFormLayout()
        form.addRow("نام مشتری", self.customer)
        form.addRow("شناسه دستگاه", self.hwid)
        form.addRow("تاریخ انقضا (YYYY-MM-DD)", self.expires)
        form.addRow("تعداد کاربران مجاز", self.max_users)

        layout = QVBoxLayout(self)
        title = QLabel("ابزار تولید لایسنس")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addLayout(form)
        layout.addWidget(self.btn)
        layout.addWidget(QLabel("خروجی لایسنس"))
        layout.addWidget(self.output)

    def create(self):
        customer = self.customer.text().strip()
        hwid = self.hwid.text().strip()
        expires = self.expires.text().strip()
        max_users = int(self.max_users.value())

        if not customer or not hwid or not expires:
            QMessageBox.warning(self, "خطا", "همه فیلدها باید تکمیل شوند.")
            return

        try:
            datetime.strptime(expires, "%Y-%m-%d")
        except ValueError:
            QMessageBox.warning(self, "خطا", "فرمت تاریخ معتبر نیست.")
            return

        license_key = generate_license(customer, hwid, expires, max_users)
        self.output.setPlainText(license_key)

import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GeneratorWindow()
    window.show()
    sys.exit(app.exec())