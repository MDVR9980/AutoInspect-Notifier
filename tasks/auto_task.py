# tasks/auto_task.py
"""
Auto Task Manager - مدیریت خودکار وظایف زمان‌بندی شده
"""
from tasks.scheduler import TaskScheduler


class AutoTaskManager:
    """مدیریت خودکار وظایف یادآوری و زمان‌بندی"""
    
    def __init__(self, db_manager, sms_manager):
        """
        Args:
            db_manager: نمونه DatabaseManager برای دسترسی به دیتابیس
            sms_manager: نمونه SMSManager برای ارسال پیامک
        """
        self.db_manager = db_manager
        self.sms_manager = sms_manager
        self.scheduler = TaskScheduler(db_manager, sms_manager)
        
    def start(self):
        """شروع زمان‌بندی خودکار وظایف"""
        try:
            self.scheduler.start()
            self.scheduler.start_daily_task()
            print("✓ Auto Task Manager started successfully")
            return True
        except Exception as e:
            print(f"✗ Error starting Auto Task Manager: {e}")
            return False
    
    def stop(self):
        """توقف زمان‌بندی خودکار وظایف"""
        try:
            self.scheduler.shutdown()
            print("✓ Auto Task Manager stopped successfully")
            return True
        except Exception as e:
            print(f"✗ Error stopping Auto Task Manager: {e}")
            return False
    
    def get_scheduled_jobs(self):
        """دریافت لیست jobهای زمان‌بندی شده"""
        return self.scheduler.get_jobs()
    
    def check_reminders_now(self):
        """اجرای دستی بررسی و ارسال یادآوری‌ها"""
        return self.scheduler.check_and_send_reminders()
    
    def check_missed_now(self):
        """اجرای دستی بررسی وظایف عقب‌افتاده"""
        return self.scheduler.check_missed_tasks()
