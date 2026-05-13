# autoinspect-notifier/main.py

import sys
import logging
import os
from logging.handlers import RotatingFileHandler

from PyQt6.QtWidgets import QApplication

# --- Local Imports ---
from settings import DATA_DIR, BACKUP_DIR, LOG_DIR, LOG_FILE_PATH
from ui.main_window import MainWindow
from tasks.scheduler import start_scheduler_in_thread
from core.db_manager import db_manager


def setup_logging():
    """
    Configures the application-wide logging.

    Logs are sent to both the console and a rotating file (`logs/app.log`).
    File rotation keeps the log file from growing indefinitely.
    """
    # Create the logs directory if it doesn't exist.
    LOG_DIR.mkdir(exist_ok=True)

    # --- Create a logger instance ---
    # Get the root logger. All other loggers in the app will inherit from this.
    log = logging.getLogger()
    log.setLevel(logging.INFO) # Set the minimum level of messages to handle.

    # --- Create a formatter ---
    # Defines the format of the log messages.
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # --- Console Handler ---
    # Sends log messages to the standard output (the console).
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    log.addHandler(console_handler)

    # --- File Handler ---
    # Writes log messages to a file.
    # RotatingFileHandler manages log files, creating new ones when they reach a certain size.
    file_handler = RotatingFileHandler(
        LOG_FILE_PATH, maxBytes=5*1024*1024, backupCount=2 # 5 MB per file, 2 backups
    )
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)

    log.info("Logging configured successfully.")

def ensure_directories_exist():
    """
    Creates the necessary data and backup directories if they don't already exist.
    This prevents errors when the application tries to write files.
    """
    try:
        DATA_DIR.mkdir(exist_ok=True)
        BACKUP_DIR.mkdir(exist_ok=True)
        LOG_DIR.mkdir(exist_ok=True)
        logging.info("Ensured all necessary directories exist.")
    except OSError as e:
        logging.error(f"Failed to create necessary directories: {e}", exc_info=True)
        # In a real app, you might want to show an error dialog and exit.
        sys.exit(1) # Exit if we can't create essential folders.

def main():
    """
    The main entry point of the application.
    """
    # 1. Configure logging as the very first step.
    setup_logging()

    # 2. Ensure all required folders exist.
    ensure_directories_exist()

    # 3. Initialize the database connection and tables.
    db_manager.initialize()

    # 4. Start the background scheduler thread.
    # This will handle daily SMS checks and backups without freezing the UI.
    scheduler_thread = start_scheduler_in_thread()
    logging.info("Background scheduler started.")

    # 5. Create and run the PyQt application.
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # Start the application's event loop.
    # The sys.exit() ensures a clean exit.
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
