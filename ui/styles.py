# styles.py

def get_light_theme():
    return """
    * {
        font-family: 'Vazirmatn', 'Segoe UI', Tahoma, sans-serif;
        font-size: 13px;
    }
    
    QMainWindow, QWidget {
        background-color: #f8fafc;
        color: #1e293b;
    }
    
    /* تنظیمات تب‌ها */
    QTabWidget::pane {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        background: #ffffff;
        top: -1px;
    }
    QTabBar::tab {
        background-color: #f1f5f9;
        color: #64748b;
        padding: 10px 20px;
        margin-right: 2px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        border: 1px solid #e2e8f0;
        border-bottom: none;
    }
    QTabBar::tab:selected {
        background-color: #ffffff;
        color: #0ea5e9;
        font-weight: bold;
        border-top: 3px solid #0ea5e9;
    }
    QTabBar::tab:hover:!selected {
        background-color: #e2e8f0;
    }

    /* تنظیمات GroupBox */
    QGroupBox {
        font-weight: bold;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        margin-top: 15px;
        background-color: #ffffff;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 10px;
        color: #475569;
    }

    /* ورودی‌های متنی و کمبوباکس */
    QLineEdit, QComboBox {
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 6px 12px;
        background-color: #ffffff;
        selection-background-color: #0ea5e9;
    }
    QLineEdit:focus, QComboBox:focus {
        border: 2px solid #0ea5e9;
    }
    
    /* دکمه‌های عمومی */
    QPushButton {
        background-color: #0ea5e9;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #0284c7;
    }
    QPushButton:pressed {
        background-color: #0369a1;
    }
    QPushButton:disabled {
        background-color: #cbd5e1;
        color: #94a3b8;
    }

    /* دکمه ثبت (سبز) */
    QPushButton#btn_submit {
        background-color: #10b981;
    }
    QPushButton#btn_submit:hover { background-color: #059669; }

    /* دکمه حذف (قرمز) */
    QPushButton#btn_delete_all {
        background-color: #ef4444;
    }
    QPushButton#btn_delete_all:hover { background-color: #dc2626; }

    /* جدول */
    QTableWidget {
        background-color: #ffffff;
        alternate-background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        gridline-color: #f1f5f9;
        outline: none;
    }
    QHeaderView::section {
        background-color: #f1f5f9;
        color: #475569;
        font-weight: bold;
        padding: 8px;
        border: none;
        border-bottom: 2px solid #cbd5e1;
    }
    QTableWidget::item:selected {
        background-color: #bae6fd;
        color: #0c4a6e;
    }
    """

def get_dark_theme():
    return """
    * {
        font-family: 'Vazirmatn', 'Segoe UI', Tahoma, sans-serif;
        font-size: 13px;
    }
    
    QMainWindow, QWidget {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* تنظیمات تب‌ها */
    QTabWidget::pane {
        border: 1px solid #334155;
        border-radius: 8px;
        background: #1e293b;
        top: -1px;
    }
    QTabBar::tab {
        background-color: #0f172a;
        color: #94a3b8;
        padding: 10px 20px;
        margin-right: 2px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        border: 1px solid #334155;
        border-bottom: none;
    }
    QTabBar::tab:selected {
        background-color: #1e293b;
        color: #38bdf8;
        font-weight: bold;
        border-top: 3px solid #38bdf8;
    }
    QTabBar::tab:hover:!selected {
        background-color: #1e293b;
    }

    /* تنظیمات GroupBox */
    QGroupBox {
        font-weight: bold;
        border: 1px solid #334155;
        border-radius: 8px;
        margin-top: 15px;
        background-color: #1e293b;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 10px;
        color: #cbd5e1;
    }

    /* ورودی‌های متنی و کمبوباکس */
    QLineEdit, QComboBox {
        border: 1px solid #475569;
        border-radius: 6px;
        padding: 6px 12px;
        background-color: #0f172a;
        color: #f8fafc;
        selection-background-color: #38bdf8;
    }
    QLineEdit:focus, QComboBox:focus {
        border: 2px solid #38bdf8;
    }
    
    /* دکمه‌های عمومی */
    QPushButton {
        background-color: #0ea5e9;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #38bdf8;
    }
    QPushButton:pressed {
        background-color: #0284c7;
    }
    
    /* دکمه ثبت (سبز) */
    QPushButton#btn_submit {
        background-color: #10b981;
    }
    QPushButton#btn_submit:hover { background-color: #34d399; }

    /* دکمه حذف (قرمز) */
    QPushButton#btn_delete_all {
        background-color: #ef4444;
    }
    QPushButton#btn_delete_all:hover { background-color: #f87171; }

    /* جدول */
    QTableWidget {
        background-color: #1e293b;
        alternate-background-color: #0f172a;
        border: 1px solid #334155;
        border-radius: 8px;
        gridline-color: #334155;
        outline: none;
    }
    QHeaderView::section {
        background-color: #0f172a;
        color: #f8fafc;
        font-weight: bold;
        padding: 8px;
        border: none;
        border-bottom: 2px solid #475569;
    }
    QTableWidget::item:selected {
        background-color: #0c4a6e;
        color: #bae6fd;
    }
    """
