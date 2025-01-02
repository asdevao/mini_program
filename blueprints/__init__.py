
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_cors import CORS
from flask_migrate import Migrate
from redis import Redis
import settings as settings
from .route import register_routes  # 导入注册函数

# 初始化 Flask 扩展
db = SQLAlchemy()
mail = Mail()
migrate = Migrate()


def create_app(config_filename):
    # 创建 Flask 应用实例
    app = Flask(
        __name__,
        static_folder='./dist',  # 设置静态文件夹目录
        template_folder="./dist",  # 设置模板文件夹目录
        static_url_path=""  # 静态文件的 URL 前缀
    )

    # 加载配置
    app.config.from_object(settings)  # 从 settings.py 文件加载配置
    app.json.ensure_ascii = False
    # 初始化 Flask 扩展
    db.init_app(app)  # 初始化 SQLAlchemy
    mail.init_app(app)  # 初始化邮件发送功能
    migrate.init_app(app, db)  # 初始化数据库迁移工具

    CORS(app, expose_headers=["Content-Disposition"], supports_credentials=True)  # 启用 CORS 支持

    redis_client = Redis.from_url(app.config['REDIS_URL'])
    # 将 Redis 客户端注入到应用上下文中
    app.redis = redis_client

    # 创建 EmailUtil 实例并将其注入到应用上下文中
    from blueprints.utils.email_util import EmailUtil
    # app.email_util = EmailUtil(redis_client, mail)

    # 注册蓝图 (如有多个功能模块，请在此注册蓝图)
    register_routes(app)  # 调用注册函数

    return app
