import os
import random
from datetime import datetime
from flask import jsonify, Blueprint, request
import json
from blueprints import db
from sqlalchemy.exc import SQLAlchemyError
from ..Models.AddressModel import MemberAddress
from ..utils.location_util import get_region_name_by_codes

bp = Blueprint('address', __name__)

# 获取当前脚本所在的目录
current_dir = os.path.dirname(__file__)

# 配置 JSON 数据文件的路径
JSON_PATH = os.path.join( 'static', 'data', '省市县.json')


# 获取收货地址列表
@bp.route('/', methods=['GET'])
def get_addresses():
    """
       从数据库中读取会员地址数据并返回给前端。
       支持通过 token 过滤会员地址。
       """
    try:
        # 获取请求中的 token
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"msg": "Token is missing"}), 400
        print(token)
        # 查询与 token 匹配的会员地址数据
        addresses = MemberAddress.query.filter_by(token=token).all()

        # 将查询结果转换为字典列表
        results = []
        for address in addresses:
            address_data = {
                "id": address.id,
                "receiver": address.receiver,
                "contact": address.contact,
                "provinceCode": address.provinceCode,
                "cityCode": address.cityCode,
                "countyCode": address.countyCode,
                "address": address.address,
                "isDefault": int(address.isDefault),  # 转换为整数类型
                "fullLocation": address.fullLocation,
                "postalCode": address.postalCode,
                "addressTags": address.addressTags,
                "token": address.token,
                "created_at": address.created_at.isoformat(),  # 格式化日期
                "updated_at": address.updated_at.isoformat()  # 格式化日期
            }
            results.append(address_data)

        # 构造响应数据
        response = {
            "code": "1",
            "msg": "操作成功",
            "result": results
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"msg": f"Internal server error: {str(e)}"}), 500


# 获取地址详情
@bp.route("/<id>", methods=["GET"])
def get_address_by_id(id):
    # """
    # 从 Excel 文件中读取收货地址数据，根据 ID 和 Token 返回符合指定结构的数据。
    # """
    # try:
    #     # 获取请求头中的 Token
    #     token = request.headers.get("Authorization")
    #     if not token:
    #         return jsonify({"msg": "Missing Authorization token"}), 401
    #
    #     # 检查 Excel 文件是否存在
    #     if not os.path.exists(EXCEL_FILE_PATH):
    #         return jsonify({"msg": "No data found"}), 404
    #
    #     # 读取 Excel 文件
    #     addresses = pd.read_excel(EXCEL_FILE_PATH)
    #
    #     # 确保字段都转换为字符串类型（避免类型匹配问题）
    #     addresses = addresses.astype(str)
    #
    #     # 根据 id 和 token 过滤数据
    #     matching_address = addresses[
    #         (addresses["id"] == id) & (addresses["token"] == token)
    #         ]
    #
    #     # 如果没有匹配的地址，返回错误信息
    #     if matching_address.empty:
    #         return jsonify({"msg": "Invalid id or token"}), 403
    #
    #     # 获取匹配的地址数据
    #     address_data = matching_address.iloc[0].to_dict()
    #
    #     # 构造返回结果
    #     result = {
    #         "id": address_data["id"],
    #         "receiver": address_data["receiver"],
    #         "contact": address_data["contact"],
    #         "provinceCode": address_data["provinceCode"],
    #         "cityCode": address_data["cityCode"],
    #         "countyCode": address_data["countyCode"],
    #         "fullLocation": address_data["fullLocation"],
    #         "address": address_data["address"],
    #         "isDefault": int(address_data["isDefault"]),  # 转换为整数
    #     }
    #
    #     return jsonify({"msg": "操作成功", "result": result}), 200
    #
    # except Exception as e:
    #     return jsonify({"msg": f"Internal server error: {str(e)}"}), 500
    """
        从数据库中读取收货地址数据，根据 ID 和 Token 返回符合指定结构的数据。
        """
    try:
        # 获取请求头中的 Token
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"msg": "Missing Authorization token"}), 401

        # 从数据库中查找符合条件的地址
        matching_address = MemberAddress.query.filter_by(id=id, token=token).first()

        # 如果没有匹配的地址，返回错误信息
        if not matching_address:
            return jsonify({"msg": "Invalid id or token"}), 403

        # 获取匹配的地址数据并构造返回结果
        address_data = {
            "id": str(matching_address.id),
            "receiver": matching_address.receiver,
            "contact": matching_address.contact,
            "provinceCode": matching_address.provinceCode,
            "cityCode": matching_address.cityCode,
            "countyCode": matching_address.countyCode,
            "fullLocation": matching_address.fullLocation,
            "address": matching_address.address,
            "isDefault": int(matching_address.isDefault),  # 转换为整数
        }

        return jsonify({"msg": "操作成功", "result": address_data}), 200

    except Exception as e:
        return jsonify({"msg": f"Internal server error: {str(e)}"}), 500


