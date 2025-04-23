from flask import Blueprint, request, jsonify
from datetime import datetime, time, timedelta, timezone
from ..models.attendance import Attendance
from ..models.student import Student
from ..models.course import Course
from ..utils.database import db
# from ..utils.notifier import send_notification
from config import Config

import logging
# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('AttendanceAPI')
attendance_bp = Blueprint('attendance', __name__, url_prefix='/api/attendance')

def _build_preflight_response():
    response = jsonify({"msg": "Preflight Accepted"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Max-Age", "86400")
    return response

@attendance_bp.route('/today', methods=['GET', 'OPTIONS'])
def get_today_attendance():
    logger.info("\n======== 收到查询请求 ========")
    logger.debug("请求参数: %s", request.args)
    if request.method == 'OPTIONS':
        # 返回符合规范的预检响应
        return _build_preflight_response()
    """获取当日考勤状态（东八区版本）"""
    # 创建东八区时区对象
    tz_shanghai = timezone(timedelta(hours=8))
    try:
        # 验证必要参数
        student_id = request.args.get('student_id')
        if not student_id:
            logger.error("缺少必要参数: student_id")
            return jsonify({
                "error": "Missing required parameter: student_id",
                "example_request": "GET /api/attendance/today?student_id=20250001"
            }), 400

        # 获取东八区当前日期时间
        now = datetime.now(tz_shanghai)
        today_date = now.date()
        current_time = now.time()

        # 查询当日记录（直接匹配东八区日期）
        record = Attendance.query.filter_by(
            student_id=student_id,
            date=today_date  # 假设date字段存储的是东八区日期
        ).first()

        # 构建响应数据
        response_data = {
            "system_time": now.isoformat(),  # 带时区的系统时间
            "course_schedule": {
                "start": Config.COURSE_START_TIME.strftime('%H:%M:%S'),
                "end": Config.COURSE_END_TIME.strftime('%H:%M:%S')
            },
            "attendance": {}
        }

        if record:
            # 直接使用数据库存储的东八区时间
            response_data['attendance'] = {
                "check_in": (
                    datetime.combine(today_date, record.check_in).astimezone(tz_shanghai)
                    if record.check_in
                    else None
                ),
                "check_out": (
                    datetime.combine(today_date, record.check_out).astimezone(tz_shanghai)
                    if record.check_out
                    else None
                ),
                "status": record.status
            }

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"获取考勤信息失败: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "system_time": datetime.now(tz_shanghai).isoformat()
        }), 500

