# app/models/attendance.py
from datetime import date, time
from app.utils.database import db


class Attendance(db.Model):
    __tablename__ = 'attendance'

    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(20), db.ForeignKey('students.student_id'), nullable=False)
    course_id = db.Column(db.String(10), db.ForeignKey('courses.course_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    check_in = db.Column(db.Time)
    check_out = db.Column(db.Time)
    status = db.Column(
        db.Enum('Normal', 'Late', 'Early', 'Late + Early', 'Absent', 'Anomaly', name='attendance_status'),
        default = 'Absent'
    )

    # 关系定义
    student = db.relationship('Student', back_populates='attendance_records')
    course = db.relationship('Course', back_populates='attendance_records')