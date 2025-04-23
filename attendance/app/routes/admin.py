# routes/admin.py
from datetime import datetime, timedelta  # 新增datetime模块导入
from ..models import Attendance, Student, Course
from ..utils import db
from flask import Blueprint, request, jsonify
import logging  # 新增日志模块导入
import pandas as pd
import os
from ..utils.oss import OSSManager
from sqlalchemy import and_, or_, not_, exists

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('AdminAPI')
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def _build_preflight_response():
    response = jsonify({"msg": "Preflight Accepted"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Max-Age", "86400")
    return response

@admin_bp.route('/attendance', methods=['GET', 'OPTIONS'])
def get_attendance_records():
    logger.info("------老师查考勤来了。。。")
    if request.method == 'OPTIONS':
        # 返回符合规范的预检响应
        return _build_preflight_response()
    try:
        # 获取查询参数
        logger.debug("请求参数: %s", request.args)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        student_id = request.args.get('student_id')

        student_name = request.args.get('student_name')
        status = request.args.get('status')

        # 构建基础查询
        query = db.session.query(
            Attendance.date,
            Attendance.check_in,
            Attendance.check_out,
            Attendance.status,
            Student.student_id,
            Student.name.label('student_name'),
            Course.course_name
        ).join(Student, Student.student_id == Attendance.student_id
               ).join(Course, Course.course_id == Attendance.course_id)

        # 添加新过滤条件
        if student_name:
            query = query.filter(Student.name.ilike(f"%{student_name}%"))  # 支持模糊查询
        if status:
            query = query.filter(Attendance.status == status)

        # 添加过滤条件
        if start_date and end_date:
            query = query.filter(Attendance.date.between(start_date, end_date))
        if student_id:
            query = query.filter(Attendance.student_id == student_id)

        # 执行分页查询
        pagination = query.paginate(page=page, per_page=per_page)

        return jsonify({
            'data': [{
                'date': record.date.isoformat(),
                'check_in': record.check_in.isoformat() if record.check_in else None,
                'check_out': record.check_out.isoformat() if record.check_out else None,
                'status': record.status,
                'student_id': record.student_id,
                'student_name': record.student_name,
                'course_name': record.course_name
            } for record in pagination.items],
            'pagination': {
                'total': pagination.total,
                'current_page': pagination.page,
                'per_page': pagination.per_page
            }
        }), 200

    except Exception as e:
        logger.error(f"获取考勤记录失败: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@admin_bp.route('/attendance/export', methods=['POST', 'OPTIONS'])
def export_attendance():
    if request.method == 'OPTIONS':
        return _build_preflight_response()
    try:
        # 参数校验
        params = request.get_json()
        logger.info(f"导出参数: {params}")

        # 构建查询（复用原有逻辑）
        query = build_attendance_query(params)
        records = query.all()

        if not records:
            return jsonify({"error": "No data to export"}), 400

        # 生成Excel
        filename = generate_excel(records)

        # 上传OSS并获取URL
        oss = OSSManager()
        if not oss.upload_file(filename):
            raise RuntimeError("OSS upload failed")

        download_url = oss.generate_presigned_url(filename)

        return jsonify({
            "code": 200,
            "msg": "success",
            "data": {
                "url": download_url
            }
        }), 200

    except Exception as e:
        logger.error(f"导出失败: {str(e)}")
        return handle_export_error(e)


# 公共错误处理
def handle_export_error(e):
    error_msg = str(e)
    if "No data" in error_msg:
        return jsonify({"error": "No data to export"}), 400
    return jsonify({"error": "Export failed"}), 500


# 构建查询（复用原有逻辑）
def build_attendance_query(params):
    # 构建基础查询
    query = db.session.query(
        Attendance.date,
        Attendance.check_in,
        Attendance.check_out,
        Attendance.status,
        Student.student_id,
        Student.name.label('student_name'),
        Course.course_name
    ).select_from(Attendance)  # 强制指定主表
    logger.info("------1。。。")
    # 精确指定 JOIN 条件
    query = query.join(
        Student,
        Attendance.student_id == Student.student_id
    ).join(
        Course,
        Attendance.course_id == Course.course_id
    )
    logger.info("------2。。。")
    # 直接复用 GET 接口的过滤逻辑
    if student_name := params.get('student_name'):
        query = query.filter(Student.name.ilike(f"%{student_name}%"))  # 姓名模糊匹配
    logger.info("------3。。。")
    if status := params.get('status'):
        query = query.filter(Attendance.status == status)  # 状态精确匹配

    start_date = params.get('start_date')  # 提前提取参数
    end_date = params.get('end_date')  # 并赋给变量
    if start_date and end_date:
        query = query.filter(Attendance.date.between(start_date, end_date))  # 日期范围

    if student_id := params.get('student_id'):
        query = query.filter(Attendance.student_id == student_id)  # 学号精确匹配
    return query


# 生成Excel文件
def generate_excel(records):
    df = pd.DataFrame([{
        '日期': record.date.strftime('%Y-%m-%d'),
        '学号': record.student_id,
        '姓名': record.student_name,
        '课程': record.course_name,
        '签到时间': record.check_in.strftime('%H:%M') if record.check_in else 'N/A',
        '签退时间': record.check_out.strftime('%H:%M') if record.check_out else 'N/A',
        '状态': record.status
    } for record in records])

    filename = f"attendance_{datetime.now().strftime('%Y%m%d%H%M')}.xlsx"
    df.to_excel(filename, index=False)
    return filename