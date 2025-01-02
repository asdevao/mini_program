from flask import jsonify, Blueprint, request
from ..Models.HotModel import HotInVogue, HotPreference, HotNew, HotOneStop
from ..utils.hot_util import load_data_from_db

bp = Blueprint('hot', __name__)


# 特惠推荐-小程序
@bp.route('/preference', methods=['GET'])
def get_hot_preference_data():
    """
    提供 /hot/preference 路由，返回符合查询参数的 JSON 数据。
    """
    # 获取请求参数
    sub_type = request.args.get("subType", None, type=int)
    page_size = request.args.get("pageSize", 10, type=int)
    page = request.args.get("page", 1, type=int)

    try:
        # 加载并格式化数据
        data = load_data_from_db(HotPreference, sub_type=sub_type, page_size=page_size, page=page)
        return jsonify({"result": data, "status": 200, "msg": "操作成功", 'code': '1'})
    except Exception as e:
        # 错误处理
        return jsonify({"status": 500, "message": f"Error: {str(e)}"}), 500


@bp.route('/inVogue', methods=['GET'])
def hot_inVogue():
    sub_type = request.args.get("subType", None, type=int)
    page_size = request.args.get("pageSize", 10, type=int)
    page = request.args.get("page", 1, type=int)

    try:
        # 加载并格式化数据
        data = load_data_from_db(HotInVogue, sub_type=sub_type, page_size=page_size, page=page)
        return jsonify({"result": data, "status": 200, "msg": "操作成功", 'code': '1'})
    except Exception as e:
        # 错误处理
        return jsonify({"status": 500, "message": f"Error: {str(e)}"}), 500


@bp.route('/oneStop', methods=['GET'])
def hot_oneStop():
    sub_type = request.args.get("subType", None, type=int)
    page_size = request.args.get("pageSize", 10, type=int)
    page = request.args.get("page", 1, type=int)

    try:
        # 加载并格式化数据
        data = load_data_from_db(HotOneStop, sub_type=sub_type, page_size=page_size, page=page)
        return jsonify({"result": data, "status": 200, "msg": "操作成功", 'code': '1'})
    except Exception as e:
        # 错误处理
        return jsonify({"status": 500, "message": f"Error: {str(e)}"}), 500


@bp.route('/new', methods=['GET'])
def hot_new():
    sub_type = request.args.get("subType", None, type=int)
    page_size = request.args.get("pageSize", 10, type=int)
    page = request.args.get("page", 1, type=int)

    try:
        # 加载并格式化数据
        data = load_data_from_db(HotNew, sub_type=sub_type, page_size=page_size, page=page)
        return jsonify({"result": data, "status": 200, "msg": "操作成功", 'code': '1'})
    except Exception as e:
        # 错误处理
        return jsonify({"status": 500, "message": f"Error: {str(e)}"}), 500
