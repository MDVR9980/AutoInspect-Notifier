"""
مدیریت دیتابیس SQLite
"""
import sqlite3
from pathlib import Path
import logging
from typing import List, Dict, Optional, Tuple
from jdatetime import datetime as jdatetime

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.connection = None
        self._init_database()

    def _init_database(self):
        """ایجاد دیتابیس و جدول‌ها"""
        try:
            self.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False
            )

            self.connection.row_factory = sqlite3.Row

            cursor = self.connection.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subscribers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone TEXT NOT NULL,
                    plate TEXT NOT NULL,
                    visit_date TEXT NOT NULL,
                    expire_date TEXT NOT NULL,
                    sms_status TEXT DEFAULT 'در انتظار',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.connection.commit()

            logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def _calculate_expire_date(self, visit_date: str) -> str:
        """
        محاسبه تاریخ انقضا
        یک سال بعد از تاریخ مراجعه
        """
        try:
            parts = visit_date.split('/')

            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])

            visit_jdate = jdatetime(year, month, day)

            expire_jdate = visit_jdate.replace(
                year=visit_jdate.year + 1
            )

            return expire_jdate.strftime('%Y/%m/%d')

        except Exception as e:
            logger.error(f"Expire date calculation error: {e}")
            return visit_date

    def add_subscriber(
        self,
        phone: str,
        plate: str,
        visit_date: str
    ) -> bool:
        """افزودن مشترک"""

        try:
            expire_date = self._calculate_expire_date(
                visit_date
            )

            cursor = self.connection.cursor()

            cursor.execute("""
                INSERT INTO subscribers (
                    phone,
                    plate,
                    visit_date,
                    expire_date,
                    sms_status
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                phone,
                plate,
                visit_date,
                expire_date,
                "در انتظار"
            ))

            self.connection.commit()

            logger.info(f"Subscriber added: {plate}")

            return True

        except Exception as e:
            logger.error(f"Add subscriber error: {e}")
            return False

    def add_subscribers_bulk(
        self,
        subscribers: List[Tuple[str, str, str]]
    ) -> int:
        """
        افزودن گروهی مشترکین

        فرمت:
        [
            (phone, plate, visit_date),
            ...
        ]
        """

        inserted_count = 0

        try:
            cursor = self.connection.cursor()

            for phone, plate, visit_date in subscribers:

                expire_date = self._calculate_expire_date(
                    visit_date
                )

                cursor.execute("""
                    INSERT INTO subscribers (
                        phone,
                        plate,
                        visit_date,
                        expire_date,
                        sms_status
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    phone,
                    plate,
                    visit_date,
                    expire_date,
                    "در انتظار"
                ))

                inserted_count += 1

            self.connection.commit()

            logger.info(
                f"{inserted_count} subscribers added"
            )

            return inserted_count

        except Exception as e:
            logger.error(f"Bulk insert error: {e}")
            return 0

    def get_all_subscribers(self) -> List[Dict]:
        """دریافت همه مشترکین"""

        try:
            cursor = self.connection.cursor()

            cursor.execute("""
                SELECT *
                FROM subscribers
                ORDER BY id DESC
            """)

            rows = cursor.fetchall()

            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Get subscribers error: {e}")
            return []

    def get_subscriber_by_id(
        self,
        subscriber_id: int
    ) -> Optional[Dict]:
        """دریافت مشترک با شناسه"""

        try:
            cursor = self.connection.cursor()

            cursor.execute("""
                SELECT *
                FROM subscribers
                WHERE id = ?
            """, (subscriber_id,))

            row = cursor.fetchone()

            if row:
                return dict(row)

            return None

        except Exception as e:
            logger.error(f"Get subscriber by id error: {e}")
            return None

    def get_subscribers_for_reminder(
        self,
        target_expire_date: str
    ) -> List[Dict]:
        """
        دریافت مشترکینی که باید پیامک دریافت کنند
        """

        try:
            cursor = self.connection.cursor()

            cursor.execute("""
                SELECT *
                FROM subscribers
                WHERE expire_date = ?
                AND sms_status != 'ارسال شد'
            """, (target_expire_date,))

            rows = cursor.fetchall()

            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Reminder query error: {e}")
            return []

    def update_sms_status(
        self,
        subscriber_id: int,
        status: str
    ) -> bool:
        """آپدیت وضعیت پیامک"""

        try:
            cursor = self.connection.cursor()

            cursor.execute("""
                UPDATE subscribers
                SET sms_status = ?
                WHERE id = ?
            """, (
                status,
                subscriber_id
            ))

            self.connection.commit()

            logger.info(
                f"SMS status updated for ID {subscriber_id}"
            )

            return True

        except Exception as e:
            logger.error(f"Update sms status error: {e}")
            return False

    def delete_subscriber(
        self,
        subscriber_id: int
    ) -> bool:
        """حذف مشترک"""

        try:
            cursor = self.connection.cursor()

            cursor.execute("""
                DELETE FROM subscribers
                WHERE id = ?
            """, (subscriber_id,))

            self.connection.commit()

            logger.info(
                f"Subscriber deleted: {subscriber_id}"
            )

            return True

        except Exception as e:
            logger.error(f"Delete subscriber error: {e}")
            return False

    def delete_all_subscribers(self) -> bool:
        """حذف همه مشترکین"""

        try:
            cursor = self.connection.cursor()

            cursor.execute("""
                DELETE FROM subscribers
            """)

            self.connection.commit()

            logger.warning("All subscribers deleted")

            return True

        except Exception as e:
            logger.error(f"Delete all error: {e}")
            return False

    def get_total_count(self) -> int:
        """تعداد کل مشترکین"""

        try:
            cursor = self.connection.cursor()

            cursor.execute("""
                SELECT COUNT(*) as total
                FROM subscribers
            """)

            row = cursor.fetchone()

            return row["total"]

        except Exception as e:
            logger.error(f"Count error: {e}")
            return 0

    def reset_all_sms_status(self) -> bool:
        """ریست وضعیت پیامک همه رکوردها"""

        try:
            cursor = self.connection.cursor()

            cursor.execute("""
                UPDATE subscribers
                SET sms_status = 'در انتظار'
            """)

            self.connection.commit()

            logger.info("All sms statuses reset")

            return True

        except Exception as e:
            logger.error(f"Reset sms status error: {e}")
            return False

    def close(self):
        """بستن اتصال دیتابیس"""

        try:
            if self.connection:
                self.connection.close()
                logger.info("Database connection closed")

        except Exception as e:
            logger.error(f"Close connection error: {e}")

    def search_subscribers(self, text: str) -> List[Dict]:
        """
        جستجوی مشترکین بر اساس شماره موبایل یا پلاک
        """
        try:
            cursor = self.connection.cursor()

            query = """
                SELECT id, phone, plate, visit_date, expire_date, sms_status, created_at
                FROM subscribers
                WHERE phone LIKE ? OR plate LIKE ?
                ORDER BY id DESC
            """

            pattern = f"%{text}%"
            cursor.execute(query, (pattern, pattern))

            rows = cursor.fetchall()

            # تبدیل خروجی از Row به dict
            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
