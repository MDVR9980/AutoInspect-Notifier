import openpyxl
import logging
from typing import Tuple
from core.db_manager import db_manager # Import the global DB manager instance

# Setup logging for this module
log = logging.getLogger(__name__)


def import_customers_from_excel(file_path: str) -> Tuple[int, int]:
    """
    Reads an Excel file and adds customer data to the database.

    Assumes the Excel file has three columns in order:
    Plate Number, Phone Number, Expiry Date (format YYYY/MM/DD).

    Args:
        file_path (str): The absolute path to the .xlsx file.

    Returns:
        Tuple[int, int]: A tuple containing (number of customers added, number of duplicates/failures).
    """
    added_count = 0
    failed_count = 0
    try:
        # Load the Excel workbook and select the active worksheet.
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active

        # Iterate over all rows in the sheet, starting from the second row to skip headers.
        for row in sheet.iter_rows(min_row=2, values_only=True):
            # Ensure the row has at least 3 columns to avoid errors.
            if len(row) < 3:
                failed_count += 1
                continue

            # Extract data, converting to string and stripping whitespace.
            plate = str(row[0]).strip()
            phone = str(row[1]).strip()
            expire_date = str(row[2]).strip() # Assuming date is already in 'YYYY/MM/DD' text format

            # Basic validation to ensure essential data is not empty.
            if not plate or not phone or not expire_date:
                log.warning(f"Skipping row with missing data: {row}")
                failed_count += 1
                continue

            # Attempt to add the customer to the database.
            # The db_manager's add_customer handles duplicate prevention.
            if db_manager.add_customer(plate, phone, expire_date):
                added_count += 1
            else:
                # This could be a duplicate or a database error.
                log.warning(f"Failed to add or duplicate customer: {plate}, {phone}")
                failed_count += 1
                
        log.info(f"Excel import complete. Added: {added_count}, Skipped/Duplicates: {failed_count}")

    except FileNotFoundError:
        log.error(f"Excel file not found at path: {file_path}")
        return 0, 0
    except Exception as e:
        # Catch any other unexpected errors during file processing.
        log.error(f"An error occurred during Excel import: {e}", exc_info=True)
        return added_count, failed_count
        
    return added_count, failed_count
