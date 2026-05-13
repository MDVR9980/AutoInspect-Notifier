import os
import shutil
import logging
from datetime import datetime
from settings import DB_FILE_PATH, BACKUP_DIR # Import paths from the central settings file
from typing import Optional

# Setup logging for this module
log = logging.getLogger(__name__)


class BackupManager:
    """
    Manages the creation of database backups.

    This class handles the logic for creating timestamped copies of the
    main database file in a designated backup directory.
    """

    def __init__(self, db_path: str, backup_dir: str):
        """
        Initializes the BackupManager.

        Args:
            db_path (str): The full path to the source database file.
            backup_dir (str): The full path to the directory where backups will be stored.
        """
        # Store the provided paths.
        self.db_path = db_path
        self.backup_dir = backup_dir
        # Ensure the backup directory exists.
        self._ensure_backup_dir_exists()

    def _ensure_backup_dir_exists(self) -> None:
        """
        Checks if the backup directory exists and creates it if it doesn't.
        """
        try:
            # The 'exist_ok=True' argument prevents an error if the directory already exists.
            os.makedirs(self.backup_dir, exist_ok=True)
        except OSError as e:
            # Log an error if the directory could not be created (e.g., due to permissions).
            log.error(f"Could not create backup directory at {self.backup_dir}: {e}")
            # Raise the exception to notify the calling code of the failure.
            raise

    def create_backup(self) -> Optional[str]:
        """
        Creates a timestamped backup of the database file.

        The backup filename will be in the format: 'backup_YYYY-MM-DD_HH-MM-SS.db'.

        Returns:
            Optional[str]: The full path to the created backup file if successful,
                           otherwise None.
        """
        # Check if the source database file actually exists.
        if not os.path.exists(self.db_path):
            log.error(f"Source database file not found at {self.db_path}. Cannot create backup.")
            return None

        try:
            # Get the current time and format it for the filename.
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            # Construct the full filename for the backup.
            backup_filename = f"backup_{timestamp}.db"
            # Construct the full destination path.
            destination_path = os.path.join(self.backup_dir, backup_filename)

            # Copy the source database file to the backup destination.
            # shutil.copy2 attempts to preserve metadata.
            shutil.copy2(self.db_path, destination_path)

            # Log a success message with the path to the new backup.
            log.info(f"Database backup successfully created at: {destination_path}")
            return destination_path

        except (IOError, OSError) as e:
            # Catch file-related errors that might occur during the copy operation.
            log.error(f"Failed to create database backup: {e}")
            return None

# Global Instance
# Create a single, reusable instance of the manager using paths from settings.
backup_manager = BackupManager(db_path=DB_FILE_PATH, backup_dir=BACKUP_DIR)
