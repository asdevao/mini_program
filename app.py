
from blueprints import create_app, db

# 创建应用实例
app = create_app('settings.py')  # 可以传递配置文件名来加载具体配置

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # 启动开发服务器
    app.run(
        host='0.0.0.0',  # 允许从外部访问
        port=5000,       # 默认端口
        debug=True       # 开启调试模式
    )
