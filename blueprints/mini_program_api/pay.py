from flask import Blueprint, jsonify, request
from blueprints import db

from ..Models.CartModel import CartData
from ..Models.OrderModel import Order
from ..utils.cart_uitl import update_goods_inventory
from ..utils.parse_goods_field_util import parse_skus

bp = Blueprint('pay', __name__)
ORDER_EXCEL_FILE = r"C:\Users\chenbin\Desktop\小程序后端\apps\static\data\orders.xlsx"


@bp.route('/mock', methods=['GET'])
def pay_order():
    """
       根据订单 ID 更新订单状态为 2，并返回操作成功消息
       """
    try:
        # 从请求中获取订单 ID 参数
        order_id = request.args.get('orderId', '')

        if not order_id:
            return jsonify({"msg": "Order ID is required"}), 400  # 返回错误信息

        # 转换传入的 order_id 为字符串
        order_id = str(order_id)

        # 精准匹配 order_id
        order = Order.query.filter_by(order_id=order_id).first()
        skus_data = parse_skus(order.skus or '[]')
        # 提取 SKU 的 ID 和 count
        sku_details = [{"id": sku.get("id"), "count": sku.get("quantity", 0)} for sku in skus_data]
        # 更新库存
        for sku in sku_details:
            sku_id = sku.get("id")
            count = sku.get("count", 0)
            if sku_id and count > 0:
                update_goods_inventory(sku_id, count)  # 调用减少库存函数

        if not order:
            return jsonify({"msg": "Order not found"}), 404  # 如果找不到订单，返回 404

        # 更新订单状态为 2
        order.order_state = 2

        # 提交数据库更改
        db.session.commit()

        # 返回成功消息
        return jsonify({"msg": "操作成功"}), 200

    except Exception as e:
        db.session.rollback()  # 回滚事务，防止意外错误
        print(f"Error: {str(e)}")  # 打印异常信息
        return jsonify({"msg": f"Internal server error: {str(e)}"}), 500

