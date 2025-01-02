from flask import jsonify, Blueprint, request
from sqlalchemy.exc import SQLAlchemyError
from blueprints import db
from ..Models.CartModel import CartData
from ..utils.cart_uitl import add_to_cart, get_sku_data_from_db


bp = Blueprint('cart', __name__)


# 查询商品数据并返回匹配的行
@bp.route('/', methods=['GET'])
def get_cart_data():
    """
      从数据库中查询购物车数据并返回 JSON 格式
      """
    try:
        # 获取请求参数（如果有用户的 token，可以传入用来过滤用户的购物车数据）
        token = request.headers.get("Authorization")
        print('购物车:', token)
        # 查询购物车数据，如果 token 存在，则过滤当前用户的购物车

        cart_items = CartData.query.filter_by(token=token).all()

        # 检查是否有购物车数据
        if not cart_items:
            return jsonify({"msg": "No cart data found", "result": []}), 200

        # 将查询结果转为 JSON 格式
        cart_items_list = []
        for item in cart_items:
            cart_item = {
                "id": str(item.id),
                "name": item.name,
                "picture": item.picture,
                "price": float(item.price) if item.price else 0.0,
                "count": item.count,
                "skuId": item.sku_id,
                "attrsText": item.attributes_text,  # 商品描述
                "selected": item.selected,
                "nowPrice": float(item.current_price) if item.current_price else 0.0,
                "stock": item.stock,
                "isCollect": item.is_collected,
                "discount": float(item.discount) if item.discount else 0.0,
                "isEffective": item.is_effective,
            }
            cart_items_list.append(cart_item)

        # 返回完整的 JSON 格式响应
        response = {
            "msg": "Success",
            "result": cart_items_list
        }
        print(response)
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"msg": f"Failed to fetch data from database: {str(e)}"}), 500


# 加入购物车
@bp.route('/', methods=['POST'])
def add_cart_data():
    try:
        # 从前端接收数据
        data = request.json
        token = request.headers.get("Authorization")  # 从 Header 获取 token

        sku_id = data["skuId"]
        count = data["count"]

        # 使用自定义方法从数据库查询 SKU 数据
        result = get_sku_data_from_db(sku_id)

        goods_detail = result['goods_detail']
        sku_data = result['sku_data']
        # 调用 add_to_cart 函数来处理添加或更新购物车项
        add_to_cart(
            cart_id=sku_id,  # 使用 sku_id 作为 cart_id
            goods_detail=goods_detail,
            sku_data=sku_data,
            count=count,
            token=token
        )

        # 提交更改到数据库
        db.session.commit()

        # 返回成功响应
        response_data = {
            "code": "1",
            "msg": "操作成功",
            "result": {
                "skuId": sku_data.get("skuCode", ""),
                "name": sku_data.get("specs", [{}])[0].get("valueName", ""),  # 假设规格名作为商品名称
                "attributes_text": sku_data.get("specs", [{}])[0].get("valueName", ""),
                "picture": sku_data.get("picture", ""),
                "price": goods_detail.oldPrice,
                "nowPrice": goods_detail.price,
                "selected": True,
                "stock": sku_data.get("inventory", 0),
                "count": count,
                "discount": goods_detail.discount,
                "isCollect": False,
                "isEffective": True,
                "id": goods_detail.id,
            },
        }
        return jsonify(response_data), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"数据库错误: {e}")
        return jsonify({"msg": f"Database error: {str(e)}"}), 500

    except Exception as e:
        print(f"发生错误: {e}")
        return jsonify({"msg": f"Error occurred: {str(e)}"}), 500


