from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from ..models.user import User
from ..utils.database import db
import logging
from datetime import datetime, time, timedelta, timezone


auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
logger = logging.getLogger('AuthAPI')


def _build_preflight_response():
    response = jsonify({"msg": "Preflight Accepted"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    return response


@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    logger.info("----login...")
    if request.method == 'OPTIONS':
        return _build_preflight_response()
    # 创建东八区时区对象
    tz_shanghai = timezone(timedelta(hours=8))
    # 获取东八区当前日期时间
    now = datetime.now(tz_shanghai)
    today_date = now.date()
    current_time = now.time()
    logger.info("\n======== 登录请求 ========")
    try:
        # 解析请求数据
        data = request.get_json()
        if not data:
            logger.error("空请求体")
            return jsonify({"error": "Request body cannot be empty"}), 400

        # 验证字段
        required_fields = ['username', 'password']
        if missing := [f for f in required_fields if f not in data]:
            logger.error("缺失字段: %s", missing)
            return jsonify({"error": "Required fields missing", "missing": missing}), 400

        # 查询用户
        user = User.query.options(
            db.joinedload(User.student),
            db.joinedload(User.teacher)
        ).filter_by(username=data['username']).first()

        if not user or user.password != data['password']:
            logger.warning("认证失败的用户: %s", data['username'])
            return jsonify({"error": "Invalid username or password"}), 401

        # 生成JWT令牌
        access_token = create_access_token(
            identity=user.user_id,
            expires_delta=timedelta(hours=48),
            additional_claims={
                "role": user.role,
                "username": user.username
            }
        )

        logger.info("用户 %s 登录成功", user.user_id)
        response_data = {
            "success": True,
            "token": access_token,
            "user": {
                "user_id": user.user_id,
                "username": user.username,
                "role": user.role,
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
        }
        logger.info(f"------00000------{user.student}")
        # 根据角色添加详细信息
        if user.role == 'student' and user.student:
            logger.info(f"------student------{user.student.name}")
            student = user.student
            response_data['user'].update({
                "profile": {
                    "type": "student",
                    "student_id": student.student_id,
                    "name": student.name,
                    "email": student.email,
                    "course": {
                        "course_id": student.course_id,
                        "course_name": student.course.course_name if student.course else None
                    }
                }
            })
        elif user.role == 'admin' and user.teacher:
            logger.info(f"-----admin-------{user.teacher.name}")
            teacher = user.teacher
            response_data['user'].update({
                "profile": {
                    "type": "teacher",
                    "teacher_id": teacher.teacher_id,
                    "name": teacher.name,
                    "email": teacher.email,
                    "courses": [{
                        "course_id": course.course_id,
                        "course_name": course.course_name
                    } for course in teacher.courses]
                }
            })

        # 更新最后登录时间
        user.last_login = today_date
        db.session.commit()
        return jsonify(response_data), 200

    except Exception as e:
        logger.error("登录异常: %s", str(e), exc_info=True)
        return jsonify({"error": "Internal server error"}), 500