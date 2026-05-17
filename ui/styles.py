"""
Ultra Professional UI Style System
مدیریت کامل تم و استایل رابط کاربری
"""

class Styles:

    # ---------- Light Theme ----------
    LIGHT_THEME = {
        "background": "#F5F7FA",
        "surface": "#FFFFFF",
        "primary": "#2979FF",
        "primary_hover": "#1E5DD8",
        "border": "#E5E7EB",
        "text_main": "#1F2937",
        "text_secondary": "#6B7280",
        "success": "#16A34A",
        "warning": "#F59E0B",
        "danger": "#EF4444"
    }

    # ---------- Dark Theme ----------
    DARK_THEME = {
        "background": "#0E0E0F",
        "surface": "#161618",
        "primary": "#4C8BFF",
        "primary_hover": "#3A74D9",
        "border": "#2A2A2D",
        "text_main": "#EDEDED",
        "text_secondary": "#A0A0A0",
        "success": "#22C55E",
        "warning": "#F59E0B",
        "danger": "#EF4444"
    }

    # ---------- Radius ----------
    RADIUS_BUTTON = 10
    RADIUS_CARD = 16
    RADIUS_INPUT = 8
    RADIUS_LOGO = 20

    # ---------- Spacing ----------
    SPACE_XS = 4
    SPACE_SM = 8
    SPACE_MD = 16
    SPACE_LG = 24
    SPACE_XL = 32

    def __init__(self, theme="light"):
        self.current_theme = theme
        self.colors = self.LIGHT_THEME if theme == "light" else self.DARK_THEME

    def switch_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.colors = self.LIGHT_THEME if self.current_theme == "light" else self.DARK_THEME
        return self.current_theme

    # ---------- Base Application ----------
    def get_app_style(self):
        return f"""
        QWidget {{
            background-color: {self.colors['background']};
            color: {self.colors['text_main']};
            font-family: Vazirmatn;
            font-size: 10pt;
        }}
        """

    # ---------- Cards ----------
    def get_card_style(self):
        return f"""
        QWidget#card {{
            background: {self.colors['surface']};
            border: 1px solid {self.colors['border']};
            border-radius: {self.RADIUS_CARD}px;
        }}
        """

    # ---------- Buttons ----------
    def get_button_style(self):
        return f"""
        QPushButton {{
            background-color: {self.colors['primary']};
            color: white;
            border: none;
            border-radius: {self.RADIUS_BUTTON}px;
            padding: 10px 18px;
            font-weight: 600;
        }}

        QPushButton:hover {{
            background-color: {self.colors['primary_hover']};
        }}

        QPushButton:pressed {{
            padding-top: 11px;
            padding-bottom: 9px;
        }}

        QPushButton:disabled {{
            background-color: {self.colors['border']};
            color: {self.colors['text_secondary']};
        }}
        """

    # ---------- Sidebar ----------
    def get_sidebar_style(self):
        return f"""
        #sidebarButton {{
            border: none;
            padding: 10px;
            text-align: right;
            border-radius: 8px;
        }}

        #sidebarButton:hover {{
            background: {self.colors['border']};
        }}

        #sidebarButton:checked {{
            background: {self.colors['primary']};
            color: white;
        }}
        """

    # ---------- Inputs ----------
    def get_input_style(self):
        return f"""
        QLineEdit,
        QTextEdit,
        QComboBox,
        QDateEdit {{
            background: {self.colors['surface']};
            border: 1px solid {self.colors['border']};
            border-radius: {self.RADIUS_INPUT}px;
            padding: 8px;
        }}

        QLineEdit:focus,
        QTextEdit:focus,
        QComboBox:focus,
        QDateEdit:focus {{
            border: 2px solid {self.colors['primary']};
        }}
        """

    # ---------- Tables ----------
    def get_table_style(self):
        return f"""
        QTableWidget {{
            background: {self.colors['surface']};
            border-radius: {self.RADIUS_CARD}px;
            border: 1px solid {self.colors['border']};
            gridline-color: {self.colors['border']};
            selection-background-color: {self.colors['primary']};
        }}

        QHeaderView::section {{
            background: {self.colors['background']};
            border: none;
            padding: 10px;
            font-weight: bold;
        }}
        """

    # ---------- Tabs ----------
    def get_tab_style(self):
        return f"""
        QTabWidget::pane {{
            border: none;
        }}

        QTabBar::tab {{
            background: transparent;
            padding: 10px 18px;
            margin-right: 4px;
            border-radius: {self.RADIUS_BUTTON}px;
        }}

        QTabBar::tab:selected {{
            background: {self.colors['primary']};
            color: white;
        }}

        QTabBar::tab:hover {{
            background: {self.colors['border']};
        }}
        """

    # ---------- Scrollbars ----------
    def get_scrollbar_style(self):
        return f"""
        QScrollBar:vertical {{
            background: transparent;
            width: 10px;
        }}

        QScrollBar::handle:vertical {{
            background: {self.colors['border']};
            border-radius: 5px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {self.colors['primary']};
        }}

        QScrollBar:horizontal {{
            background: transparent;
            height: 10px;
        }}

        QScrollBar::handle:horizontal {{
            background: {self.colors['border']};
            border-radius: 5px;
        }}
        """

    # ---------- Menu ----------
    def get_menu_style(self):
        return f"""
        QMenu {{
            background: {self.colors['surface']};
            border: 1px solid {self.colors['border']};
            padding: 5px;
        }}

        QMenu::item {{
            padding: 6px 20px;
            border-radius: 6px;
        }}

        QMenu::item:selected {{
            background: {self.colors['primary']};
            color: white;
        }}
        """

    # ---------- Checkbox ----------
    def get_checkbox_style(self):
        return f"""
        QCheckBox {{
            spacing: 6px;
        }}

        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {self.colors['border']};
            border-radius: 4px;
            background: {self.colors['surface']};
        }}

        QCheckBox::indicator:checked {{
            background: {self.colors['primary']};
            border: none;
        }}
        """

    # ---------- Tooltip ----------
    def get_tooltip_style(self):
        return f"""
        QToolTip {{
            background: {self.colors['surface']};
            border: 1px solid {self.colors['border']};
            padding: 6px;
            color: {self.colors['text_main']};
        }}
        """

    # ---------- Progress Bar ----------
    def get_progress_style(self):
        return f"""
        QProgressBar {{
            border: 1px solid {self.colors['border']};
            border-radius: {self.RADIUS_INPUT}px;
            text-align: center;
        }}

        QProgressBar::chunk {{
            background-color: {self.colors['primary']};
            border-radius: {self.RADIUS_INPUT}px;
        }}
        """

    # ---------- Dialog ----------
    def get_dialog_style(self):
        return f"""
        QDialog {{
            background: {self.colors['surface']};
            border-radius: {self.RADIUS_CARD}px;
        }}
        """
