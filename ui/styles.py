"""
مدیریت استایل‌ها و تم‌های رابط کاربری
"""

class Styles:
    """کلاس مدیریت استایل‌های برنامه"""
    
    # تم روشن
    LIGHT_THEME = {
        'background': '#f5f5f5',
        'surface': '#ffffff',
        'primary': '#2196F3',
        'primary_dark': '#1976D2',
        'primary_light': '#BBDEFB',
        'secondary': '#4CAF50',
        'secondary_dark': '#388E3C',
        'error': '#f44336',
        'warning': '#ff9800',
        'success': '#4CAF50',
        'text_primary': '#212121',
        'text_secondary': '#757575',
        'border': '#e0e0e0',
        'hover': '#f0f0f0',
        'disabled': '#bdbdbd'
    }
    
    # تم تیره
    DARK_THEME = {
        'background': '#1a1a1a',
        'surface': '#2d2d2d',
        'primary': '#42A5F5',
        'primary_dark': '#1E88E5',
        'primary_light': '#64B5F6',
        'secondary': '#66BB6A',
        'secondary_dark': '#43A047',
        'error': '#ef5350',
        'warning': '#ffa726',
        'success': '#66BB6A',
        'text_primary': '#ffffff',
        'text_secondary': '#b0b0b0',
        'border': '#404040',
        'hover': '#3a3a3a',
        'disabled': '#555555'
    }
    
    def __init__(self, theme='light'):
        """
        مقداردهی اولیه
        
        Args:
            theme: نوع تم ('light' یا 'dark')
        """
        self.current_theme = theme
        self.colors = self.LIGHT_THEME if theme == 'light' else self.DARK_THEME
    
    def switch_theme(self):
        """تغییر تم بین روشن و تیره"""
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.colors = self.LIGHT_THEME if self.current_theme == 'light' else self.DARK_THEME
        return self.current_theme
    
    def get_main_window_style(self):
        """استایل پنجره اصلی"""
        return f"""
            QMainWindow {{
                background-color: {self.colors['background']};
            }}
            QWidget {{
                background-color: {self.colors['background']};
                color: {self.colors['text_primary']};
                font-family: 'Segoe UI', Tahoma, sans-serif;
                font-size: 10pt;
            }}
            QTabWidget::pane {{
                border: 1px solid {self.colors['border']};
                background-color: {self.colors['surface']};
                border-radius: 4px;
            }}
            QTabBar::tab {{
                background-color: {self.colors['surface']};
                color: {self.colors['text_primary']};
                padding: 10px 20px;
                margin: 2px;
                border: 1px solid {self.colors['border']};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {self.colors['primary']};
                color: white;
            }}
            QTabBar::tab:hover {{
                background-color: {self.colors['hover']};
            }}
        """
    
    def get_button_style(self, button_type='primary'):
        """
        استایل دکمه‌ها
        
        Args:
            button_type: نوع دکمه ('primary', 'secondary', 'danger', 'success')
        """
        if button_type == 'primary':
            bg_color = self.colors['primary']
            hover_color = self.colors['primary_dark']
        elif button_type == 'secondary':
            bg_color = self.colors['secondary']
            hover_color = self.colors['secondary_dark']
        elif button_type == 'danger':
            bg_color = self.colors['error']
            hover_color = '#d32f2f'
        elif button_type == 'success':
            bg_color = self.colors['success']
            hover_color = self.colors['secondary_dark']
        else:
            bg_color = self.colors['primary']
            hover_color = self.colors['primary_dark']
        
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }}

            QPushButton:hover {{
                background-color: {hover_color};
            }}

            QPushButton:pressed {{
                padding-top: 11px;
                padding-bottom: 9px;
            }}

            QPushButton:disabled {{
                background-color: {self.colors['disabled']};
                color: {self.colors['text_secondary']};
            }}
        """
    
    def get_input_style(self):
        """استایل فیلدهای ورودی"""
        return f"""
            QLineEdit,
            QTextEdit,
            QDateEdit,
            QComboBox {{
                background-color: {self.colors['surface']};
                color: {self.colors['text_primary']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 8px;
            }}

            QLineEdit:focus,
            QTextEdit:focus,
            QDateEdit:focus,
            QComboBox:focus {{
                border: 2px solid {self.colors['primary']};
            }}
        """
    
    def get_table_style(self):
        """استایل جدول"""
        return f"""
            QTableWidget {{
                background-color: {self.colors['surface']};
                alternate-background-color: {self.colors['hover']};
                gridline-color: {self.colors['border']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                selection-background-color: {self.colors['primary_light']};
            }}

            QHeaderView::section {{
                background-color: {self.colors['primary']};
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }}
        """
    
    def get_groupbox_style(self):
        """استایل GroupBox"""
        return f"""
            QGroupBox {{
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """
