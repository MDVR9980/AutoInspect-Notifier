"""
تنظیمات اصلی برنامه AutoInspect Notifier
"""
import os
from pathlib import Path

# مسیرهای پروژه
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = DATA_DIR / "backups"
ASSETS_DIR = DATA_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
EXPORTS_DIR = BASE_DIR / "exports"
LOGS_DIR = BASE_DIR / "logs"

# ایجاد پوشه‌ها در صورت عدم وجود
for directory in [DATA_DIR, BACKUP_DIR, ASSETS_DIR, ICONS_DIR, EXPORTS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# دیتابیس
DATABASE_PATH = DATA_DIR / "database.db"

# تنظیمات SMS (قاصدک)
SMS_API_URL = "https://api.ghasedak.me/v2/sms/send/simple"
SMS_API_KEY = "YOUR_GHASEDAK_API_KEY_HERE"  # کلید API قاصدک را اینجا قرار دهید
SMS_LINE_NUMBER = "YOUR_LINE_NUMBER"  # شماره خط قاصدک

# متن پیامک (قابل تغییر)
SMS_TEMPLATE = """
مشتری گرامی
پلاک: {plate}
تاریخ انقضای معاینه فنی: {expire_date}
لطفاً جهت تمدید به مرکز معاینه فنی مراجعه فرمایید.
"""

# تنظیمات زمان‌بندی
REMINDER_DAYS_BEFORE = 3  # چند روز قبل از انقضا پیامک ارسال شود
SCHEDULER_CHECK_TIME = "08:00"  # ساعت چک روزانه (فرمت HH:MM)

# تنظیمات لاگ
LOG_FILE = LOGS_DIR / "app.log"
LOG_LEVEL = "INFO"

# تنظیمات تم
DEFAULT_THEME = "light"  # light یا dark

# تنظیمات فایل اکسل
EXCEL_COLUMNS = {
    "phone": 0,  # ستون شماره تلفن
    "plate": 1   # ستون پلاک
}

# آیکون برنامه
APP_ICON = ICONS_DIR / "app_icon.ico"
