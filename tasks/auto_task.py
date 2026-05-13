# tasks/auto_task.py

import logging
from persiantools.jdatetime import JalaliDate
import jdatetime

# 1. استفاده از import های مطلق برای رفع خطای ImportError
from core.db_manager import DatabaseManager
from core.sms_api import SmsApiClient, sms_client # sms_client سراسری را هم وارد می‌کنیم
import settings

# لاگ‌گیری برای این ماژول
log = logging.getLogger(__name__)


class TaskManager:
    """
    وظیفه خودکار بررسی تاریخ انقضای معاینه فنی و ارسال پیامک
    در همان روز انقضا را مدیریت می‌کند.
    """

    def __init__(self, db_manager: DatabaseManager, sms_api_client: SmsApiClient):
        """
        سازنده کلاس TaskManager.

        Args:
            db_manager (DatabaseManager): یک نمونه برای کار با دیتابیس.
            sms_api_client (SmsApiClient): یک نمونه برای ارسال پیامک.
        """
        self.db_manager = db_manager
        self.sms_client = sms_api_client

    def process_daily_notifications(self) -> None:
        """
        مشتریانی که تاریخ انقضای معاینه فنی آن‌ها امروز است را پیدا کرده
        و برای آن‌ها پیامک ارسال می‌کند.
        """
        log.info("شروع وظیفه روزانه ارسال پیامک...")
        
        # 2. استفاده از تاریخ شمسی (Jalali) به جای میلادی
        today_jalali_str = JalaliDate(jdatetime.date.today()).strftime('%Y-%m-%d')
        
        # مشتریانی که تاریخ انقضای آن‌ها امروز است را مستقیماً از دیتابیس می‌خوانیم
        customers_to_notify = self.db_manager.get_customers_for_sms(today_jalali_str)
        
        if not customers_to_notify:
            log.info(f"برای تاریخ {today_jalali_str} هیچ مشتری نیاز به اطلاع‌رسانی ندارد. پایان کار.")
            return

        log.info(f"امروز {len(customers_to_notify)} مشتری برای اطلاع‌رسانی پیدا شد.")

        for customer in customers_to_notify:
            customer_id, name, phone, car_model, car_id, _, expiry_date, _ = customer
            
            # ساخت پیام
            message = self._create_reminder_message(name, car_model, car_id, expiry_date)
            
            # ارسال پیامک
            is_sent = self.sms_client.send_sms(phone, message)
            
            # به‌روزرسانی وضعیت در دیتابیس
            if is_sent:
                self.db_manager.update_sms_status(customer_id, 'sent')
                log.info(f"پیامک برای {name} ({phone}) با موفقیت ارسال و وضعیت به‌روز شد.")
            else:
                self.db_manager.update_sms_status(customer_id, 'failed')
                log.warning(f"ارسال پیامک برای {name} ({phone}) ناموفق بود. وضعیت 'failed' ثبت شد.")

    def _create_reminder_message(self, name: str, car_model: str, car_id: str, expiry_date: str) -> str:
        """یک پیام یادآوری استاندارد ایجاد می‌کند."""
        message = (
            f"سلام {name} عزیز،\n"
            f"تاریخ معاینه فنی خودروی شما ({car_model} به شماره پلاک {car_id}) "
            f"امروز ({expiry_date}) به پایان می‌رسد.\n"
            f"لطفا جهت تمدید آن اقدام فرمایید."
        )
        return message

# --- نقطه ورود برای Scheduler ---

def run_notification_task():
    """
    این تابع توسط زمان‌بند (scheduler) فراخوانی می‌شود.
    این تابع مسئولیت ایجاد و پاک‌سازی منابع (مانند اتصال دیتابیس) را برای
    هر بار اجرای وظیفه بر عهده دارد تا از مشکلات مربوط به thread جلوگیری شود.
    """
    log.info("زمان‌بند فعال شد: در حال اجرای وظیفه اطلاع‌رسانی.")
    db_manager_instance = None
    try:
        # برای هر بار اجرا، یک نمونه جدید از DatabaseManager می‌سازیم.
        # این کار برای اجرای امن در ترد (thread) ضروری است.
        db_manager_instance = DatabaseManager(db_path=settings.DB_FILE_PATH)
        
        # از نمونه سراسری sms_client که قبلاً ساخته شده استفاده می‌کنیم
        task_manager = TaskManager(db_manager=db_manager_instance, sms_api_client=sms_client)
        
        # اجرای منطق اصلی
        task_manager.process_daily_notifications()

    except Exception as e:
        log.error(f"خطای پیش‌بینی نشده در اجرای وظیفه اطلاع‌رسانی: {e}", exc_info=True)
    finally:
        # تضمین می‌کنیم که اتصال دیتابیس در هر صورت بسته شود.
        if db_manager_instance:
            db_manager_instance.close()
        log.info("اجرای وظیفه اطلاع‌رسانی تمام شد. منابع پاک‌سازی شدند.")
