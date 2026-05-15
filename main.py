import ctypes, sys, logging, time
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QIcon, QPixmap, QFont, QColor, QPainter
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve

import settings
from core.db_manager import DatabaseManager
from ui.main_window import MainWindow
from tasks.auto_task import AutoTaskManager
from core.sms_api import SMSManager
from license_manager import LicenseManager
from activation_window import show_activation_window


DEV_MODE = False
DEVELOPER_HWID = "e0ae2d59f6c1d75381c78cb6f7f1ebdf67eba39960e494977149284a64f05314"


# ---------------------------------------------------------
# Custom Splash Screen
# ---------------------------------------------------------
class CustomSplash(QWidget):
    def __init__(self, logo_path):
        super().__init__()

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(500, 500)

        # Opacity
        self.setWindowOpacity(0.0)

        # Load Logo
        pix = QPixmap(str(logo_path))
        if pix.isNull():
            print("Splash ERROR: Logo not found ->", logo_path)
            self.logo = None
        else:
            self.logo = pix.scaled(
                260, 260,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

        # Fade In
        self.fade_in_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_anim.setDuration(700)
        self.fade_in_anim.setStartValue(0.0)
        self.fade_in_anim.setEndValue(1.0)
        self.fade_in_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Fade Out
        self.fade_out_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out_anim.setDuration(450)
        self.fade_out_anim.setStartValue(1.0)
        self.fade_out_anim.setEndValue(0.0)
        self.fade_out_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Animated dots
        self.message = ""
        self.dots = 0
        self.dot_timer = QTimer(self)
        self.dot_timer.timeout.connect(self.update_dots)
        self.dot_timer.start(350)

    def update_dots(self):
        self.dots = (self.dots + 1) % 4
        self.update()

    def show_message(self, text):
        self.message = text
        self.update()

    # Fade control
    def fade_in(self):
        self.fade_in_anim.start()

    def fade_out_and_close(self, callback):
        def done():
            self.close()
            if callback:
                callback()
        self.fade_out_anim.finished.connect(done)
        self.fade_out_anim.start()

    # Paint Event
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        bg = QColor(255, 255, 255, 245)
        painter.setBrush(bg)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 22, 22)

        # Logo
        if self.logo:
            x = (self.width() - self.logo.width()) // 2
            y = (self.height() - self.logo.height()) // 2 - 35
            painter.drawPixmap(x, y, self.logo)

        # Message
        painter.setFont(QFont("Segoe UI", 11))
        painter.setPen(QColor(20, 20, 20))

        msg = f"{self.message}{'.' * self.dots}"
        painter.drawText(
            0, self.height() - 60,
            self.width(), 40,
            Qt.AlignmentFlag.AlignCenter,
            msg
        )


# ---------------------------------------------------------
# Splash Factory
# ---------------------------------------------------------
def create_splash(app):
    logo = settings.PRIMARY_LOGO
    splash = CustomSplash(logo)

    # Center
    screen = app.primaryScreen().availableGeometry()
    splash.move(
        screen.center().x() - splash.width() // 2,
        screen.center().y() - splash.height() // 2
    )

    splash.show()
    splash.fade_in()
    app.processEvents()

    return splash


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------
def setup_logging():
    settings.LOGS_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(settings.LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger(__name__)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main():
    logger = setup_logging()
    logger.info("شروع برنامه")

    try:
        # Fix Taskbar Icon
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                u"AutoInspect.Notifier.App"
            )
        except Exception:
            pass

        app = QApplication(sys.argv)
        app.setApplicationName(settings.APP_NAME)
        app.setApplicationVersion(settings.APP_VERSION)

        if settings.APP_ICON.exists():
            app.setWindowIcon(QIcon(str(settings.APP_ICON)))

        splash_start = time.time()

        # Splash
        splash = create_splash(app)
        splash.show_message("Loading modules")

        # License
        splash.show_message("Checking license")
        lm = LicenseManager()

        if DEV_MODE and lm.get_hwid() == DEVELOPER_HWID:
            ok = True
        else:
            ok, _ = lm.check_valid()

        if not ok:
            splash.close()
            show_activation_window()
            ok, _ = lm.check_valid()
            if not ok:
                logger.error("Activation failed.")
                return 1

        # Database
        splash.show_message("Loading database")
        db = DatabaseManager(settings.DATABASE_PATH)

        # SMS
        sms_manager = SMSManager(settings.SMS_API_KEY, settings.SMS_LINE_NUMBER)

        # Tasks
        auto_task_manager = AutoTaskManager(db, sms_manager)
        auto_task_manager.start()

        # Prepare Main Window
        window = MainWindow(db, auto_task_manager)
        window.setWindowTitle(settings.APP_NAME)

        min_duration = 1.8  
        elapsed = time.time() - splash_start
        delay_ms = max(0, int((min_duration - elapsed) * 1000))

        # Show Main After Splash Fade
        def open_main():
            window.show()

        QTimer.singleShot(delay_ms, lambda: splash.fade_out_and_close(open_main))

        # Execute
        exit_code = app.exec()
        auto_task_manager.stop()
        return exit_code

    except Exception as e:
        logger.error(f"Fatal Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
