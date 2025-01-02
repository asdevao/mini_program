from blueprints import db
from flask import Blueprint, request, jsonify

from ..Models.GoodsDetailModel import GoodsDetail
from ..Models.OrderModel import Order
from ..utils.parse_goods_field_util import parse_skus

bp = Blueprint('manage', __name__)


@bp.route('/sku/search', methods=['POST'])
def searchSku():
    # 获取前端传来的 skuId
    data = request.get_json()  # 获取 JSON 请求体
    sku_id = data.get('sku_id')

    # 检查 sku_id 是否存在
    if not sku_id:
        return {"error": "sku_id is required"}, 400

    # 确保 sku_id 是字符串类型
    sku_id = str(sku_id)

    # 初始化库存和销量
    sales_volume = 0  # 销售数量
    current_inventory = 0  # 当前库存数量

    # 查询订单表中的所有商品记录，计算销量
    order_list = Order.query.all()
    for order in order_list:
        # 解析 skus 字段
        skus = parse_skus(order.skus)
        for sku in skus:
            # 确保 sku.get('skuCode') 和 sku_id 比较时类型一致
            if str(sku.get('spuId')) == sku_id:
                sales_volume += sku.get('quantity', 0)

    # 查询商品详情表中的所有商品记录，获取库存
    goods_list = GoodsDetail.query.all()
    # 遍历所有商品记录
    for goods in goods_list:
        # 解析 skus 字段
        skus = parse_skus(goods.skus)
        for sku in skus:
            if sku.get('skuCode') == sku_id:
                current_inventory = sku.get('inventory', 0)
    print('查询到的数据销量为：', sales_volume, '查询到的库存为:', current_inventory)

    # 返回结果
    if current_inventory is not None:
        return {
            "stock": current_inventory,
            "sales": sales_volume
        }
    else:
        return {"error": "SKU not found"}, 404


@bp.route('/sku/update', methods=['POST'])
def update_inventory():
    data = request.get_json()
    sku_id = data.get('skuId')  # 获取 SKU ID
    stock = data.get('stock')  # 获取新的库存值

    # 检查参数有效性
    if not sku_id or stock is None:
        return jsonify({"error": "skuId 和 stock 参数是必须的"}), 400

    # 确保库存是非负整数
    if not isinstance(stock, int) or stock < 0:
        return jsonify({"error": "库存值必须是非负整数"}), 400

    # 遍历商品记录
    goods_list = GoodsDetail.query.all()
    old_inventory = None
    new_inventory = None
    updated = False

    for goods in goods_list:
        skus = parse_skus(goods.skus)
        for sku in skus:
            if sku.get('skuCode') == sku_id:
                old_inventory = sku.get('inventory', 0)
                new_inventory = old_inventory + stock
                sku['inventory'] = new_inventory
                updated = True
                print(f"更新库存: SKU {sku_id} 的库存从 {old_inventory} 增加到 {new_inventory}")

        if updated:
            goods.skus = str(skus)  # 更新后的 skus 写回 GoodsDetail 对象
            db.session.commit()  # 提交更改
            break  # 找到并更新后退出循环

    if not updated:
        return jsonify({"error": "未找到指定的 SKU"}), 404

    # 返回响应，包括 SKU ID、旧库存和新库存
    return jsonify({
        "message": "库存更新成功",
        "result" : {
            "skuId": sku_id,
            "oldStock": old_inventory,
            "newStock": new_inventory
        }
    }), 200

