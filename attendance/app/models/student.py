# app/models/student.py
from datetime import date
from app.utils.database import db


class Student(db.Model):
    __tablename__ = 'students'

    student_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    course_id = db.Column(db.String(10), db.ForeignKey('courses.course_id'), nullable=False)  # 新增非空约束
    user_id = db.Column(db.String(20), db.ForeignKey('users.user_id'), unique=True)

    # 关系定义
    course = db.relationship('Course', back_populates='students')
    attendance_records = db.relationship('Attendance', back_populates='student')
    user = db.relationship('User', back_populates='student')