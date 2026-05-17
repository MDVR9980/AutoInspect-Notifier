# main_window.py
# Ultra Professional Version - Part 1 (Core UI)

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import *
import pyqtgraph as pg
from core.db_manager import DatabaseManager
from core.backup_manager import BackupManager
from utils.excel_importer import ExcelImporter
from tasks.auto_task import AutoTaskManager
from settings import SettingsManager, DATABASE_PATH, BACKUP_DIR
from ui.styles import Styles


# ------------------------------
# UI COMPONENTS
# ------------------------------

class SidebarButton(QPushButton):

    def __init__(self,text,icon=""):
        super().__init__()

        self.setText(text)

        if icon:
            self.setIcon(QIcon(icon))
            self.setIconSize(QSize(18,18))

        self.setCheckable(True)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setMinimumHeight(44)

        self.setObjectName("sidebarButton")

class Card(QFrame):

    def __init__(self):
        super().__init__()

        self.setObjectName("card")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16,16,16,16)
        layout.setSpacing(10)


class StatCard(QFrame):

    def __init__(self, title, icon):
        super().__init__()

        self.setObjectName("statCard")
        self.setMinimumHeight(110)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16,16,16,16)

        top = QHBoxLayout()

        icon_label = QLabel(icon)
        icon_label.setObjectName("statIcon")

        title_label = QLabel(title)
        title_label.setObjectName("statTitle")

        top.addWidget(icon_label)
        top.addWidget(title_label)
        top.addStretch()

        self.value = QLabel("0")
        self.value.setObjectName("statValue")

        layout.addLayout(top)
        layout.addStretch()
        layout.addWidget(self.value)

    def set_value(self, v):

        self.value.setText(str(v))


class SectionTitle(QLabel):

    def __init__(self, text):
        super().__init__(text)

        self.setObjectName("sectionTitle")
        self.setAlignment(Qt.AlignmentFlag.AlignRight)


# ------------------------------
# MAIN WINDOW
# ------------------------------

