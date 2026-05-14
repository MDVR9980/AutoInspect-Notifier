"""
پنجره اصلی برنامه AutoInspect Notifier
"""

import sys
import os
from datetime import datetime
import jdatetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QTableWidget, QTableWidgetItem, QLabel, QLineEdit,
    QMessageBox, QFileDialog, QGroupBox, QFormLayout, QHeaderView,
    QStatusBar, QToolBar, QDialog, QDialogButtonBox, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QAction

from core.db_manager import DatabaseManager
from core.sms_api import SMSManager
from core.backup_manager import BackupManager
from utils.excel_importer import ExcelImporter
from tasks.auto_task import AutoTaskManager
from ui.styles import Styles
import settings


class MainWindow(QMainWindow):
    """پنجره اصلی برنامه"""
    
    def __init__(self, db_manager, scheduler):
        super().__init__()
        
        # مقداردهی اولیه
        self.db_manager = db_manager
        self.sms_manager = scheduler
        self.backup_manager = BackupManager(
            str(settings.DATABASE_PATH),
            str(settings.BACKUP_DIR)
        )
        self.excel_importer = ExcelImporter()
        self.auto_task_manager = AutoTaskManager(self.db_manager, self.sms_manager)
        
        # مدیریت استایل
        self.styles = Styles(theme='light')
        
        # راه‌اندازی UI
        self.init_ui()
        
        # شروع وظایف خودکار
        self.auto_task_manager.start()
        
        # بارگذاری داده‌ها
        self.load_subscribers()
    
    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        self.setWindowTitle("AutoInspect Notifier - سیستم یادآوری معاینه فنی")
        self.setGeometry(100, 100, 1200, 700)
        
        # ویجت مرکزی
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # لی‌اوت اصلی
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # ایجاد نوار ابزار
        self.create_toolbar()
        
        # ایجاد تب‌ها
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # تب داشبورد
        self.dashboard_tab = self.create_dashboard_tab()
        self.tabs.addTab(self.dashboard_tab, "📊 داشبورد")
        
        # تب افزودن مشترک
        self.add_subscriber_tab = self.create_add_subscriber_tab()
        self.tabs.addTab(self.add_subscriber_tab, "➕ افزودن مشترک")
        
        # تب ورود اکسل
        self.excel_import_tab = self.create_excel_import_tab()
        self.tabs.addTab(self.excel_import_tab, "📁 ورود از اکسل")
        
        # نوار وضعیت
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("آماده")
        
        # اعمال استایل
        self.apply_styles()
    
    def create_toolbar(self):
        """ایجاد نوار ابزار"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # دکمه بروزرسانی
        refresh_action = QAction("🔄 بروزرسانی", self)
        refresh_action.triggered.connect(self.load_subscribers)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        # دکمه بکاپ
        backup_action = QAction("💾 بکاپ", self)
        backup_action.triggered.connect(self.create_backup)
        toolbar.addAction(backup_action)
        
        # دکمه بازیابی
        restore_action = QAction("♻️ بازیابی", self)
        restore_action.triggered.connect(self.restore_backup)
        toolbar.addAction(restore_action)
        
        toolbar.addSeparator()
        
        # دکمه تغییر تم
        theme_action = QAction("🌓 تغییر تم", self)
        theme_action.triggered.connect(self.toggle_theme)
        toolbar.addAction(theme_action)
    
    def create_dashboard_tab(self):
        """ایجاد تب داشبورد"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # بخش جستجو
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 جستجو:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("شماره موبایل یا پلاک...")
        self.search_input.textChanged.connect(self.search_subscribers)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        
        layout.addLayout(search_layout)
        
        # جدول مشترکین
        self.subscribers_table = QTableWidget()
        self.subscribers_table.setColumnCount(7)
        self.subscribers_table.setHorizontalHeaderLabels([
            "شناسه",
            "شماره موبایل",
            "پلاک",
            "تاریخ مراجعه",
            "تاریخ انقضا",
            "وضعیت پیامک",
            "تاریخ ایجاد"
        ])
        
        # تنظیمات جدول
        header = self.subscribers_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.subscribers_table.setAlternatingRowColors(True)
        self.subscribers_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        
        layout.addWidget(self.subscribers_table)
        
        # دکمه‌های عملیات
        buttons_layout = QHBoxLayout()
        
        self.delete_button = QPushButton("🗑 حذف")
        self.delete_button.clicked.connect(self.delete_selected_subscriber)
        
        self.send_sms_button = QPushButton("📨 ارسال پیامک")
        self.send_sms_button.clicked.connect(self.send_single_sms)
        
        self.clear_all_button = QPushButton("⚠ حذف همه")
        self.clear_all_button.clicked.connect(self.clear_all_subscribers)
        
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.send_sms_button)
        buttons_layout.addWidget(self.clear_all_button)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        return widget
    
    def create_add_subscriber_tab(self):
        """تب افزودن مشترک"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        group_box = QGroupBox("ثبت مشترک جدید")
        form_layout = QFormLayout()
        
        # شماره موبایل
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("09123456789")
        
        # پلاک
        self.plate_input = QLineEdit()
        self.plate_input.setPlaceholderText("12الف34567")
        
        # تاریخ مراجعه
        self.visit_date_input = QLineEdit()
        self.visit_date_input.setPlaceholderText("1405/02/24")
        
        form_layout.addRow("شماره موبایل:", self.phone_input)
        form_layout.addRow("پلاک:", self.plate_input)
        form_layout.addRow("تاریخ مراجعه:", self.visit_date_input)
        
        # دکمه ثبت
        self.add_button = QPushButton("✅ ثبت مشترک")
        self.add_button.clicked.connect(self.add_subscriber)
        
        form_layout.addRow(self.add_button)
        
        group_box.setLayout(form_layout)
        
        layout.addWidget(group_box)
        layout.addStretch()
        
        return widget
    
    def create_excel_import_tab(self):
        """تب ورود اکسل"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        group_box = QGroupBox("ورود اطلاعات از فایل اکسل")
        form_layout = QFormLayout()
        
        # مسیر فایل
        self.excel_path_input = QLineEdit()
        self.excel_path_input.setReadOnly(True)
        
        browse_button = QPushButton("📂 انتخاب فایل")
        browse_button.clicked.connect(self.select_excel_file)
        
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.excel_path_input)
        file_layout.addWidget(browse_button)
        
        # تاریخ مراجعه
        self.excel_visit_date_input = QLineEdit()
        self.excel_visit_date_input.setPlaceholderText("1405/02/24")
        
        # دکمه ورود
        self.import_button = QPushButton("⬆ ورود اطلاعات")
        self.import_button.clicked.connect(self.import_excel_data)
        
        form_layout.addRow("فایل اکسل:", file_layout)
        form_layout.addRow("تاریخ مراجعه:", self.excel_visit_date_input)
        form_layout.addRow(self.import_button)
        
        group_box.setLayout(form_layout)
        
        layout.addWidget(group_box)
        layout.addStretch()
        
        return widget
    
    def load_subscribers(self):
        """بارگذاری مشترکین"""
        subscribers = self.db_manager.get_all_subscribers()
        
        self.subscribers_table.setRowCount(len(subscribers))
        
        for row, subscriber in enumerate(subscribers):
            for col, value in enumerate(subscriber):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.subscribers_table.setItem(row, col, item)
        
        self.status_bar.showMessage(f"{len(subscribers)} مشترک بارگذاری شد")
    
    def add_subscriber(self):
        """افزودن مشترک"""
        phone = self.phone_input.text().strip()
        plate = self.plate_input.text().strip()
        visit_date = self.visit_date_input.text().strip()
        
        if not phone or not plate or not visit_date:
            QMessageBox.warning(self, "خطا", "همه فیلدها الزامی هستند")
            return
        
        try:
            self.db_manager.add_subscriber(phone, plate, visit_date)
            
            QMessageBox.information(
                self,
                "موفق",
                "مشترک با موفقیت ثبت شد"
            )
            
            self.phone_input.clear()
            self.plate_input.clear()
            self.visit_date_input.clear()
            
            self.load_subscribers()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "خطا",
                f"خطا در ثبت مشترک:\n{str(e)}"
            )
    
    def search_subscribers(self):
        """جستجوی مشترکین"""
        search_text = self.search_input.text().strip()
        
        if search_text:
            subscribers = self.db_manager.search_subscribers(search_text)
        else:
            subscribers = self.db_manager.get_all_subscribers()
        
        self.subscribers_table.setRowCount(len(subscribers))
        
        for row, subscriber in enumerate(subscribers):
            for col, value in enumerate(subscriber):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.subscribers_table.setItem(row, col, item)
    
    def delete_selected_subscriber(self):
        """حذف مشترک انتخاب شده"""
        selected = self.subscribers_table.currentRow()
        
        if selected < 0:
            QMessageBox.warning(self, "هشدار", "یک ردیف انتخاب کنید")
            return
        
        subscriber_id = self.subscribers_table.item(selected, 0).text()
        
        reply = QMessageBox.question(
            self,
            "تأیید حذف",
            "آیا مطمئن هستید؟",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db_manager.delete_subscriber(subscriber_id)
            self.load_subscribers()
            
            QMessageBox.information(
                self,
                "موفق",
                "مشترک حذف شد"
            )
        
    def send_single_sms(self):
        """ارسال پیامک به مشترک انتخاب شده"""
        selected = self.subscribers_table.currentRow()
        
        if selected < 0:
            QMessageBox.warning(self, "هشدار", "یک ردیف انتخاب کنید")
            return
        
        subscriber_id = self.subscribers_table.item(selected, 0).text()
        phone = self.subscribers_table.item(selected, 1).text()
        plate = self.subscribers_table.item(selected, 2).text()
        
        try:
            message = settings.SMS_TEMPLATE.format(plate=plate)
            
            result = self.sms_manager.send_sms(phone, message)
            
            if result:
                self.db_manager.update_sms_status(subscriber_id, 'sent')
                
                QMessageBox.information(
                    self,
                    "موفق",
                    "پیامک با موفقیت ارسال شد"
                )
                
                self.load_subscribers()
            else:
                QMessageBox.warning(
                    self,
                    "خطا",
                    "خطا در ارسال پیامک"
                )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "خطا",
                f"خطا در ارسال پیامک:\n{str(e)}"
            )
    
    def clear_all_subscribers(self):
        """حذف همه مشترکین"""
        reply = QMessageBox.question(
            self,
            "تأیید حذف",
            "⚠ آیا از حذف همه مشترکین مطمئن هستید؟\nاین عملیات غیرقابل بازگشت است!",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db_manager.clear_all_subscribers()
            self.load_subscribers()
            
            QMessageBox.information(
                self,
                "موفق",
                "همه مشترکین حذف شدند"
            )
    
    def select_excel_file(self):
        """انتخاب فایل اکسل"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "انتخاب فایل اکسل",
            "",
            "Excel Files (*.xlsx *.xls)"
        )
        
        if file_path:
            self.excel_path_input.setText(file_path)
    
    def import_excel_data(self):
        """ورود داده‌ها از اکسل"""
        file_path = self.excel_path_input.text().strip()
        visit_date = self.excel_visit_date_input.text().strip()
        
        if not file_path:
            QMessageBox.warning(self, "خطا", "فایل اکسل را انتخاب کنید")
            return
        
        if not visit_date:
            QMessageBox.warning(self, "خطا", "تاریخ مراجعه را وارد کنید")
            return
        
        try:
            data = self.excel_importer.read_excel(file_path)
            
            success_count = 0
            error_count = 0
            
            for row in data:
                phone = row.get('phone', '').strip()
                plate = row.get('plate', '').strip()
                
                if phone and plate:
                    try:
                        self.db_manager.add_subscriber(phone, plate, visit_date)
                        success_count += 1
                    except:
                        error_count += 1
            
            QMessageBox.information(
                self,
                "نتیجه ورود",
                f"✅ موفق: {success_count}\n❌ خطا: {error_count}"
            )
            
            self.excel_path_input.clear()
            self.excel_visit_date_input.clear()
            
            self.load_subscribers()
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "خطا",
                f"خطا در خواندن فایل اکسل:\n{str(e)}"
            )
    
    def create_backup(self):
        """ایجاد بکاپ"""
        try:
            backup_path = self.backup_manager.create_backup()
            
            QMessageBox.information(
                self, "موفق",
                f"بکاپ ایجاد شد:\n{backup_path}"
            )
            
            self.status_bar.showMessage("بکاپ با موفقیت ایجاد شد")
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "خطا",
                f"خطا در ایجاد بکاپ:\n{str(e)}"
            )
    
    def restore_backup(self):
        """بازیابی بکاپ"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "انتخاب فایل بکاپ",
            "",
            "Database Files (*.db *.sqlite)"
        )
        
        if not file_path:
            return
        
        reply = QMessageBox.question(
            self,
            "تأیید بازیابی",
            "آیا از بازیابی بکاپ مطمئن هستید؟\nاطلاعات فعلی جایگزین خواهند شد.",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.backup_manager.restore_backup(file_path)
                
                QMessageBox.information(
                    self,
                    "موفق",
                    "بکاپ با موفقیت بازیابی شد"
                )
                
                self.load_subscribers()
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "خطا",
                    f"خطا در بازیابی بکاپ:\n{str(e)}"
                )
    
    def toggle_theme(self):
        """تغییر تم"""
        self.styles.switch_theme()
        self.apply_styles()
        
        current_theme = self.styles.current_theme
        
        if current_theme == 'dark':
            self.status_bar.showMessage("تم تیره فعال شد")
        else:
            self.status_bar.showMessage("تم روشن فعال شد")
    
    def apply_styles(self):
        """اعمال استایل‌ها"""
        self.setStyleSheet(self.styles.get_main_window_style())
        
        # دکمه‌ها
        buttons = self.findChildren(QPushButton)
        for button in buttons:
            button.setStyleSheet(self.styles.get_button_style())
        
        # ورودی‌ها
        inputs = self.findChildren(QLineEdit)
        for input_widget in inputs:
            input_widget.setStyleSheet(self.styles.get_input_style())
        
        # جدول‌ها
        tables = self.findChildren(QTableWidget)
        for table in tables:
            table.setStyleSheet(self.styles.get_table_style())
        
        # گروه‌باکس‌ها
        groupboxes = self.findChildren(QGroupBox)
        for groupbox in groupboxes:
            groupbox.setStyleSheet(self.styles.get_groupbox_style())
    
    def closeEvent(self, event):
        """رویداد بستن برنامه"""
        try:
            self.auto_task_manager.stop()
        except:
            pass
        
        event.accept()


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

