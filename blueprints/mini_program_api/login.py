from flask import jsonify, Blueprint, request
from ..Models.UserLoginModel import UserDataWithPhoneNumber

bp = Blueprint('login', __name__)


# 广告区域-小程序 轮播图
@bp.route('/wxMin/simple', methods=['GET','POST'])
def login():
    try:
        # 获取请求的JSON数据
        data = request.get_json()

        # 从请求参数中获取 phoneNumber
        phone_number = data.get('phoneNumber')
        print(phone_number)

        if not phone_number:
            return jsonify({"code": "0", "msg": "Missing phoneNumber parameter"}), 400

        # 查询数据库中的用户数据
        user = UserDataWithPhoneNumber.query.filter_by(mobile=str(phone_number)).first()

        if not user:
            return jsonify({"code": "0", "msg": "PhoneNumber not found"}), 404

        # 构造返回结果
        result = {
            "id": str(user.id),
            "account": user.account,
            "mobile": user.mobile,
            "token": user.token,
            "avatar": user.avatar,
            "nickname": user.nickname,
        }

        # 返回数据
        return jsonify({
            "code": "1",
            "msg": "操作成功",
            "result": result
        }), 200

    except Exception as e:
        return jsonify({"code": "0", "msg": f"Internal server error: {str(e)}"}), 500