class MainWindow(QMainWindow):

    def __init__(self, db_manager, scheduler):
        super().__init__()

        self.db_manager = db_manager
        self.scheduler = scheduler

        self.sms_manager = getattr(scheduler, "sms_manager", None)

        self.backup_manager = BackupManager(DATABASE_PATH, BACKUP_DIR)
        self.excel_importer = ExcelImporter()
        self.auto_task_manager = AutoTaskManager(self.db_manager, self.sms_manager)
        self.settings_manager = SettingsManager()

        self.styles = Styles("light")

        self.init_window()

        # Apply styles
        self.setStyleSheet(
            self.styles.get_app_style() +
            self.styles.get_card_style() +
            self.styles.get_button_style() +
            self.styles.get_input_style() +
            self.styles.get_table_style() +
            self.styles.get_sidebar_style()
        )

        self.init_ui()

        try:
            self.auto_task_manager.start()
        except Exception:
            pass

    # ------------------------------
    # Window Settings
    # ------------------------------

    def init_window(self):

        self.setWindowTitle("AutoInspect Notifier")
        self.resize(1400, 850)

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        font = QFont("Vazirmatn", 10)
        self.setFont(font)

    # ------------------------------
    # Main UI Layout
    # ------------------------------

    def init_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0,0,0,0)

        self.sidebar = self.create_sidebar()
        root_layout.addWidget(self.sidebar)

        container = QVBoxLayout()

        self.topbar = self.create_topbar()
        container.addWidget(self.topbar)

        self.pages = QStackedWidget()
        container.addWidget(self.pages)

        wrapper = QWidget()
        wrapper.setLayout(container)

        root_layout.addWidget(wrapper,1)

        self.init_pages()

    # ------------------------------
    # Pages Init
    # ------------------------------
    def init_pages(self):

        # Create pages
        self.dashboard_page = QWidget()
        self.subscribers_page = QWidget()
        self.add_page = QWidget()
        self.excel_page = QWidget()
        self.backup_page = QWidget()
        self.settings_page = QWidget()
        self.about_page = QWidget()

        # Add to stacked widget
        self.pages.addWidget(self.dashboard_page)
        self.pages.addWidget(self.subscribers_page)
        self.pages.addWidget(self.add_page)
        self.pages.addWidget(self.excel_page)
        self.pages.addWidget(self.backup_page)
        self.pages.addWidget(self.settings_page)
        self.pages.addWidget(self.about_page)

        # Build page contents
        self.create_dashboard_page()
        self.create_subscribers_page()
        self.create_add_page()
        self.create_excel_page()
        self.create_backup_page()
        self.create_settings_page()
        self.create_about_page()

        # Initial data
        self.load_subscribers()
        self.refresh_dashboard()


    # ------------------------------
    # Sidebar
    # ------------------------------

    def create_sidebar(self):

        frame = QFrame()
        frame.setObjectName("sidebar")
        frame.setFixedWidth(250)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10,20,10,10)

        logo = QLabel("AutoInspect")
        logo.setObjectName("logoTitle")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(logo)
        layout.addSpacing(20)

        self.sidebar_buttons = []

        pages = [
            ("داشبورد","🏠"),
            ("مشترکین","👥"),
            ("افزودن مشترک","➕"),
            ("واردات اکسل","📥"),
            ("پشتیبان","💾"),
            ("تنظیمات","⚙️"),
            ("درباره","ℹ️")
        ]

        # pages = [
        #     ("داشبورد","icons/dashboard.svg"),
        #     ("مشترکین","icons/users.svg"),
        #     ("افزودن مشترک","icons/add.svg"),
        #     ("واردات اکسل","icons/excel.svg"),
        #     ("پشتیبان","icons/backup.svg"),
        #     ("تنظیمات","icons/settings.svg"),
        #     ("درباره","icons/info.svg")
        # ]
        
        for index,(title,icon) in enumerate(pages):

            btn = SidebarButton(title,icon)

            btn.clicked.connect(lambda _,x=index:self.set_page(x))

            layout.addWidget(btn)

            self.sidebar_buttons.append(btn)

        layout.addStretch()

        return frame

    # ------------------------------
    # Topbar
    # ------------------------------

    def create_topbar(self):

        bar = QFrame()
        bar.setObjectName("topbar")

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(15,10,15,10)

        self.page_title = QLabel("داشبورد")
        self.page_title.setObjectName("pageTitle")

        layout.addWidget(self.page_title)

        layout.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("جستجو شماره یا پلاک...")

        self.search_input.setMaximumWidth(280)

        layout.addWidget(self.search_input)

        refresh_btn = QPushButton("بروزرسانی")
        refresh_btn.clicked.connect(self.refresh_all)

        layout.addWidget(refresh_btn)

        return bar

    # ------------------------------
    # Navigation
    # ------------------------------

    def set_page(self,index):

        self.pages.setCurrentIndex(index)

        for b in self.sidebar_buttons:
            b.setChecked(False)

        self.sidebar_buttons[index].setChecked(True)

        titles = [
            "داشبورد",
            "مدیریت مشترکین",
            "افزودن مشترک",
            "واردات اکسل",
            "پشتیبان گیری",
            "تنظیمات",
            "درباره برنامه"
        ]

        self.page_title.setText(titles[index])

    # ------------------------------
    # Global Refresh
    # ------------------------------

    def refresh_all(self):

        try:

            if hasattr(self,"load_subscribers"):
                self.load_subscribers()

            if hasattr(self,"refresh_dashboard"):
                self.refresh_dashboard()

        except Exception:
            pass
