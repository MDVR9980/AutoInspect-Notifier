# tasks/__init__.py
"""
Tasks Package - مدیریت وظایف زمان‌بندی شده و خودکار
"""
from tasks.scheduler import TaskScheduler
from tasks.auto_task import AutoTaskManager

__all__ = ['TaskScheduler', 'AutoTaskManager']