@attendance_bp.route('/check-in', methods=['POST', 'OPTIONS'])  # 必须包含OPTIONS
def check_in():
    logger.info("\n======== 收到签到请求 ========")
    if request.method == 'OPTIONS':
        # 返回符合规范的预检响应
        return _build_preflight_response()
    try:
        # 获取东八区时间
        tz_shanghai = timezone(timedelta(hours=8))
        now = datetime.now(tz_shanghai)

        # 记录原始请求信息
        logger.debug("原始数据: %s", request.get_data(as_text=True))

        data = request.json
        if not data:
            logger.error("请求体为空")
            return jsonify({"error": "Request body cannot be empty"}), 400

        logger.debug("解析的JSON数据: %s", data)

        # 验证必要字段
        required_fields = ['student_id', 'course_id']
        missing = [field for field in required_fields if field not in data]
        if missing:
            logger.error("缺失字段: %s", missing)
            return jsonify({"error": "Required fields missing", "missing": missing}), 400

        student_id = data['student_id']
        course_id = data['course_id']
        logger.info("签到学生: %s | 课程: %s", student_id, course_id)

        # 检查学生和课程是否存在
        student = Student.query.get(student_id)
        course = Course.query.get(course_id)
        logger.debug("学生存在: %s | 课程存在: %s", bool(student), bool(course))
        if not student or not course:
            logger.error("数据不存在: 学生-%s 课程-%s", student_id, course_id)
            return jsonify({"error": "Student or course not found"}), 404

        # 获取课程时间范围
        today_date = now.date()
        course_end_time = datetime.combine(today_date, Config.COURSE_END_TIME).astimezone(tz_shanghai)
        logger.info("----------course_end_time: %s", course_end_time)
        logger.info("----------now: %s", now)
        # 判断是否超过课程结束时间
        if now > course_end_time:
            logger.warning("课程已结束，尝试签到")
            # 检查是否已有缺勤记录
            existing_record = Attendance.query.filter_by(
                student_id=student_id,
                date=today_date
            ).first()

            if not existing_record:
                # 创建缺勤记录
                absent_record = Attendance(
                    student_id=student_id,
                    course_id=course_id,
                    date=today_date,
                    check_in=None,
                    check_out=None,
                    status='Absent'
                )
                db.session.add(absent_record)
                db.session.commit()
                logger.info("已创建缺勤记录")

            return jsonify({
                "error": "Course has ended, check-in not allowed",
                "course_end_time": course_end_time.strftime('%Y-%m-%d %H:%M:%S'),
                "current_time": now.strftime('%Y-%m-%d %H:%M:%S')
            }), 400


        # 时间校验
        course_start = Config.COURSE_START_TIME
        logger.debug("当前时间: %s | 课程开始时间: %s", now.time(), course_start)
        is_late = now.time() > course_start
        logger.info("迟到判断: %s", is_late)

        # 检查是否重复签到
        existing = Attendance.query.filter_by(
            student_id=student_id,
            date=today_date
        ).first()

        if existing:
            logger.warning("重复签到尝试")
            return jsonify({
                "error": "Check-in already completed today",
                "first_checkin": existing.check_in
            }), 400

        # 构建考勤记录
        record = Attendance(
            student_id=student_id,
            course_id=course_id,
            date=now.date(),  # 新增日期字段
            check_in=now.time(),
            check_out=None,
            status='Late' if is_late else 'Normal'
        )
        logger.debug("准备插入记录: %s", {
            "student": student_id,
            "course": course_id,
            "check_in": now.strftime('%H:%M:%S'),
            "status": record.status
        })

        # 数据库操作
        db.session.add(record)
        logger.debug("已添加至Session")
        db.session.commit()
        logger.info("数据库提交成功")

        return jsonify({
            'success': True,
            'time': now.strftime('%H:%M:%S'),
            'status': record.status
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.exception("发生严重错误")
        return jsonify({
            "error": "Internal server error",
            "exception_type": str(type(e)),
            "detail": str(e)
        }), 500
    finally:
        logger.info("======== 请求处理结束 ========\n")


@attendance_bp.route('/check-out', methods=['POST', 'OPTIONS'])
def check_out():
    logger.info("\n======== 收到签退请求 ========")
    if request.method == 'OPTIONS':
        # 返回符合规范的预检响应
        return _build_preflight_response()
    try:
        # 获取东八区时间
        tz_shanghai = timezone(timedelta(hours=8))
        now = datetime.now(tz_shanghai)

        # 记录请求信息
        logger.debug("请求头: %s", dict(request.headers))
        logger.debug("原始数据: %s", request.get_data(as_text=True))

        data = request.json
        if not data:
            logger.error("请求体为空")
            return jsonify({"error": "Request body cannot be empty"}), 400

        # 验证必要字段
        required_fields = ['student_id']
        missing = [field for field in required_fields if field not in data]
        if missing:
            logger.error("缺失字段: %s", missing)
            return jsonify({"error": "Required fields missing", "missing": missing}), 400

        student_id = data['student_id']
        logger.info("Processing check-out for student: %s", student_id)

        # 查找当日签到记录
        today = now.date()
        record = Attendance.query.filter_by(
            student_id=student_id,
            date=today
        ).first()

        if not record:
            logger.error("未找到当日签到记录")
            return jsonify({"error": "Check-in required before check-out"}), 400

        if record.check_out is not None:
            logger.error("重复签退")
            return jsonify({"error": "Check-out already completed"}), 400

        # 判断是否早退
        is_early = now.time() < Config.COURSE_END_TIME
        logger.debug("当前时间: %s | 课程结束时间: %s", now.time(), Config.COURSE_END_TIME)
        logger.info("早退判断: %s", is_early)

        # 更新签退记录
        record.check_out = now.time()
        if is_early:
            record.status = 'Early' if record.status == 'Normal' else f'{record.status} + Early'
        logger.info(f"--------status--{record.status}")
        db.session.commit()
        logger.info("签退时间更新成功")

        return jsonify({
            'success': True,
            'check_out_time': now.strftime('%H:%M:%S'),
            'status': record.status
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.exception("签退处理异常")
        return jsonify({
            "error": "Check-out failed",
            "detail": str(e)
        }), 500
    finally:
        logger.info("======== 请求处理结束 ========\n")


@attendance_bp.route('/search', methods=['GET', 'OPTIONS'])
def get_student_attendance():
    logger.info("\n======== 收到学生查询请求 ========")
    if request.method == 'OPTIONS':
        # 返回符合规范的预检响应
        return _build_preflight_response()
    try:
        # 解析参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        status = request.args.get('status')
        student_id = request.args.get('student_id')

        # 构建基础查询
        query = Attendance.query.filter_by(
            student_id=student_id
        ).join(Student)
        logger.info("+++++status: ", status)
        # 添加过滤条件
        if start_date and end_date:
            query = query.filter(Attendance.date.between(start_date, end_date))
        if status:
            query = query.filter(Attendance.status == status)

        # 执行分页
        pagination = query.paginate(page=page, per_page=per_page)

        return jsonify({
            'data': [{
                'date': record.date.isoformat(),
                'check_in': record.check_in.isoformat() if record.check_in else None,
                'check_out': record.check_out.isoformat() if record.check_out else None,
                'status': record.status,
                'course_name': record.course.course_name
            } for record in pagination.items],
            'pagination': {
                'total': pagination.total,
                'current_page': pagination.page,
                'per_page': pagination.per_page
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500