# ------------------------------
# DASHBOARD PAGE
# ------------------------------

    def create_dashboard_page(self):

        layout = QVBoxLayout(self.dashboard_page)
        layout.setContentsMargins(20,20,20,20)
        layout.setSpacing(20)

        stats_layout = QGridLayout()

        self.card_total = StatCard("کل مشترکین","👥")
        self.card_today = StatCard("ارسال امروز","📤")
        self.card_month = StatCard("ارسال ماه","📅")
        self.card_error = StatCard("خطا","⚠️")

        stats_layout.addWidget(self.card_total,0,0)
        stats_layout.addWidget(self.card_today,0,1)
        stats_layout.addWidget(self.card_month,1,0)
        stats_layout.addWidget(self.card_error,1,1)

        layout.addLayout(stats_layout)

                # ---------------- Chart Card ----------------

        chart_card = Card()

        chart_layout = QVBoxLayout()

        chart_title = SectionTitle("آمار یادآوری‌ها")

        self.reminder_chart = pg.PlotWidget()
        self.reminder_chart.setBackground("transparent")

        self.reminder_chart.showGrid(x=True,y=True)

        chart_layout.addWidget(chart_title)
        chart_layout.addWidget(self.reminder_chart)

        chart_card.layout().addLayout(chart_layout)

        layout.addWidget(chart_card)

        info_card = Card()

        info_layout = info_card.layout()

        title = SectionTitle("وضعیت سیستم")

        self.dashboard_info = QLabel("سیستم آماده است")

        info_layout.addWidget(title)
        info_layout.addWidget(self.dashboard_info)

        layout.addWidget(info_card)
        layout.addStretch()

    def refresh_dashboard(self):

        try:

            subscribers = self.db_manager.get_subscribers()

            total = len(subscribers)

            reminders = [s.get("reminder_count",0) for s in subscribers]

        except Exception:

            total = 0
            reminders = []

        self.card_total.set_value(total)

        # draw chart
        if reminders:

            x = list(range(len(reminders)))

            self.reminder_chart.clear()

            self.reminder_chart.plot(
                x,
                reminders,
                pen=pg.mkPen(width=3,color="#3b82f6"),
                symbol="o"
            )




# ------------------------------
# SUBSCRIBERS PAGE
# ------------------------------

    def create_subscribers_page(self):

        layout = QVBoxLayout(self.subscribers_page)
        layout.setContentsMargins(20,20,20,20)

        title = SectionTitle("لیست مشترکین")

        layout.addWidget(title)

        self.subscribers_table = QTableWidget()

        self.subscribers_table.setColumnCount(7)

        self.subscribers_table.setHorizontalHeaderLabels([
            "شناسه",
            "شماره موبایل",
            "پلاک",
            "تاریخ معاینه",
            "تاریخ انقضا",
            "یادآوری آخر",
            "تعداد یادآوری"
        ])

        self.subscribers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.subscribers_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows
)

        self.subscribers_table.setAlternatingRowColors(True)

        # ---------- CRM Features ----------

        self.subscribers_table.setSortingEnabled(True)

        self.subscribers_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.subscribers_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        self.subscribers_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.subscribers_table.customContextMenuRequested.connect(
            self.subscribers_context_menu
        )

        layout.addWidget(self.subscribers_table)

        self.search_input.textChanged.connect(self.search_subscribers)

    # ------------------------------
    # Load Subscribers
    # ------------------------------

    def load_subscribers(self):

        try:

            subscribers = self.db_manager.get_subscribers()

        except Exception:

            subscribers = []

        self.populate_table(subscribers)

        self.statusBar().showMessage(f"{len(subscribers)} مشترک بارگذاری شد")

    def populate_table(self,subscribers):

        self.subscribers_table.setRowCount(0)

        for row_data in subscribers:

            row = self.subscribers_table.rowCount()

            self.subscribers_table.insertRow(row)

            values = [
                row_data.get("id"),
                row_data.get("phone"),
                row_data.get("plate"),
                row_data.get("visit_date"),
                row_data.get("expire_date"),
                row_data.get("last_reminder"),
                row_data.get("reminder_count")
            ]

            for col,value in enumerate(values):

                item = QTableWidgetItem(str(value))

                if col == 6 and value:

                    if int(value) >= 3:
                        item.setBackground(Qt.red)

                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.subscribers_table.setItem(row,col,item)

    # ------------------------------
    # Search
    # ------------------------------

    def search_subscribers(self):

        text = self.search_input.text().strip()

        if not text:

            self.load_subscribers()
            return

        try:

            subscribers = self.db_manager.search_subscribers(text)

        except Exception:

            subscribers = []

        self.populate_table(subscribers)



