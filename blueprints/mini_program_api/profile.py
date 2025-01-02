import os
from flask import jsonify, Blueprint, request
import requests
import json
from sqlalchemy.exc import SQLAlchemyError
from blueprints import db
from ..Models.ProfileModel import MemberProfileData
from ..utils.location_util import get_region_name_by_codes

bp = Blueprint('profile', __name__)

# 配置目标接口地址
AVATAR_URL = "https://pcapi-xiaotuxian-front.itheima.net/member/profile/avatar"
# 获取当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 配置 JSON 数据文件的路径
JSON_PATH = os.path.join(current_dir, 'static', 'data', '省市县.json')


# 获取会员信息
@bp.route('/', methods=['GET'])
def get_member_profile():

    """
        从数据库读取会员数据，校验 token 后返回数据。
    """
    try:
        # 获取前端传递的 token
        token = request.headers.get("Authorization")
        print("前端数据",token)
        if not token:
            return jsonify({"msg": "缺少授权令牌"}), 401
        # 查询所有用户数据
        profiles = MemberProfileData.query.all()

        # 提取 token 列数据
        tokens = [profile.token for profile in profiles]

        # 打印 token 列数据
        print("Token 列数据:", tokens)
        # 从数据库查询匹配的会员数据
        profile = MemberProfileData.query.filter_by(token=token).first()

        # 校验 token 是否匹配
        if not profile:
            return jsonify({"msg": "无效的 token"}), 403

        # 提取用户数据并返回
        result = {
            "id": profile.id,
            "avatar": profile.avatar,
            "nickname": profile.nickname,
            "account": profile.account,
            "gender": profile.gender,
            "birthday": profile.birthday.strftime('%Y-%m-%d') if profile.birthday else None,
            "fullLocation": profile.full_location,
            "profession": profile.profession,
        }

        return jsonify({"msg": "操作成功", "result": result}), 200

    except SQLAlchemyError as e:
        # 捕获数据库相关错误
        return jsonify({"msg": f"数据库错误: {str(e)}"}), 500

    except Exception as e:
        # 捕获其他错误
        return jsonify({"msg": f"服务器内部错误: {str(e)}"}), 500


# 更新会员信息的接口
@bp.route('/', methods=['PUT'])
def update_member_profile():
    """
    校验 token 后更新会员信息并保存至数据库。
    """
    try:
        # 从请求头中获取 token
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"msg": "Missing Authorization token"}), 401

        # 查询数据库中是否存在匹配的 token
        profile = MemberProfileData.query.filter_by(token=token).first()
        if not profile:
            return jsonify({"msg": "Invalid token"}), 403

        # 获取请求中的更新数据
        updated_data = request.get_json()

        # 获取省、市、区的编码
        province_code = updated_data.get("provinceCode")
        city_code = updated_data.get("cityCode")
        county_code = updated_data.get("countyCode")
        # 如果地址编码不为空，更新 full_location，否则保持原值不变
        if province_code and city_code and county_code:
            # 使用 JSON 文件查找地址并生成 fullLocation
            with open(JSON_PATH, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            full_location = get_region_name_by_codes(province_code, city_code, county_code, json_data)
            if not full_location:
                return jsonify({"msg": "Invalid region codes, unable to determine full location"}), 400

            # 更新 full_location
            profile.full_location = full_location

        # 更新其他可更新字段
        updatable_fields = ["nickname", "gender", "birthday", "profession"]
        for field in updatable_fields:
            if field in updated_data:
                setattr(profile, field, updated_data[field])

        # 提交更新到数据库
        db.session.commit()

        # 返回更新后的信息
        result = {
            "id": profile.id,
            "avatar": profile.avatar,
            "nickname": profile.nickname,
            "account": profile.account,
            "gender": profile.gender,
            "birthday": profile.birthday,
            "fullLocation": profile.full_location,
            "profession": profile.profession,
        }

        return jsonify({"msg": "操作成功", "result": result}), 200

    except SQLAlchemyError as e:
        db.session.rollback()  # 回滚事务
        return jsonify({"msg": f"数据库错误: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"msg": f"服务器内部错误: {str(e)}"}), 500

    # """
    #   使用 PUT 请求更新会员信息，带上 token 进行验证。
    #   """
    # try:
    #     # 从前端请求中获取 token 和更新的用户数据
    #     token = request.headers.get("Authorization")  # 获取 token
    #     if not token:
    #         return jsonify({"msg": "Missing Authorization token"}), 401
    #
    #     # 从请求体中获取需要更新的用户信息
    #     data = request.get_json()  # 获取更新数据，假设是 JSON 格式
    #     if not data:
    #         return jsonify({"msg": "No data provided for update"}), 400
    #
    #     # 构建请求头和请求体
    #     headers = {
    #         "Authorization": token,
    #         "Content-Type": "application/json"
    #     }
    #
    #     # 请求体中包含你想要更新的字段
    #     payload = {
    #         "nickname": data.get("nickname"),
    #         "gender": data.get("gender"),
    #         "birthday": data.get("birthday"),
    #         "profession": data.get("profession"),
    #         "provinceCode": data.get("provinceCode"),
    #         "cityCode": data.get("cityCode"),
    #         "countyCode": data.get("countyCode")
    #     }
    #
    #     # 向目标接口发送 PUT 请求
    #     response = requests.put(PROFILE_URL, json=payload, headers=headers)
    #     print(response.json())
    #     # 检查响应状态码
    #     if response.status_code == 200:
    #         # 更新成功，返回响应数据
    #         return jsonify(response.json()), 200
    #     else:
    #         # 请求失败，返回错误信息
    #         return jsonify({
    #             "msg": f"Failed to update profile. Error: {response.text}",
    #             "status": response.status_code
    #         }), response.status_code
    #
    # except Exception as e:
    #     # 捕获异常并返回错误信息
    #     return jsonify({"msg": f"Internal server error: {str(e)}"}), 500


# 更新头像
@bp.route('/avatar', methods=['POST'])
def update_avatar():
    """
      修改会员头像。
      根据传递的 token 更新用户头像。
    """
    try:
        # 获取前端传递的 token
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"msg": "Missing Authorization token"}), 401

        # 配置请求头
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }

        # 这里假设头像文件通过多部分表单（multipart/form-data）上传，下面的代码仅为示例
        # 假设图片路径是通过 request.files 上传的
        avatar_file = request.files.get("avatar")

        if not avatar_file:
            return jsonify({"msg": "Missing avatar file"}), 400

        # 发送请求，上传头像文件
        files = {
            "avatar": avatar_file
        }

        response = requests.post(AVATAR_URL, headers=headers, files=files)

        # 检查响应状态码
        if response.status_code == 200:
            # 请求成功，返回头像数据给前端
            profile_data = response.json()
            avatar_url = profile_data.get('result', {}).get('avatar', '')

            # 返回数据结构符合要求
            return jsonify({
                "msg": "操作成功",
                "result": {
                    "avatar": avatar_url
                }
            }), 200
        else:
            # 请求失败，返回错误信息
            return jsonify({
                "msg": f"Failed to update avatar. Error: {response.text}",
                "status": response.status_code
            }), response.status_code

    except Exception as e:
        # 捕获异常并返回错误信息
        return jsonify({"msg": f"Internal server error: {str(e)}"}), 500
