# config/default.py
import os
from datetime import time, timedelta

class Config:
    # JWT 配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET', 'dev_secret_key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_HEADER_TYPE = 'Bearer'  # 明确声明头类型


    # MySQL 连接参数（分项设置）
    MYSQL_USER = 'db_zoe'
    MYSQL_PASSWORD = 'Wk125216'
    # 建议使用mysql外网（阿里云RDS需要开通外网访问权限），因为内网需要ECS服务器和它在一个专网
    MYSQL_HOST = 'rm-wz959c8h2hv3ntym33o.mysql.rds.aliyuncs.com'
    MYSQL_PORT = 3306
    # db_ticket
    MYSQL_DB = 'db_attendance'
    MYSQL_CHARSET = 'utf8mb4'
    MYSQL_CONNECT_TIMEOUT = 10
    MYSQL_TIMEZONE = '+08:00'

    # SQLAlchemy 配置
    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@'
        f'{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?'
        f'charset={MYSQL_CHARSET}&'
        f'connect_timeout={MYSQL_CONNECT_TIMEOUT}'
    )
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'connect_args': {
            'connect_timeout': 10
        }
    }

    # OSS 配置（分项设置）
    OSS_ACCESS_KEY_ID = 'LTAI5t5iN36SaQdTvMmncvJG'
    OSS_ACCESS_KEY_SECRET = 'Bbw1lQ3cYYD6YCzQrA0tGST00X84C6'
    OSS_ENDPOINT = 'oss-cn-shenzhen.aliyuncs.com'
    OSS_BUCKET_NAME = 'booking-ticket-bucket'

    # 邮件配置（保持默认）
    SMTP_SERVER = 'smtp.qiye.aliyuncs.com'
    SMTP_PORT = 465
    EMAIL_USER = 'noreply@yourdomain.com'
    EMAIL_PASSWORD = 'email_password'  # 建议实际使用时配置环境变量

    # 课程时间配置
    COURSE_START_TIME = time(9, 0)  # 9:00 AM
    COURSE_END_TIME = time(23, 50)   # 5:00 PM
