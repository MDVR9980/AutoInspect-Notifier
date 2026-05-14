"""
مدیریت زمان‌بندی ارسال پیامک‌ها
"""
import logging
from datetime import timedelta

import jdatetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from core.db_manager import DatabaseManager
from core.sms_api import SMSManager
from settings import REMINDER_DAYS_BEFORE, SCHEDULER_CHECK_TIME

logger = logging.getLogger(__name__)


class TaskScheduler:
    """مدیریت زمان‌بندی ارسال خودکار پیامک‌ها"""

    def __init__(self, db_manager: DatabaseManager, sms_manager: SMSManager):
        self.db_manager = db_manager
        self.sms_manager = sms_manager

        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

        logger.info("زمان‌بند راه‌اندازی شد")

    def start_daily_task(self):
        """راه‌اندازی وظیفه روزانه"""

        try:
            # حذف تسک قبلی در صورت وجود
            if self.scheduler.get_job('daily_sms_task'):
                self.scheduler.remove_job('daily_sms_task')

            hour, minute = map(int, SCHEDULER_CHECK_TIME.split(':'))
            trigger = CronTrigger(
                hour=hour,
                minute=minute
            )

            self.scheduler.add_job(
                func=self.check_and_send_reminders,
                trigger=trigger,
                id='daily_sms_task',
                name='ارسال روزانه پیامک یادآوری',
                replace_existing=True
            )

            logger.info(
                f"وظیفه روزانه برای ساعت "
                f"{hour}:{minute:02d} تنظیم شد"
            )

            return True

        except Exception as e:
            logger.error(f"خطا در تنظیم وظیفه روزانه: {str(e)}")
            return False

    def check_and_send_reminders(self):
        """بررسی و ارسال پیامک‌های یادآوری"""

        logger.info("شروع بررسی پیامک‌های یادآوری")

        try:
            today = jdatetime.date.today()

            # تاریخ انقضایی که باید امروز برایش پیامک ارسال شود
            target_expire_date = today + timedelta(days=REMINDER_DAYS_BEFORE)

            target_expire_date_str = target_expire_date.strftime('%Y/%m/%d')

            logger.info(
                f"بررسی پیامک‌ها برای تاریخ انقضا: "
                f"{target_expire_date_str}"
            )

            subscribers = self.db_manager.get_subscribers_for_reminder(
                target_expire_date_str
            )

            if not subscribers:
                logger.info("هیچ مشترکی برای ارسال پیامک یافت نشد")
                return {
                    'success': 0,
                    'failed': 0,
                    'total': 0
                }

            success_count = 0
            failed_count = 0

            for subscriber in subscribers:
                try:
                    subscriber_id = subscriber[0]
                    phone = subscriber[1]
                    plate = subscriber[2]
                    expire_date = subscriber[3]

                    logger.info(f"ارسال پیامک به {phone}")

                    send_result = self.sms_manager.send_reminder(
                        phone_number=phone,
                        plate_number=plate,
                        expire_date=expire_date
                    )

                    if send_result:
                        self.db_manager.update_sms_status(
                            subscriber_id,
                            'ارسال شد'
                        )

                        success_count += 1

                        logger.info(
                            f"پیامک با موفقیت به {phone} ارسال شد"
                        )

                    else:
                        failed_count += 1

                        logger.error(
                            f"ارسال پیامک به {phone} ناموفق بود"
                        )

                except Exception as e:
                    failed_count += 1

                    logger.error(
                        f"خطا در ارسال پیامک به مشترک: {str(e)}"
                    )

            logger.info(
                f"پایان ارسال پیامک‌ها | "
                f"موفق: {success_count} | "
                f"ناموفق: {failed_count}"
            )

            return {
                'success': success_count,
                'failed': failed_count,
                'total': len(subscribers)
            }

        except Exception as e:
            logger.error(f"خطا در بررسی پیامک‌ها: {str(e)}")

            return {
                'success': 0,
                'failed': 0,
                'total': 0
            }

    def check_missed_tasks(self):
        """
        بررسی پیامک‌های از دست رفته
        زمانی که برنامه یا سیستم خاموش بوده
        """

        logger.info("بررسی وظایف از دست رفته")

        try:
            today = jdatetime.date.today()

            total_sent = 0

            # بررسی چند روز اخیر
            for days_back in range(REMINDER_DAYS_BEFORE + 1):

                check_day = today - timedelta(days=days_back)

                target_expire_date = (
                    check_day + timedelta(days=REMINDER_DAYS_BEFORE)
                )

                target_expire_date_str = target_expire_date.strftime(
                    '%Y/%m/%d'
                )

                subscribers = self.db_manager.get_subscribers_for_reminder(
                    target_expire_date_str
                )

                if not subscribers:
                    continue

                logger.info(
                    f"{len(subscribers)} پیامک عقب‌افتاده یافت شد"
                )

                for subscriber in subscribers:
                    try:
                        subscriber_id = subscriber[0]
                        phone = subscriber[1]
                        plate = subscriber[2]
                        expire_date = subscriber[3]

                        send_result = self.sms_manager.send_reminder(
                            phone_number=phone,
                            plate_number=plate,
                            expire_date=expire_date
                        )

                        if send_result:
                            self.db_manager.update_sms_status(
                                subscriber_id,
                                'ارسال شد'
                            )

                            total_sent += 1

                            logger.info(
                                f"پیامک عقب‌افتاده به {phone} ارسال شد"
                            )

                    except Exception as e:
                        logger.error(
                            f"خطا در ارسال پیامک عقب‌افتاده: {str(e)}"
                        )

            logger.info(
                f"بررسی وظایف عقب‌افتاده پایان یافت | "
                f"تعداد ارسال: {total_sent}"
            )

            return total_sent

        except Exception as e:
            logger.error(f"خطا در بررسی وظایف عقب‌افتاده: {str(e)}")
            return 0

    def get_jobs(self):
        """دریافت لیست وظایف"""

        try:
            return self.scheduler.get_jobs()

        except Exception as e:
            logger.error(f"خطا در دریافت وظایف: {str(e)}")
            return []

    def shutdown(self):
        """توقف زمان‌بند"""

        try:
            self.scheduler.shutdown(wait=False)

            logger.info("زمان‌بند متوقف شد")

            return True

        except Exception as e:
            logger.error(f"خطا در توقف زمان‌بند: {str(e)}")
            return False
