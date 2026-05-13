import schedule
import time
import logging
import threading
from tasks.auto_task import process_sms_notifications # Import the SMS task
from core.backup_manager import backup_manager       # Import the backup manager instance

# Setup logging for this module
log = logging.getLogger(__name__)


def run_pending_tasks():
    """
    An infinite loop that runs pending scheduled jobs.
    
    This function is designed to be the target of a background thread.
    """
    log.info("Scheduler thread started. Waiting for scheduled jobs.")
    while True:
        # Checks if any job is due to run.
        schedule.run_pending()
        # Waits for one second before checking again to avoid busy-waiting.
        time.sleep(1)


def start_scheduler():
    """
    Configures and starts the background scheduler.

    This function sets up the daily jobs for sending SMS and creating backups,
    and then starts the scheduler loop in a non-blocking daemon thread.
    """
    # Configure Jobs

    # Schedule the SMS notification process to run every day at a specific time.
    # The time '10:00' can be adjusted as needed.
    schedule.every().day.at("10:00").do(process_sms_notifications)
    log.info("Scheduled daily SMS check at 10:00.")

    # Schedule the database backup process to run every day at a different time.
    # The time '01:00' (1 AM) is chosen for off-peak hours.
    schedule.every().day.at("01:00").do(backup_manager.create_backup)
    log.info("Scheduled daily database backup at 01:00.")

    # Start the Scheduler Thread

    # Create a new thread that will run the 'run_pending_tasks' function.
    # Using a thread ensures that the scheduler does not block the main GUI.
    scheduler_thread = threading.Thread(target=run_pending_tasks)
    
    # Set 'daemon=True' so the thread will automatically exit when the main program closes.
    scheduler_thread.daemon = True
    
    # Start the thread.
    scheduler_thread.start()
    log.info("Scheduler background thread has been started.")
