# app/utils/database.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
import logging

# 配置日志
logger = logging.getLogger('SQLAlchemy')
db = SQLAlchemy()


@event.listens_for(Engine, "connect")
def set_timezone(dbapi_connection, connection_record):
    """数据库连接时区设置"""
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("SET time_zone='+08:00';")  # 设置为东八区
        cursor.close()
        logger.debug("成功设置数据库时区为 +08:00")
    except Exception as e:
        logger.error("时区设置失败: %s", str(e))
        raise


class DatabaseManager:
    @staticmethod
    def init_app(app):
        """数据库初始化方法"""
        # 确保配置统一（不覆盖应用配置）
        app.config.setdefault('SQLALCHEMY_ENGINE_OPTIONS', {
            'pool_size': 10,
            'pool_recycle': 3600,
            'pool_pre_ping': True,
            'max_overflow': 20,
            'pool_use_lifo': True  # 启用连接池LIFO模式
        })

        # 初始化SQLAlchemy
        db.init_app(app)

        # 验证连接池配置
        engine_options = app.config['SQLALCHEMY_ENGINE_OPTIONS']
        logger.info("数据库连接池配置: %s", engine_options)

        # 生产环境建议添加健康检查
        if app.env == 'production':
            @event.listens_for(Engine, "checkout")
            def ping_connection(dbapi_connection, connection_record, connection_proxy):
                cursor = dbapi_connection.cursor()
                try:
                    cursor.execute("SELECT 1")
                except:
                    raise Exception("数据库连接健康检查失败")
                finally:
                    cursor.close()