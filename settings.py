"""
تنظیمات اصلی برنامه AutoInspect Notifier
"""

import json
from pathlib import Path

# =========================
# مسیرهای پروژه
# =========================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = DATA_DIR / "backups"

ASSETS_DIR = DATA_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
LOGOS_DIR = ASSETS_DIR / "logos"

LOGS_DIR = BASE_DIR / "logs"

# ایجاد پوشه‌ها در صورت عدم وجود
REQUIRED_DIRS = [
    DATA_DIR,
    BACKUP_DIR,
    ASSETS_DIR,
    ICONS_DIR,
    LOGOS_DIR,
    LOGS_DIR,
]

for directory in REQUIRED_DIRS:
    directory.mkdir(parents=True, exist_ok=True)


# =========================
# اطلاعات برنامه
# =========================

APP_NAME = "AutoInspect Notifier"
APP_VERSION = "1.0.0"


# =========================
# دیتابیس
# =========================

DATABASE_PATH = DATA_DIR / "database.db"


# =========================
# تنظیمات SMS (قاصدک)
# =========================

SMS_API_URL = "https://api.ghasedak.me/v2/sms/send/simple"

SMS_API_KEY = "YOUR_API_KEY"

SMS_LINE_NUMBER = "30005088"


# متن پیامک
SMS_TEMPLATE = """
مشتری گرامی
پلاک: {plate}
تاریخ انقضای معاینه فنی: {expire_date}
لطفاً جهت تمدید به مرکز معاینه فنی مراجعه فرمایید.
"""


# =========================
# تنظیمات زمان‌بندی
# =========================

REMINDER_DAYS_BEFORE = 3
SCHEDULER_CHECK_TIME = "08:00"


# =========================
# تنظیمات لاگ
# =========================

LOG_FILE = LOGS_DIR / "app.log"
LOG_LEVEL = "INFO"


# =========================
# تنظیمات ظاهری
# =========================

DEFAULT_THEME = "light"


# =========================
# تنظیمات اکسل
# =========================

EXCEL_COLUMNS = {
    "phone": 0,
    "plate": 1
}


# =========================
# آیکون‌ها و لوگو
# =========================

APP_ICON_ICO = ICONS_DIR / "app_icon.ico"

PRIMARY_LOGO_SVG = LOGOS_DIR / "PrimaryLogo.svg"
PRIMARY_LOGO_PNG = LOGOS_DIR / "PrimaryLogo.png"

MONO_LOGO = LOGOS_DIR / "MonochromeVersion.png"
APP_ICON_PNG = LOGOS_DIR / "AppIconVersion.png"


# =========================
# مدیریت تنظیمات برنامه
# =========================

SETTINGS_FILE = DATA_DIR / "app_settings.json"


class SettingsManager:
    """
    مدیریت تنظیمات قابل تغییر برنامه
    """

    def __init__(self):
        self.settings = {}
        self.load_settings()

    def load_settings(self):
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    self.settings = json.load(f)
            except Exception:
                self.settings = {"theme": DEFAULT_THEME}
                self.save_settings()
        else:
            self.settings = {"theme": DEFAULT_THEME}
            self.save_settings()

    def save_settings(self):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=4, ensure_ascii=False)

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()
