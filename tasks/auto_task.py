import logging
from datetime import datetime, timedelta
from typing import List, Tuple

# Import core components
from ..core.db_manager import DatabaseManager
from ..core.sms_api import SmsApiClient

# Setup logging for this module
log = logging.getLogger(__name__)


class TaskManager:
    """
    Manages the automated task of checking for upcoming expirations
    and sending SMS notifications.
    """

    def __init__(self, db_manager: DatabaseManager, sms_client: SmsApiClient):
        """
        Initializes the TaskManager.

        Args:
            db_manager (DatabaseManager): An instance for database operations.
            sms_client (SmsApiClient): An instance for sending messages.
        """
        self.db_manager = db_manager
        self.sms_client = sms_client

    def check_and_send_reminders(self, days_before_expiry: int = 7) -> None:
        """
        Fetches customers whose inspection is expiring soon and sends them a reminder.

        Args:
            days_before_expiry (int): Days before expiry to send a notification.
        """
        log.info("Starting scheduled task: Check and send reminders.")
        try:
            self.db_manager.connect()
            
            all_customers = self.db_manager.get_all_customers()
            if not all_customers:
                log.info("No customers found in the database. Task finished.")
                return

            customers_to_notify = self._filter_customers_for_notification(all_customers, days_before_expiry)
            if not customers_to_notify:
                log.info("No customers require notification today. Task finished.")
                return

            log.info(f"Found {len(customers_to_notify)} customers to notify.")

            for customer in customers_to_notify:
                plate, phone, expiry_date, _ = customer
                message = self._create_reminder_message(plate, expiry_date)
                response = self.sms_client.send_sms(receptor=phone, message=message)
                
                # Update status based on API response
                if response and response.get('result', {}).get('status') == 'success':
                    self.db_manager.update_customer_status(plate, 'Sent')
                else:
                    self.db_manager.update_customer_status(plate, 'Failed')

        except Exception as e:
            log.error(f"An error occurred during the reminder task: {e}")
        finally:
            self.db_manager.close()
            log.info("Reminder task finished.")

    def _filter_customers_for_notification(self, customers: List[Tuple], days_before: int) -> List[Tuple]:
        """Filters customers whose expiry date is exactly 'days_before' from now."""
        today = datetime.now().date()
        notification_date = today + timedelta(days=days_before)
        
        filtered_list = []
        for customer in customers:
            plate, _, expiry_date_str, status = customer
            try:
                expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
                # Notify if expiry is on the target date and SMS has not been sent successfully yet.
                if expiry_date == notification_date and status.lower() != 'sent':
                    filtered_list.append(customer)
            except ValueError:
                log.warning(f"Invalid date format for customer with plate {plate}: '{expiry_date_str}'.")
        
        return filtered_list

    def _create_reminder_message(self, plate_number: str, expiry_date: str) -> str:
        """Creates a formatted SMS reminder message."""
        message = (
            f"مشتری گرامی،\n"
            f"تاریخ انقضای معاینه فنی خودروی شما به شماره پلاک {plate_number} "
            f"در تاریخ {expiry_date} به پایان می‌رسد.\n"
            f"لطفا جهت تمدید اقدام فرمایید.\n"
            f"[نام مرکز شما]"
        )
        return message
