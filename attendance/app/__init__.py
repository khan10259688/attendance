# app/__init__.py
from flask import Flask, request, jsonify
from config import Config
from flask_cors import CORS
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity  # 添加这行


def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)

    # 第一阶段：基础CORS配置
    CORS(app,
         resources={r"/api/*": {
             "origins": [
                "*",
                "http://localhost:5173",    # 开发环境
                'http://127.0.0.1:5173',    # 本地开发
                'http://0.0.0.0:5173',    # 本地开发
                "http://47.113.109.132:5173" # 生产环境
            ],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # 仅声明实际使用的方法
             "allow_headers": ["Authorization", "Content-Type"],
             "supports_credentials": True,
             "expose_headers": ["Content-Disposition"]
         }}
         )

    # 加载配置
    app.config.from_object(config_class)

    # 初始化数据库等组件
    from .utils.database import db
    db.init_app(app)

    # 初始化定时任务
    from .scheduler import init_scheduler
    init_scheduler(app)

    # 注册路由蓝图（必须在CORS之后）

    from .routes import auth_bp
    app.register_blueprint(auth_bp)

    from .routes import attendance_bp
    app.register_blueprint(attendance_bp)

    from .routes import admin_bp
    app.register_blueprint(admin_bp)

    # 初始化JWT
    jwt = JWTManager(app)

    @app.before_request
    def check_jwt():
        app.logger.debug(f"收到请求: {request.method} {request.path} | Endpoint: {request.endpoint}")
        # 优先处理OPTIONS请求
        if request.method == 'OPTIONS':
            app.logger.debug("放行OPTIONS预检请求")
            return
        # 精确匹配登录端点
        if request.endpoint == 'auth.login':
            app.logger.debug("放行登录端点")
            return
        try:
            verify_jwt_in_request(locations=['headers'])  # 令牌查找
            user_id = get_jwt_identity()  # 存储用户信息
            app.logger.debug(f"用户 {user_id} 认证通过")
        except Exception as e:
            app.logger.error(f"JWT验证失败: {str(e)}")
            return jsonify({ "code": 401, "msg": "Invalid or expired credentials", "data": None }), 401

    # 应用启动时打印路由
    with app.app_context():
        print("\n=== 路由列表 ===")
        for rule in app.url_map.iter_rules():
            methods = ','.join(rule.methods)
            print(f"{rule.endpoint}: {rule} [{methods}]")
        print("===============\n")

    # 添加全局OPTIONS处理
    # @app.after_request
    # def inject_cors_headers(response):
    #     """为所有响应注入CORS头"""
    #     allowed_origins = ['http://localhost:5173', 'http://127.0.0.1:5173']
    #     origin = request.headers.get('Origin', '')

    #     if origin in allowed_origins:
    #         response.headers['Access-Control-Allow-Origin'] = origin
    #         response.headers['Access-Control-Allow-Credentials'] = 'true'
    #         response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'

    #     # 统一添加安全头
    #     response.headers['Vary'] = 'Origin'
    #     return response

    return app