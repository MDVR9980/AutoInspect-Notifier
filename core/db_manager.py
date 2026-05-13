# autoinspect-notifier/core/db_manager.py

import sqlite3
import logging
from typing import Optional, List, Tuple

# --- Setup logging for this module ---
# This helps in debugging and tracking database operations.
log = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages all interactions with the SQLite database.

    This class encapsulates the database connection, table creation,
    and CRUD (Create, Read, Update, Delete) operations for the
    customer data.
    """

    def __init__(self, db_path: str):
        """
        Initializes the DatabaseManager.

        Args:
            db_path (str): The file path to the SQLite database.
        """
        # Store the path to the database file.
        self.db_path = db_path
        # Initialize the connection object to None. It will be created when connect() is called.
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        """
        Establishes a connection to the database.
        
        Raises:
            sqlite3.Error: If the connection to the database fails.
        """
        try:
            # Establish a connection to the SQLite database file.
            self.conn = sqlite3.connect(self.db_path)
            # Log a successful connection.
            log.info(f"Successfully connected to the database at {self.db_path}")
        except sqlite3.Error as e:
            # Log an error if the connection fails.
            log.error(f"Database connection failed: {e}")
            # Re-raise the exception to be handled by the caller.
            raise

    def close(self) -> None:
        """Closes the database connection if it is open."""
        # Check if a connection object exists.
        if self.conn:
            # Close the database connection.
            self.conn.close()
            # Log the action.
            log.info("Database connection closed.")

    def create_table(self) -> None:
        """
        Creates the 'customers' table if it does not already exist.
        
        The table stores customer information. The 'plate_number' column
        is defined as UNIQUE to prevent duplicate entries for the same vehicle.
        """
        # Ensure there is an active connection.
        if not self.conn:
            log.error("Cannot create table: No active database connection.")
            return

        try:
            # SQL statement to create the customers table.
            # "IF NOT EXISTS" prevents an error if the table already exists.
            # "UNIQUE" on plate_number ensures each vehicle is registered only once.
            create_table_query = """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate_number TEXT NOT NULL UNIQUE,
                phone_number TEXT NOT NULL,
                expiry_date TEXT NOT NULL,
                sms_status TEXT DEFAULT 'Pending'
            );
            """
            # Create a cursor object to execute SQL commands.
            cursor = self.conn.cursor()
            # Execute the SQL statement.
            cursor.execute(create_table_query)
            # Commit the changes to the database.
            self.conn.commit()
            # Log the successful creation of the table.
            log.info("'customers' table created or already exists.")
        except sqlite3.Error as e:
            # Log any error that occurs during table creation.
            log.error(f"Error creating table: {e}")

    def add_customer(self, plate: str, phone: str, expiry_date: str) -> bool:
        """
        Adds a new customer record to the database.

        Args:
            plate (str): The car's license plate number.
            phone (str): The customer's mobile phone number.
            expiry_date (str): The inspection expiry date in 'YYYY-MM-DD' format.
            
        Returns:
            bool: True if the customer was added successfully, False if the
                  plate number already exists or another error occurred.
        """
        # Ensure there is an active connection.
        if not self.conn:
            log.error("Cannot add customer: No active database connection.")
            return False

        try:
            # SQL statement for inserting a new record.
            # Using '?' placeholders is a security best practice to prevent SQL injection.
            insert_query = "INSERT INTO customers (plate_number, phone_number, expiry_date) VALUES (?, ?, ?)"
            # Create a cursor object.
            cursor = self.conn.cursor()
            # Execute the query with the provided data tuple.
            cursor.execute(insert_query, (plate, phone, expiry_date))
            # Commit the transaction to save the record.
            self.conn.commit()
            # Log the successful insertion.
            log.info(f"Added customer: Plate={plate}, Phone={phone}")
            return True
        except sqlite3.IntegrityError:
            # This specific error is raised when the UNIQUE constraint on plate_number fails.
            log.warning(f"Attempted to add a duplicate plate number: {plate}")
            return False
        except sqlite3.Error as e:
            # Log any other database error during insertion.
            log.error(f"Failed to add customer {plate}: {e}")
            return False

    def get_all_customers(self) -> List[Tuple]:
        """
        Retrieves all customer records from the database.

        Returns:
            List[Tuple]: A list of tuples, where each tuple represents a customer record.
                         Returns an empty list if no records are found or an error occurs.
        """
        # Ensure there is an active connection.
        if not self.conn:
            log.error("Cannot get customers: No active database connection.")
            return []

        try:
            # SQL query to select relevant columns from the customers table.
            select_query = "SELECT plate_number, phone_number, expiry_date, sms_status FROM customers"
            # Create a cursor.
            cursor = self.conn.cursor()
            # Execute the query.
            cursor.execute(select_query)
            # Fetch all rows from the query result.
            return cursor.fetchall()
        except sqlite3.Error as e:
            # Log any error during data retrieval.
            log.error(f"Failed to retrieve customers: {e}")
            # Return an empty list in case of an error.
            return []

    def update_customer_status(self, plate_number: str, new_status: str) -> None:
        """
        Updates the SMS status for a specific customer identified by plate number.

        Args:
            plate_number (str): The license plate of the customer to update.
            new_status (str): The new status to set (e.g., 'Sent', 'Failed').
        """
        # Ensure there is an active connection.
        if not self.conn:
            log.error("Cannot update status: No active database connection.")
            return

        try:
            # SQL statement to update the sms_status for a given plate_number.
            update_query = "UPDATE customers SET sms_status = ? WHERE plate_number = ?"
            # Create a cursor.
            cursor = self.conn.cursor()
            # Execute the update command with the new status and plate number.
            cursor.execute(update_query, (new_status, plate_number))
            # Commit the changes to the database.
            self.conn.commit()
            
            # cursor.rowcount tells us how many rows were affected.
            if cursor.rowcount > 0:
                # Log a success message if at least one row was updated.
                log.info(f"Updated status for plate {plate_number} to '{new_status}'.")
            else:
                # Log a warning if no matching plate number was found.
                log.warning(f"No customer found with plate {plate_number} to update.")
        except sqlite3.Error as e:
            # Log any error that occurs during the update.
            log.error(f"Failed to update status for plate {plate_number}: {e}")

    def delete_all_customers(self) -> None:
        """
        Deletes all records from the 'customers' table. This is a destructive
        operation and should be used with caution.
        """
        # Ensure there is an active connection.
        if not self.conn:
            log.error("Cannot delete customers: No active database connection.")
            return
            
        try:
            # SQL statement to delete all rows from the table.
            delete_query = "DELETE FROM customers"
            # Create a cursor.
            cursor = self.conn.cursor()
            # Execute the delete command.
            cursor.execute(delete_query)
            # Commit the changes.
            self.conn.commit()
            # Log the action.
            log.info("All customer records have been deleted.")
        except sqlite3.Error as e:
            # Log any error during deletion.
            log.error(f"Failed to delete all customers: {e}")
