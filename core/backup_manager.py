"""
مدیریت پشتیبان‌گیری و بازیابی دیتابیس
"""
import os
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)


class BackupManager:
    def __init__(self, db_path: str, backup_dir: str):
        self.db_path = db_path
        self.backup_dir = backup_dir
        
        # ایجاد پوشه backup در صورت عدم وجود
        Path(self.backup_dir).mkdir(parents=True, exist_ok=True)

    def create_backup(self) -> Optional[str]:
        """
        ایجاد فایل پشتیبان با فرمت: backup_YYYY_MM_DD_HH_MM_SS.db
        
        بازگشت:
            مسیر فایل پشتیبان یا None در صورت خطا
        """
        try:
            if not os.path.exists(self.db_path):
                logger.error(f"Database file not found: {self.db_path}")
                return None

            # ساخت نام فایل با timestamp
            timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            backup_filename = f"backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)

            # کپی فایل دیتابیس
            shutil.copy2(self.db_path, backup_path)

            logger.info(f"Backup created: {backup_path}")
            return backup_path

        except PermissionError:
            logger.error("Permission denied for backup operation")
            return None

        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return None

    def restore_backup(self, backup_path: str) -> bool:
        """
        بازیابی دیتابیس از فایل پشتیبان
        
        آرگومان‌ها:
            backup_path: مسیر فایل پشتیبان
            
        بازگشت:
            True در صورت موفقیت، False در غیر این صورت
        """
        try:
            if not os.path.exists(backup_path):
                logger.error(f"Backup file not found: {backup_path}")
                return False

            # ایجاد نسخه امنیتی از دیتابیس فعلی قبل از بازیابی
            if os.path.exists(self.db_path):
                temp_backup = f"{self.db_path}.temp_backup"
                shutil.copy2(self.db_path, temp_backup)

                try:
                    # بازیابی از فایل پشتیبان
                    shutil.copy2(backup_path, self.db_path)
                    logger.info(f"Database restored from: {backup_path}")
                    
                    # حذف نسخه موقت
                    if os.path.exists(temp_backup):
                        os.remove(temp_backup)
                    
                    return True

                except Exception as e:
                    # در صورت خطا، بازگردانی نسخه قبلی
                    logger.error(f"Restore failed, reverting: {e}")
                    if os.path.exists(temp_backup):
                        shutil.copy2(temp_backup, self.db_path)
                        os.remove(temp_backup)
                    return False
            else:
                # اگر دیتابیس وجود نداشت، مستقیم بازیابی می‌کنیم
                shutil.copy2(backup_path, self.db_path)
                logger.info(f"Database restored from: {backup_path}")
                return True

        except PermissionError:
            logger.error("Permission denied for restore operation")
            return False

        except Exception as e:
            logger.error(f"Restore operation failed: {e}")
            return False

    def list_backups(self) -> List[dict]:
        """
        لیست تمام فایل‌های پشتیبان
        
        بازگشت:
            لیستی از دیکشنری‌ها شامل نام و مسیر فایل‌های پشتیبان
        """
        try:
            backups = []
            
            if not os.path.exists(self.backup_dir):
                return backups

            for filename in os.listdir(self.backup_dir):
                if filename.startswith("backup_") and filename.endswith(".db"):
                    file_path = os.path.join(self.backup_dir, filename)
                    file_stat = os.stat(file_path)
                    backup_info = {
                        "filename": filename,
                        "path": file_path,
                        "size": round(file_stat.st_size / 1024, 2),  # KB
                        "created_at": datetime.fromtimestamp(
                            file_stat.st_ctime
                        ).strftime("%Y-%m-%d %H:%M:%S")
                    }

                    backups.append(backup_info)

            # مرتب‌سازی بر اساس جدیدترین فایل
            backups.sort(
                key=lambda x: x["created_at"],
                reverse=True
            )

            return backups

        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []

    def delete_backup(self, backup_path: str) -> bool:
        """
        حذف فایل پشتیبان
        
        آرگومان‌ها:
            backup_path: مسیر فایل بکاپ
            
        بازگشت:
            True در صورت موفقیت
        """
        try:
            if not os.path.exists(backup_path):
                logger.warning(f"Backup file not found: {backup_path}")
                return False

            os.remove(backup_path)
            logger.info(f"Backup deleted: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete backup: {e}")
            return False

    def get_latest_backup(self) -> Optional[str]:
        """
        دریافت جدیدترین فایل پشتیبان
        
        بازگشت:
            مسیر جدیدترین بکاپ
        """
        try:
            backups = self.list_backups()

            if not backups:
                return None

            return backups[0]["path"]

        except Exception as e:
            logger.error(f"Failed to get latest backup: {e}")
            return None

    def backup_exists(self, backup_path: str) -> bool:
        """
        بررسی وجود فایل بکاپ
        """
        return os.path.exists(backup_path)

    def get_backup_count(self) -> int:
        """
        تعداد فایل‌های بکاپ
        """
        return len(self.list_backups())

    def clear_old_backups(self, keep_last: int = 10) -> int:
        """
        حذف بکاپ‌های قدیمی
        
        آرگومان‌ها:
            keep_last: تعداد بکاپ‌هایی که نگه داشته می‌شوند
            
        بازگشت:
            تعداد فایل‌های حذف شده
        """
        try:
            backups = self.list_backups()

            if len(backups) <= keep_last:
                return 0

            deleted_count = 0
            old_backups = backups[keep_last:]

            for backup in old_backups:
                if self.delete_backup(backup["path"]):
                    deleted_count += 1

            logger.info(f"{deleted_count} old backups deleted")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to clear old backups: {e}")
            return 0
