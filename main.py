"""
فایل اصلی برنامه
"""
import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

import settings
from db_manager import DatabaseManager
from main_window import MainWindow
from scheduler import TaskScheduler


def setup_logging():
    """راه‌اندازی سیستم لاگ"""
    settings.LOG_DIR.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(settings.LOG_FILE_PATH, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def main():
    """تابع اصلی برنامه"""
    # راه‌اندازی لاگ
    logger = setup_logging()
    logger.info("شروع برنامه")
    
    try:
        # ایجاد برنامه Qt
        app = QApplication(sys.argv)
        app.setApplicationName(settings.APP_NAME)
        app.setApplicationVersion(settings.APP_VERSION)
        
        # تنظیم آیکون برنامه
        if settings.APP_ICON_PATH.exists():
            app.setWindowIcon(QIcon(str(settings.APP_ICON_PATH)))
        
        # راه‌اندازی دیتابیس
        db = DatabaseManager()
        logger.info("دیتابیس راه‌اندازی شد")
        
        # راه‌اندازی زمان‌بند
        scheduler = TaskScheduler(db)
        scheduler.start()
        logger.info("زمان‌بند راه‌اندازی شد")
        
        # ایجاد و نمایش پنجره اصلی
        window = MainWindow(db, scheduler)
        window.setWindowTitle(settings.APP_TITLE)
        window.show()
        
        logger.info("پنجره اصلی نمایش داده شد")
        
        # اجرای برنامه
        exit_code = app.exec()
        
        # توقف زمان‌بند
        scheduler.stop()
        logger.info("برنامه بسته شد")
        
        return exit_code
        
    except Exception as e:
        logger.error(f"خطا در اجرای برنامه: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
