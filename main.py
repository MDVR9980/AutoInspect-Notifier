import os
import sys
import ctypes
import logging
import time
import settings

from ui.styles import Styles

# ---------------------------------------------------------
# Qt logging fixes
# ---------------------------------------------------------
os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false"

# ---------------------------------------------------------
# Windows DPI awareness
# ---------------------------------------------------------
if sys.platform == "win32":
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QFontDatabase, QFont
from PyQt6.QtCore import QTimer

from core.db_manager import DatabaseManager
from core.sms_api import SMSManager

from ui.main_window import MainWindow
from ui.splash_ultra import UltraSplash

from tasks.auto_task import AutoTaskManager

from license_manager import LicenseManager
from activation_window import show_activation_window


DEV_MODE = False
DEVELOPER_HWID = "e0ae2d59f6c1d75381c78cb6f7f1ebdf67eba39960e494977149284a64f05314"


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
# Splash Factory
# ---------------------------------------------------------
def create_splash(app):
    splash = UltraSplash(settings.PRIMARY_LOGO_SVG)

    try:
        screen = app.primaryScreen().availableGeometry()

        splash.move(
            screen.center().x() - splash.width() // 2,
            screen.center().y() - splash.height() // 2
        )

        splash.show()
        splash.start()

        app.processEvents()

    except Exception:
        pass

    return splash


def handle_exception(exc_type, exc_value, exc_traceback):
    logging.error(
        "Uncaught exception",
        exc_info=(exc_type, exc_value, exc_traceback)
    )


sys.excepthook = handle_exception


# ---------------------------------------------------------
# Load Fonts
# ---------------------------------------------------------
def load_fonts():
    font_paths = [
        "fonts/Vazirmatn-Regular.ttf",
        "fonts/Vazirmatn-Medium.ttf",
        "fonts/Vazirmatn-Bold.ttf"
    ]

    for path in font_paths:
        if os.path.exists(path):
            QFontDatabase.addApplicationFont(path)


# ---------------------------------------------------------
# Apply Global Styles
# ---------------------------------------------------------
def apply_styles(app):

    ui = Styles("light")

    stylesheet = (
        ui.get_app_style() +
        ui.get_card_style() +
        ui.get_button_style() +
        ui.get_input_style() +
        ui.get_table_style() +
        ui.get_tab_style() +
        ui.get_scrollbar_style() +
        ui.get_menu_style() +
        ui.get_checkbox_style() +
        ui.get_tooltip_style() +
        ui.get_progress_style() +
        ui.get_dialog_style()
    )

    app.setStyleSheet(stylesheet)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main():

    logger = setup_logging()
    logger.info("شروع برنامه")

    auto_task_manager = None

    try:

        # -------------------------------------------------
        # Fix Windows Taskbar Icon
        # -------------------------------------------------
        if sys.platform == "win32":
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                    u"AutoInspect.Notifier.App"
                )
            except Exception:
                pass

        # -------------------------------------------------
        # QApplication
        # -------------------------------------------------
        app = QApplication(sys.argv)

        app.setApplicationName(settings.APP_NAME)
        app.setApplicationVersion(settings.APP_VERSION)

        # -------------------------------------------------
        # Fonts
        # -------------------------------------------------
        load_fonts()
        app.setFont(QFont("Vazirmatn", 10))

        # -------------------------------------------------
        # Global Styles
        # -------------------------------------------------
        apply_styles(app)

        # -------------------------------------------------
        # App Icon
        # -------------------------------------------------
        if settings.APP_ICON_ICO.exists():
            app.setWindowIcon(QIcon(str(settings.APP_ICON_ICO)))

        splash_start = time.time()

        # -------------------------------------------------
        # Splash
        # -------------------------------------------------
        splash = create_splash(app)

        # -------------------------------------------------
        # License Check
        # -------------------------------------------------
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

        # -------------------------------------------------
        # Database
        # -------------------------------------------------
        db = DatabaseManager(settings.DATABASE_PATH)

        # -------------------------------------------------
        # SMS
        # -------------------------------------------------
        sms_manager = SMSManager(
            settings.SMS_API_KEY,
            settings.SMS_LINE_NUMBER
        )

        # -------------------------------------------------
        # Tasks
        # -------------------------------------------------
        auto_task_manager = AutoTaskManager(db, sms_manager)
        auto_task_manager.start()

        # -------------------------------------------------
        # Main Window
        # -------------------------------------------------
        window = MainWindow(db, auto_task_manager)
        window.setWindowTitle(settings.APP_NAME)

        # -------------------------------------------------
        # Minimum splash duration
        # -------------------------------------------------
        min_duration = 1.8
        elapsed = time.time() - splash_start
        delay_ms = max(0, int((min_duration - elapsed) * 1000))

        def open_main():
            if not window.isVisible():
                window.show()

        QTimer.singleShot(delay_ms, lambda: splash.close_splash())
        splash.finished.connect(open_main)

        # -------------------------------------------------
        # Execute
        # -------------------------------------------------
        exit_code = app.exec()

        return exit_code

    except Exception as e:

        logger.error(f"Fatal Error: {e}", exc_info=True)
        return 1

    finally:

        if auto_task_manager:
            try:
                auto_task_manager.stop()
                logger.info("AutoTaskManager stopped")
            except Exception as e:
                logger.warning(f"AutoTaskManager stop ignored: {e}")


if __name__ == "__main__":
    sys.exit(main())
