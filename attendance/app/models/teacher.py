# app/models/teacher.py
from app.utils.database import db


class Teacher(db.Model):
    __tablename__ = 'teachers'

    teacher_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(20), db.ForeignKey('users.user_id'), unique=True)

    # 关系定义
    user = db.relationship('User', back_populates='teacher')
    courses = db.relationship('Course', back_populates='teacher')