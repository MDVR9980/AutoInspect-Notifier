import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QFileDialog, QStatusBar, QTabWidget, QGroupBox, QComboBox,
                             QLineEdit, QLabel, QMessageBox)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QIcon

from ui.styles import get_light_theme, get_dark_theme
from utils.excel_importer import import_customers_from_excel
from core.db_manager import DatabaseManager
from settings import APP_ICON_PATH, DB_FILE_PATH


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("سیستم حرفه‌ای یادآوری معاینه فنی - AutoInspect Notifier")
        self.resize(900, 650)
        self.setWindowIcon(QIcon(str(APP_ICON_PATH)))
        self.settings = QSettings("MyCompany", "AutoInspectNotifier")
        
        # اتصال به دیتابیس
        self.db = DatabaseManager(DB_FILE_PATH)
        self.db.connect()

        self._init_ui()
        self.load_theme()
        self.load_data()

    def _init_ui(self):
        # تنظیم راست‌چین بودن کل پنجره
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # تب‌ها
        self.tabs = QTabWidget()
        self.tab_dashboard = QWidget()
        self.tab_customers = QWidget()

        self.tabs.addTab(self.tab_dashboard, "داشبورد و عملیات")
        self.tabs.addTab(self.tab_customers, "لیست مشتریان")
        
        main_layout.addWidget(self.tabs)

        self._init_dashboard_tab()
        self._init_customers_tab()

        # نوار وضعیت
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("برنامه آماده است.")

    def _init_dashboard_tab(self):
        layout = QVBoxLayout(self.tab_dashboard)
        layout.setSpacing(15)

        # 1. تنظیم تاریخ مراجعه (شمسی)
        group_date = QGroupBox("تنظیم تاریخ مراجعه (شمسی)")
        layout_date = QHBoxLayout()
        
        self.combo_day = QComboBox()
        self.combo_day.addItems([str(i) for i in range(1, 32)])
        self.combo_month = QComboBox()
        self.combo_month.addItems(["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"])
        self.combo_year = QComboBox()
        self.combo_year.addItems([str(i) for i in range(1402, 1415)])
        
        layout_date.addWidget(QLabel("روز:"))
        layout_date.addWidget(self.combo_day)
        layout_date.addWidget(QLabel("ماه:"))
        layout_date.addWidget(self.combo_month)
        layout_date.addWidget(QLabel("سال:"))
        layout_date.addWidget(self.combo_year)
        layout_date.addStretch()
        
        group_date.setLayout(layout_date)
        layout.addWidget(group_date)

        # 2. ثبت دستی مراجعه
        group_manual = QGroupBox("ثبت دستی مراجعه")
        layout_manual = QHBoxLayout()
        
        self.input_plate = QLineEdit()
        self.input_plate.setPlaceholderText("مثال: 12 ب 345 ایران 67")
        self.input_plate.setToolTip("شماره پلاک خودرو را در این قسمت وارد کنید")
        
        self.input_phone = QLineEdit()
        self.input_phone.setPlaceholderText("مثال: 09123456789")
        self.input_phone.setToolTip("شماره موبایل مشتری را در این قسمت وارد کنید")
        
        self.btn_submit_manual = QPushButton("ثبت اطلاعات")
        self.btn_submit_manual.setObjectName("btn_submit") # اعمال شناسه برای استایل سبز رنگ
        self.btn_submit_manual.setToolTip("ذخیره اطلاعات پلاک و شماره موبایل در سیستم")
        
        layout_manual.addWidget(self.input_plate)
        layout_manual.addWidget(self.input_phone)
        layout_manual.addWidget(self.btn_submit_manual)
        
        group_manual.setLayout(layout_manual)
        layout.addWidget(group_manual)

        # 3. عملیات گروهی و پیامک
        group_batch = QGroupBox("عملیات گروهی و پیامک")
        layout_batch = QHBoxLayout()
        
        self.btn_import_excel = QPushButton("📁 بارگذاری از اکسل")
        self.btn_import_excel.setToolTip("وارد کردن اطلاعات مشتریان به صورت گروهی از فایل اکسل")
        
        self.btn_send_sms = QPushButton("🚀 ارسال/زمان‌بندی پیامک‌ها")
        self.btn_send_sms.setToolTip("شروع بررسی و ارسال پیامک برای مشتریانی که موعدشان فرا رسیده است")
        
        layout_batch.addWidget(self.btn_import_excel)
        layout_batch.addWidget(self.btn_send_sms)
        
        group_batch.setLayout(layout_batch)
        layout.addWidget(group_batch)

        # 4. مدیریت دیتابیس و تنظیمات
        group_db = QGroupBox("مدیریت دیتابیس و سیستم")
        layout_db = QHBoxLayout()
        
        self.btn_backup = QPushButton("💾 تهیه نسخه پشتیبان")
        self.btn_backup.setToolTip("یک کپی از اطلاعات فعلی در قالب فایل ذخیره می‌کند")
        
        self.btn_restore = QPushButton("📂 بازیابی اطلاعات")
        self.btn_restore.setToolTip("بازگردانی اطلاعات از روی فایل پشتیبان تهیه شده در گذشته")
        
        self.btn_theme = QPushButton("🌙/☀️ تغییر تم")
        self.btn_theme.setToolTip("تغییر ظاهر برنامه بین حالت روز و شب")
        
        layout_db.addWidget(self.btn_backup)
        layout_db.addWidget(self.btn_restore)
        layout_db.addWidget(self.btn_theme)
        
        group_db.setLayout(layout_db)
        layout.addWidget(group_db)
        
        layout.addStretch()

        # اتصال دکمه‌ها
        self.btn_theme.clicked.connect(self.toggle_theme)
        self.btn_import_excel.clicked.connect(self.import_excel_data)

    def _init_customers_tab(self):
        layout = QVBoxLayout(self.tab_customers)

        # دکمه‌های بالای لیست
        top_layout = QHBoxLayout()
        
        self.btn_delete_all = QPushButton("🗑️ حذف کل لیست")
        self.btn_delete_all.setObjectName("btn_delete_all") # اعمال شناسه برای استایل قرمز رنگ
        self.btn_delete_all.setToolTip("حذف تمامی اطلاعات مشتریان از سیستم (غیرقابل بازگشت)")
        
        top_layout.addWidget(self.btn_delete_all)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        # جدول مشتریان
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ردیف", "پلاک خودرو", "شماره تماس", "تاریخ انقضا", "وضعیت پیامک"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)

    def load_data(self):
        try:
            customers = self.db.get_all_customers()
            self.table.setRowCount(len(customers))
            for row_idx, row_data in enumerate(customers):
                # فرض بر این است که خروجی دیتابیس شامل: id, plate, phone, expire_date, sms_status است
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
                self.table.setItem(row_idx, 1, QTableWidgetItem(str(row_data[1])))
                self.table.setItem(row_idx, 2, QTableWidgetItem(str(row_data[2])))
                self.table.setItem(row_idx, 3, QTableWidgetItem(str(row_data[3])))
                self.table.setItem(row_idx, 4, QTableWidgetItem(str(row_data[4])))
            
            self.status_bar.showMessage(f"اطلاعات بارگذاری شد: {len(customers)} رکورد")
        except Exception as e:
            self.status_bar.showMessage(f"خطا در بارگذاری اطلاعات: {e}")

    def import_excel_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "انتخاب فایل اکسل", "", "Excel Files (*.xlsx *.xls)")
        if file_path:
            # در اینجا منطق اکسل قرار می‌گیرد (فعلاً پیام موفقیت می‌دهیم)
            self.status_bar.showMessage(f"در حال وارد کردن اطلاعات از {file_path} ...")
            # import_customers_from_excel(file_path, self.db) # اگر تابع شما دیتابیس را می‌گیرد
            self.load_data()

    def toggle_theme(self):
        current_theme = self.settings.value("theme", "light")
        new_theme = "dark" if current_theme == "light" else "light"
        self.apply_theme(new_theme)

    def apply_theme(self, theme_name):
        if theme_name == "dark":
            self.setStyleSheet(get_dark_theme())
        else:
            self.setStyleSheet(get_light_theme())
        self.settings.setValue("theme", theme_name)

    def load_theme(self):
        theme = self.settings.value("theme", "light")
        self.apply_theme(theme)
