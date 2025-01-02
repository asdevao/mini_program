import importlib
from flask import Flask


def register_routes(app: Flask):
    """注册蓝图函数"""

    # 定义小程序和后台管理系统路由配置
    route_config = {
        'mini_program': {
            '/auth': 'mini_program_api.auth',
            '/home': 'mini_program_api.home',
            '/hot': 'mini_program_api.hot',
            '/category': 'mini_program_api.category',
            '/goods': 'mini_program_api.goods',
            '/login': 'mini_program_api.login',
            '/member/address': 'mini_program_api.address',
            '/member/profile': 'mini_program_api.profile',
            '/member/cart': 'mini_program_api.cart',
            '/member/order': 'mini_program_api.order',
            '/pay': 'mini_program_api.pay',
            '/manage': 'mini_program_api.manage',
        },
        'manage': {
            '/manage_auth': 'manage_api.auth',
            '/account': 'manage_api.account',
            '/orderlist': 'manage_api.orderlist',
            '/workbench': 'manage_api.workbench',
            '/sku': 'manage_api.inventory',
            '/dashboard': 'manage_api.dashboard'
        }
    }

    # 注册路由
    def register_blueprints(route_dict):
        for url_prefix, module_path in route_dict.items():
            # 动态导入模块
            try:
                # 确保从项目根目录开始导入
                module = importlib.import_module(f'blueprints.{module_path}')
                blueprint = getattr(module, 'bp', None)  # 获取蓝图对象
                if blueprint:
                    app.register_blueprint(blueprint, url_prefix=url_prefix)
                else:
                    print(f"Warning: No blueprint found for {module_path}")
            except ModuleNotFoundError as e:
                print(f"Error importing {module_path}: {e}")

    # 注册小程序路由
    register_blueprints(route_config['mini_program'])

    # 注册后台管理系统路由
    register_blueprints(route_config['manage'])