# 删除购物车单品
@bp.route('/', methods=['DELETE'])
def delete_cart_data():
    """
    删除购物车中指定的 SKU ID 集合。
    请求参数:
    - ids: 需要删除的 SKU ID 数组 (array[string])
    - token: 身份验证令牌 (header)
    """
    try:
        # 获取请求数据
        data = request.json
        token = request.headers.get("Authorization")  # 从 Header 获取 token

        # 校验参数
        if not data or "ids" not in data:
            return jsonify({"msg": "Missing 'ids' parameter in request body"}), 400

        ids_to_delete = data["ids"]
        if not isinstance(ids_to_delete, list) or not all(isinstance(i, str) for i in ids_to_delete):
            return jsonify({"msg": "'ids' must be an array of strings"}), 400

        # 查询符合条件的购物车项
        items_to_delete = CartData.query.filter(CartData.token == token, CartData.sku_id.in_(ids_to_delete)).all()

        if not items_to_delete:
            return jsonify({"msg": "No matching items found to delete"}), 404

        # 批量删除购物车项
        for item in items_to_delete:
            db.session.delete(item)

        # 提交删除操作
        db.session.commit()

        # 返回删除成功的响应
        return jsonify({"msg": f"Successfully deleted {len(items_to_delete)} items from the cart"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()  # 如果发生数据库错误，则回滚事务
        return jsonify({"msg": f"Database error: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"msg": f"Error occurred: {str(e)}"}), 500


@bp.route('/<skuId>', methods=['PUT'])
def update_cart_item(skuId):
    """
    更新购物车中指定 SKU ID 的商品信息。
    请求参数:
    - Path 参数: skuId (string)
    - Header 参数: token (string)
    - Body 参数:
        - count (integer): 商品数量
        - selected (boolean): 商品选择状态
    返回数据:
    - 符合期望的 JSON 格式
    """
    try:
        # 从请求中提取参数
        data = request.json
        token = request.headers.get("Authorization")  # 从 Header 获取 token

        # 校验请求参数
        if not token:
            return jsonify({"msg": "Missing 'Authorization' header"}), 400
        if not data:
            return jsonify({"msg": "Request body is empty"}), 400

        # 查找匹配的购物车项
        cart_item = CartData.query.filter_by(sku_id=skuId, token=token).first()
        if not cart_item:
            return jsonify({"msg": f"No matching cart item found for SKU ID: {skuId}"}), 404

        # 动态更新字段：检查传入的数据中包含的字段
        if "count" in data:
            cart_item.count = data["count"]  # 更新商品数量

        if "selected" in data:
            cart_item.selected = data["selected"]  # 更新商品是否选中

        # 提交更改到数据库
        db.session.commit()

        # 返回更新后的数据
        response_data = {
            "msg": "Operation successful",
            "result": {
                "id": str(cart_item.id),  # 确保类型为字符串
                "name": cart_item.name,
                "picture": cart_item.picture,
                "price": float(cart_item.price),  # 确保类型为浮点数
                "count": cart_item.count,  # 确保类型为整数
                "skuId": cart_item.sku_id,
                "attrsText": cart_item.attributes_text,
                "nowPrice": float(cart_item.current_price),
                "stock": cart_item.stock,
                "isCollect": cart_item.is_collected,
                "discount": float(cart_item.discount),
                "isEffective": cart_item.is_effective
            }
        }
        return jsonify(response_data), 200

    except SQLAlchemyError as e:
        db.session.rollback()  # 如果发生数据库错误，则回滚事务
        return jsonify({"msg": f"Database error: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"msg": f"Error occurred: {str(e)}"}), 500


@bp.route('/selected', methods=['PUT'])
def update_cart_selected():
    """
    更新购物车中所有商品的选择状态。
    请求参数:
    - Header 参数: token (string)
    - Body 参数:
        - selected (boolean): 是否选中
    返回数据:
    - msg: 操作结果信息
    - result: 空对象
    """
    try:
        # 从请求中提取参数
        data = request.json
        token = request.headers.get("Authorization")  # 从 Header 获取 token

        # 校验请求参数
        if not token:
            return jsonify({"msg": "Missing 'Authorization' header"}), 400
        if "selected" not in data:
            return jsonify({"msg": "Missing 'selected' in request body"}), 400

        selected = data["selected"]

        # 查询指定 token 下的所有购物车项
        cart_items = CartData.query.filter_by(token=token).all()
        if not cart_items:
            return jsonify({"msg": f"No cart items found for token: {token}"}), 404

        # 批量更新所有商品的选择状态
        for item in cart_items:
            item.selected = selected

        # 提交更改到数据库
        db.session.commit()

        # 返回操作成功的响应
        return jsonify({
            "msg": "Operation successful",
            "result": {}
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()  # 如果发生数据库错误，则回滚事务
        return jsonify({"msg": f"Database error: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"msg": f"Error occurred: {str(e)}"}), 500
