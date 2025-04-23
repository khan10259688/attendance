# 统一导出路由蓝图
from .attendance import attendance_bp
from .auth import auth_bp
from .admin import admin_bp

__all__ = ['attendance_bp', 'auth_bp', 'admin_bp']