# ------------------------------
# ADD SUBSCRIBER PAGE
# ------------------------------

    def create_add_page(self):

        layout = QVBoxLayout(self.add_page)
        layout.setContentsMargins(30,30,30,30)

        card = Card()

        form = QFormLayout()

        self.phone_input = QLineEdit()
        self.plate_input = QLineEdit()

        self.day_combo = QComboBox()
        self.month_combo = QComboBox()
        self.year_combo = QComboBox()

        for i in range(1,32):
            self.day_combo.addItem(str(i))

        for i in range(1,13):
            self.month_combo.addItem(str(i))

        for i in range(1400,1420):
            self.year_combo.addItem(str(i))

        date_layout = QHBoxLayout()

        date_layout.addWidget(self.year_combo)
        date_layout.addWidget(self.month_combo)
        date_layout.addWidget(self.day_combo)

        form.addRow("شماره موبایل",self.phone_input)
        form.addRow("پلاک خودرو",self.plate_input)
        form.addRow("تاریخ معاینه",date_layout)

        add_button = QPushButton("ثبت مشترک")

        add_button.clicked.connect(self.add_subscriber)

        form.addRow(add_button)

        card.layout().addLayout(form)

        layout.addWidget(card)
        layout.addStretch()

    # ------------------------------
    # Add Subscriber
    # ------------------------------

    def add_subscriber(self):

        phone = self.phone_input.text().strip()
        plate = self.plate_input.text().strip()

        day = self.day_combo.currentText()
        month = self.month_combo.currentText()
        year = self.year_combo.currentText()

        visit_date = f"{year}-{month}-{day}"

        if not phone or not plate:

            QMessageBox.warning(self,"خطا","اطلاعات ناقص است")
            return

        try:

            ok = self.db_manager.add_subscriber(
                phone,
                plate,
                visit_date
            )

            if ok:

                QMessageBox.information(self,"موفق","مشترک ثبت شد")

                self.phone_input.clear()
                self.plate_input.clear()

                self.load_subscribers()

        except Exception as e:

            QMessageBox.critical(self,"خطا",str(e))
# ------------------------------
# EXCEL IMPORT PAGE
# ------------------------------

    def create_excel_page(self):

        layout = QVBoxLayout(self.excel_page)
        layout.setContentsMargins(30,30,30,30)

        card = Card()

        inner = QVBoxLayout()

        title = SectionTitle("واردات مشترکین از اکسل")

        self.excel_path_input = QLineEdit()
        self.excel_path_input.setPlaceholderText("مسیر فایل اکسل")

        choose_btn = QPushButton("انتخاب فایل")
        choose_btn.clicked.connect(self.choose_excel_file)

        import_btn = QPushButton("شروع واردات")
        import_btn.clicked.connect(self.import_excel)

        inner.addWidget(title)
        inner.addWidget(self.excel_path_input)
        inner.addWidget(choose_btn)
        inner.addWidget(import_btn)

        card.layout().addLayout(inner)

        layout.addWidget(card)
        layout.addStretch()

    def choose_excel_file(self):

        file_path,_ = QFileDialog.getOpenFileName(
            self,
            "انتخاب فایل اکسل",
            "",
            "Excel Files (*.xlsx *.xls)"
        )

        if file_path:

            self.excel_path_input.setText(file_path)

    def import_excel(self):

        path = self.excel_path_input.text().strip()

        if not path:

            QMessageBox.warning(self,"خطا","فایل انتخاب نشده")
            return

        try:

            count = self.excel_importer.import_file(path)

            QMessageBox.information(
                self,
                "واردات موفق",
                f"{count} مشترک اضافه شد"
            )

            self.load_subscribers()

        except Exception as e:

            QMessageBox.critical(self,"خطا",str(e))


