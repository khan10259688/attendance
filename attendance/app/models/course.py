# app/models/course.py
from datetime import date
from app.utils.database import db


class Course(db.Model):
    __tablename__ = 'courses'

    course_id = db.Column(db.String(10), primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.String(20), db.ForeignKey('teachers.teacher_id'), nullable=False)  # 新增非空约束
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    # 关系定义
    teacher = db.relationship('Teacher', back_populates='courses')
    students = db.relationship('Student', back_populates='course')
    attendance_records = db.relationship('Attendance', back_populates='course')