"""
Configuration settings for the AutoInspect Notifier application.

This module centralizes all the static configuration variables, such as
database paths, backup directories, theme file locations, and API credentials.
Centralizing these settings makes the application easier to manage and configure.
"""

import os

# Path Definitions
# The os.path.join is used to create platform-independent paths (works on Windows, macOS, Linux).

# Base directory of the project.
# os.path.dirname(__file__) gets the directory of the current file (core).
# os.path.abspath() gets the absolute path.
# os.path.join(..., '..') goes one level up to the project root.
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Path to the main SQLite database file.
DB_PATH = os.path.join(BASE_DIR, 'data', 'database.db')

# Directory to store database backups.
BACKUP_DIR = os.path.join(BASE_DIR, 'data', 'backups')

# Path to the light theme stylesheet.
LIGHT_THEME_PATH = os.path.join(BASE_DIR, 'ui', 'themes', 'light.qss')

# Path to the dark theme stylesheet.
DARK_THEME_PATH = os.path.join(BASE_DIR, 'ui', 'themes', 'dark.qss')


# SMS API Configuration
# Credentials and endpoint for the Ghasdak SMS service.
# NOTE: It's recommended to load sensitive data like API keys from environment variables
# in a real production environment for better security.

# The URL of the SMS provider's API endpoint.
SMS_API_URL = "http://api.ghasdak.com/v1/sms/send/simple"

# Your personal API key provided by Ghasdak.
SMS_API_KEY = "a5842695aa0151c0c3ae0c8a80b0bfd04d53f9319568940e487221abcd11d11aV8S4vz9xUP6BSeuy" # !!! IMPORTANT: Replace with your actual key !!!