import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog,
    QStatusBar
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QIcon

# Local Imports
from ui.styles import light_theme_qss, dark_theme_qss
from utils.excel_importer import import_customers_from_excel
from core.db_manager import db_manager
from settings import APP_ICON_PATH # Import the icon path

# --- Setup logging for this module ---
log = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    The main window of the AutoInspect Notifier application.
    
    Handles the user interface, displays customer data, and provides
    controls for importing data and changing the theme.
    """
    def __init__(self):
        super().__init__()
        
        # App Settings
        # QSettings provides a persistent way to store application settings.
        self.settings = QSettings("MyCompany", "AutoInspectNotifier")

        # Window Configuration
        self.setWindowTitle("AutoInspect Notifier")
        self.setGeometry(100, 100, 800, 600) # x, y, width, height
        self.setWindowIcon(QIcon(APP_ICON_PATH))

        # Initialize UI Components
        self._init_widgets()
        self._init_layout()
        self._connect_signals()

        # Final Setup
        self.load_theme() # Apply the last used theme on startup
        self.populate_table() # Load initial data into the table
        log.info("Main window initialized successfully.")

    def _init_widgets(self):
        """Initializes all the widgets used in the window."""
        self.import_button = QPushButton("Import from Excel")
        self.refresh_button = QPushButton("Refresh List")
        self.theme_button = QPushButton("Toggle Theme")
        
        # Table Widget Setup
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Plate", "Phone", "Expire Date", "SMS Status"])
        # Make the table columns resize to fit the window width.
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Disable editing of table cells by the user.
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def _init_layout(self):
        """Sets up the layout of the widgets."""
        # Main Layouts
        # Central widget will hold everything inside the main window.
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        # The main vertical layout for the central widget.
        main_layout = QVBoxLayout(central_widget)
        # A horizontal layout for the top buttons.
        button_layout = QHBoxLayout()

        # Add Widgets to Layouts
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch() # Pushes the theme button to the right
        button_layout.addWidget(self.theme_button)
        
        # Add the button layout and the table to the main vertical layout.
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table)

    def _connect_signals(self):
        """Connects widget signals to their corresponding slots (functions)."""
        self.import_button.clicked.connect(self.import_excel_data)
        self.refresh_button.clicked.connect(self.populate_table)
        self.theme_button.clicked.connect(self.toggle_theme)

    def populate_table(self):
        """Fetches all customer data from the database and displays it in the table."""
        try:
            log.info("Populating customer table.")
            # Retrieve data from the database.
            customers = db_manager.get_all_customers()
            
            # Clear any existing rows to prevent duplication.
            self.table.setRowCount(0)
            self.table.setRowCount(len(customers))

            # Iterate through the data and add it to the table.
            for row_idx, row_data in enumerate(customers):
                for col_idx, col_data in enumerate(row_data):
                    item = QTableWidgetItem(str(col_data))
                    self.table.setItem(row_idx, col_idx, item)
            
            self.status_bar.showMessage(f"Loaded {len(customers)} customers.", 3000) # Message disappears after 3s
        except Exception as e:
            log.error(f"Failed to populate table: {e}", exc_info=True)
            self.status_bar.showMessage("Error loading data from database.", 5000)

    def import_excel_data(self):
        """Opens a file dialog to select an Excel file and imports the data."""
        # The 'self' argument sets the main window as the parent for the dialog.
        # The second argument is the dialog title.
        # The third is the default directory.
        # The fourth filters for specific file types.
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Excel File", "", "Excel Files (*.xlsx *.xls)"
        )

        # Proceed only if a file path was selected.
        if file_path:
            log.info(f"Starting Excel import from: {file_path}")
            self.status_bar.showMessage("Importing from Excel...")
            QApplication.processEvents() # Update the UI to show the message

            added, failed = import_customers_from_excel(file_path)

            # Show the result in the status bar.
            message = f"Import complete. Added: {added}, Skipped/Duplicates: {failed}"
            self.status_bar.showMessage(message, 5000)
            log.info(message)
            
            # Refresh the table to show the newly imported data.
            self.populate_table()

    def toggle_theme(self):
        """Switches the application's stylesheet between light and dark themes."""
        current_theme = self.settings.value("theme", "light") # Default to 'light' if not set
        if current_theme == "light":
            self.apply_theme("dark")
        else:
            self.apply_theme("light")
            
    def apply_theme(self, theme_name: str):
        """
        Applies the specified theme and saves the preference.

        Args:
            theme_name (str): The name of the theme to apply ('light' or 'dark').
        """
        if theme_name == "dark":
            self.setStyleSheet(dark_theme_qss)
            self.settings.setValue("theme", "dark")
            log.info("Applied dark theme.")
        else: # Default to light
            self.setStyleSheet(light_theme_qss)