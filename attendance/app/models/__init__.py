# app/models/__init__.py
from .base import db
from .student import Student
from .course import Course
from .teacher import Teacher
from .attendance import Attendance
from .user import User  # 新增用户模型

__all__ = ['Student', 'Course', 'Teacher', 'Attendance', 'User']

def init_models(app):
    """初始化数据库模型"""
    with app.app_context():
        db.create_all()