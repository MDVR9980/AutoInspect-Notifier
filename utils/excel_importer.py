import pandas as pd
import logging
#
# !! CHANGE HERE !!
# We import the CLASS, not an instance.
from core.db_manager import DatabaseManager

def import_customers_from_excel(file_path: str, db_manager: DatabaseManager) -> tuple[int, int]:
    """
    Reads customer data from an Excel file and adds them to the database.

    Args:
        file_path (str): The path to the Excel file.
        db_manager (DatabaseManager): An instance of the database manager to use.

    Returns:
        tuple[int, int]: A tuple containing (successful_imports, failed_imports).
    """
    if not file_path:
        return 0, 0

    try:
        df = pd.read_excel(file_path)

        # Ensure required columns exist
        required_columns = ['name', 'phone', 'car_model', 'car_id', 'last_service_date', 'inspection_expiry_date']
        if not all(col in df.columns for col in required_columns):
            logging.error(f"Excel file is missing one of the required columns: {required_columns}")
            return 0, len(df)

        successful_imports = 0
        failed_imports = 0

        for _, row in df.iterrows():
            try:
                # Add customer using the provided db_manager instance
                is_added = db_manager.add_customer(
                    name=row['name'],
                    phone=str(row['phone']),
                    car_model=row['car_model'],
                    car_id=str(row['car_id']),
                    last_service_date=str(row['last_service_date']),
                    inspection_expiry_date=str(row['inspection_expiry_date'])
                )
                if is_added:
                    successful_imports += 1
                else:
                    failed_imports += 1 # Likely a duplicate
            except Exception as e:
                logging.warning(f"Could not process row {row.to_dict()}: {e}")
                failed_imports += 1
        
        logging.info(f"Import finished. Successful: {successful_imports}, Failed/Duplicates: {failed_imports}")
        return successful_imports, failed_imports

    except FileNotFoundError:
        logging.error(f"Excel file not found at path: {file_path}")
        return 0, 0
    except Exception as e:
        logging.error(f"An unexpected error occurred during Excel import: {e}")
        return 0, 0
