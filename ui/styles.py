"""
Contains QSS (Qt Style Sheets) for the light and dark themes of the application.
"""

# Light Theme
light_theme_qss = """
    QWidget {
        background-color: #f0f0f0;
        color: #333;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    QMainWindow {
        background-color: #e9e9e9;
    }
    QPushButton {
        background-color: #0078d7;
        color: white;
        border: 1px solid #005a9e;
        padding: 8px 16px;
        border-radius: 4px;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: #005a9e;
    }
    QPushButton:pressed {
        background-color: #003c6a;
    }
    QTableWidget {
        background-color: white;
        border: 1px solid #ccc;
        gridline-color: #ddd;
    }
    QHeaderView::section {
        background-color: #0078d7;
        color: white;
        padding: 6px;
        border: 1px solid #005a9e;
        font-weight: bold;
    }
    QStatusBar {
        background-color: #f0f0f0;
        color: #333;
    }
    QLabel {
        font-size: 14px;
    }
"""

# Dark Theme
dark_theme_qss = """
    QWidget {
        background-color: #2d2d2d;
        color: #f0f0f0;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    QMainWindow {
        background-color: #252525;
    }
    QPushButton {
        background-color: #4a4a4a;
        color: #f0f0f0;
        border: 1px solid #666;
        padding: 8px 16px;
        border-radius: 4px;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: #5a5a5a;
    }
    QPushButton:pressed {
        background-color: #6a6a6a;
    }
    QTableWidget {
        background-color: #3c3c3c;
        color: #f0f0f0;
        border: 1px solid #555;
        gridline-color: #555;
    }
    QHeaderView::section {
        background-color: #4a4a4a;
        color: #f0f0f0;
        padding: 6px;
        border: 1px solid #666;
        font-weight: bold;
    }
    QStatusBar {
        background-color: #2d2d2d;
        color: #f0f0f0;
    }
    QLabel {
        font-size: 14px;
    }
"""