# ------------------------------
# BACKUP PAGE
# ------------------------------

    def create_backup_page(self):

        layout = QVBoxLayout(self.backup_page)
        layout.setContentsMargins(30,30,30,30)

        card = Card()

        inner = QVBoxLayout()

        title = SectionTitle("پشتیبان گیری از دیتابیس")

        backup_btn = QPushButton("ایجاد بکاپ")
        backup_btn.clicked.connect(self.create_backup)

        restore_btn = QPushButton("بازگردانی بکاپ")
        restore_btn.clicked.connect(self.restore_backup)

        inner.addWidget(title)
        inner.addWidget(backup_btn)
        inner.addWidget(restore_btn)

        card.layout().addLayout(inner)

        layout.addWidget(card)
        layout.addStretch()

    def create_backup(self):

        try:

            path = self.backup_manager.create_backup()

            QMessageBox.information(
                self,
                "بکاپ ایجاد شد",
                f"فایل:\n{path}"
            )

        except Exception as e:

            QMessageBox.critical(self,"خطا",str(e))

    def restore_backup(self):

        file_path,_ = QFileDialog.getOpenFileName(
            self,
            "انتخاب بکاپ",
            "",
            "Database (*.db *.sqlite)"
        )

        if not file_path:
            return

        try:

            self.backup_manager.restore_backup(file_path)

            QMessageBox.information(
                self,
                "موفق",
                "دیتابیس بازیابی شد"
            )

            self.load_subscribers()

        except Exception as e:

            QMessageBox.critical(self,"خطا",str(e))


# ------------------------------
# SETTINGS PAGE
# ------------------------------

    def create_settings_page(self):

        layout = QVBoxLayout(self.settings_page)
        layout.setContentsMargins(30,30,30,30)

        card = Card()

        form = QFormLayout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light","Dark"])

        save_btn = QPushButton("ذخیره تنظیمات")
        save_btn.clicked.connect(self.save_settings)

        form.addRow("تم برنامه",self.theme_combo)
        form.addRow(save_btn)

        card.layout().addLayout(form)

        layout.addWidget(card)
        layout.addStretch()

    def save_settings(self):

        theme = self.theme_combo.currentText()

        try:

            self.settings_manager.set_theme(theme)

            QMessageBox.information(
                self,
                "ذخیره شد",
                "تنظیمات اعمال شد"
            )

        except Exception as e:

            QMessageBox.critical(self,"خطا",str(e))


# ------------------------------
# ABOUT PAGE
# ------------------------------

    def create_about_page(self):

        layout = QVBoxLayout(self.about_page)
        layout.setContentsMargins(40,40,40,40)

        title = QLabel("AutoInspect Notifier")
        title.setObjectName("aboutTitle")

        description = QLabel(
            "سیستم مدیریت و یادآوری معاینه فنی خودرو\n"
            "نسخه حرفه ای"
        )

        description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()
        layout.addWidget(title,alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description)
        layout.addStretch()



# ------------------------------
# DELETE SUBSCRIBER
# ------------------------------

    def delete_selected_subscriber(self):

        row = self.subscribers_table.currentRow()

        if row < 0:

            QMessageBox.warning(self,"خطا","ردیفی انتخاب نشده")
            return

        subscriber_id = self.subscribers_table.item(row,0).text()

        confirm = QMessageBox.question(
            self,
            "حذف",
            "آیا مطمئن هستید؟"
        )

        if confirm != QMessageBox.Yes:
            return

        try:

            ok = self.db_manager.delete_subscriber(subscriber_id)

            if ok:

                QMessageBox.information(self,"موفق","حذف شد")

                self.load_subscribers()

        except Exception as e:

            QMessageBox.critical(self,"خطا",str(e))

    def subscribers_context_menu(self, pos):

        menu = QMenu()

        delete_action = menu.addAction("حذف مشترک")

        action = menu.exec_(self.subscribers_table.mapToGlobal(pos))

        if action == delete_action:
            self.delete_selected_subscriber()