@bp.route("/", methods=["POST"])
def add_addresses__excel():
    """
    从 Excel 文件中读取地址数据，返回给前端。
    """
    try:
        # 获取请求头中的 Token
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"msg": "Missing Authorization token"}), 401

        # 从请求体中获取其他数据
        data = request.get_json()

        # 获取省、市、区的编码
        province_code = data.get("provinceCode")
        city_code = data.get("cityCode")
        county_code = data.get("countyCode")

        # 读取 JSON 文件
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        # 调用 get_region_name_by_codes 获取完整的地址信息
        full_location = get_region_name_by_codes(province_code, city_code, county_code, json_data)

        # 如果返回的 full_location 为 None，给出错误信息
        if not full_location:
            return jsonify({"msg": "无效的地址编码，无法找到对应的省市区"}), 400

        # 构造新的一行数据
        new_address = MemberAddress(
            id= ''.join([str(random.randint(0, 9)) for _ in range(18)]),
            receiver=data.get("receiver"),
            contact=data.get("contact"),
            provinceCode=data.get("provinceCode"),
            cityCode=data.get("cityCode"),
            countyCode=data.get("countyCode"),
            address=data.get("address"),
            isDefault=int(data.get("isDefault", 0)),  # 确保 isDefault 是整数
            fullLocation=full_location,  # 将完整的地址字符串保存到 fullLocation 字段
            postalCode=data.get("postalCode", ""),  # 如果没有提供 postalCode，使用空字符串
            addressTags=data.get("addressTags", ""),  # 如果没有提供 addressTags，使用空字符串
            token=token,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # 将新地址插入数据库
        db.session.add(new_address)
        db.session.commit()  # 提交事务

        return jsonify({"msg": "操作成功，新地址已添加"}), 200

    except Exception as e:
        # 捕获详细的错误信息并返回
        db.session.rollback()  # 出错时回滚事务
        return jsonify({"msg": f"Internal server error: {str(e)}"}), 500


# 修改收货地址
@bp.route("/<id>", methods=["PUT"])
def update_address_by_id(id):
    """
       根据 ID 和 Token 更新收货地址。
       """
    try:
        print(id)
        # 获取请求头中的 Token
        token = request.headers.get("Authorization")
        updated_data = request.get_json()

        # 查找对应的地址记录
        address = MemberAddress.query.filter_by(id=id, token=token).first()

        # 如果没有找到对应的地址，返回 404 错误
        if not address:
            return jsonify({"msg": "未找到匹配的收货地址"}), 404

        # 更新地址字段
        for key, value in updated_data.items():
            if hasattr(address, key):  # 确保属性存在
                setattr(address, key, value)

        # 更新时间
        address.updated_at = datetime.utcnow()

        # 提交更新
        db.session.commit()

        # 返回更新后的数据
        return jsonify({"msg": "操作成功", "result": updated_data}), 200

    except SQLAlchemyError as e:
        # 如果发生数据库错误，返回错误信息
        db.session.rollback()  # 回滚事务
        return jsonify({"msg": f"数据库错误: {str(e)}"}), 500

    except Exception as e:
        # 捕获其他错误
        return jsonify({"msg": f"Internal server error: {str(e)}"}), 500


# 删除收货地址
@bp.route("/<id>", methods=["DELETE"])
def delete_address(id):
    """
    删除指定收货地址，并返回结果。
    - Path 参数: id (收货地址 ID)
    - Header 参数: token (授权令牌)
    """
    try:
        # 获取前端发送的 token
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"msg": "Missing Authorization token"}), 401
            # 查找匹配的地址记录
        address = MemberAddress.query.filter_by(id=id, token=token).first()

        # 如果找不到记录，返回 404
        if not address:
            return jsonify({"msg": f"未找到 ID 为 {id} 的收货地址或未授权"}), 404

        # 删除记录
        db.session.delete(address)
        db.session.commit()

        return jsonify({"msg": "操作成功", "result": {"id": id}}), 200

    except SQLAlchemyError as e:
        # 如果发生数据库错误，回滚事务并返回错误信息
        db.session.rollback()
        return jsonify({"msg": f"数据库错误: {str(e)}"}), 500

    except Exception as e:
        # 捕获其他错误
        return jsonify({"msg": f"服务器内部错误: {str(e)}"}), 500

    #     # 读取 Excel 文件数据
    #     addresses = pd.read_excel(EXCEL_FILE_PATH, dtype=str)
    #
    #     # 确保字段类型为字符串
    #     addresses["id"] = addresses["id"].astype(str)
    #     addresses["token"] = addresses["token"].astype(str)
    #
    #     # 处理前端传入的 id，忽略最后两位
    #     id_str = str(int(float(id)))  # 转换科学计数法 -> 整数 -> 字符串
    #     id_str_trimmed = id_str[:-2]  # 去除最后两位
    #     print(f"传入 ID（去掉最后两位）: {id_str_trimmed}")
    #
    #     # 截取 Excel 中的 ID，忽略最后两位
    #     id_trimmed = addresses["id"].str[:-2]  # 添加临时列，忽略最后两位
    #     print(f"所有 ID（去掉最后两位）: {id_trimmed}")
    #     # 查找符合条件的记录
    #     matching_index = addresses[
    #         (id_trimmed == id_str_trimmed) & (addresses["token"] == token)
    #         ].index
    #
    #     if matching_index.empty:
    #         return jsonify({"msg": f"Address with ID {id_str} not found or unauthorized"}), 404
    #
    #     # 删除记录
    #     addresses = addresses.drop(matching_index)
    #
    #     # 将数据写回 Excel 文件
    #     addresses.to_excel(EXCEL_FILE_PATH, index=False)
    #
    #     return jsonify({"msg": "操作成功", "result": {"id": id_str}}), 200
    #
    # except Exception as e:
    #     return jsonify({"msg": f"Internal server error: {str(e)}"}), 500
