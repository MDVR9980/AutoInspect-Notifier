import os
from pathlib import Path

# Base directory of the project
# This will be the root folder where main.py is located.
BASE_DIR = Path(__file__).resolve().parent

# Directory Settings
# We define all necessary paths based on the BASE_DIR.

# Main data directory (for database)
DATA_DIR = BASE_DIR / "data"

# Backup directory
BACKUP_DIR = BASE_DIR / "backup"

# Log directory
LOG_DIR = BASE_DIR / "logs"


APP_ICON_PATH = BASE_DIR / "data/assets/icons/app_icon.ico"

# Database Settings
DB_NAME = "database.db"
DB_FILE_PATH = DATA_DIR / DB_NAME


# Log Settings
LOG_FILE_NAME = "app.log"
LOG_FILE_PATH = LOG_DIR / LOG_FILE_NAME


# Ghasdak SMS API Settings
# IMPORTANT: Replace with your actual API key from ghasdak.io
GHASDAK_API_KEY = "a5842695aa0151c0c3ae0c8a80b0bfd04d53f9319568940e487221abcd11d11aV8S4vz9xUP6BSeuy"


# Scheduler Settings
# Time to send SMS notifications every day (24-hour format)
SMS_SCHEDULE_TIME = "10:00"

# Time to perform database backup every day (24-hour format)
BACKUP_SCHEDULE_TIME = "01:00"
