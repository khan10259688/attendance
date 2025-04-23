# app/models/user.py
from datetime import datetime
from app.utils.database import db

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.String(20), primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.Enum('student', 'admin', name='user_role'), nullable=False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    # 双向关系（可选）
    teacher = db.relationship('Teacher', back_populates='user', uselist=False)
    student = db.relationship('Student', back_populates='user', uselist=False)