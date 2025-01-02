'''
Author: asdevao 1097802349@qq.com
Date: 2024-12-19 21:52:48
LastEditors: asdevao 1097802349@qq.com
LastEditTime: 2024-12-28 15:39:54
FilePath: \apps\blueprints\manage_api\inventory.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from flask import Blueprint, request
from blueprints import db
from ..Models.GoodsDetailModel import GoodsDetail
from ..Models.OrderModel import Order
from ..utils.parse_goods_field_util import parse_skus
from ..utils.response_util import ResponseUtil

bp = Blueprint('inventory', __name__)


@bp.route('/<skuid>', methods=['GET'])
def inventory(skuid):
    # 确保 sku_id 是字符串类型
    sku_id = str(skuid)

    # 初始化库存和销量
    sales_volume = 0  # 销售数量
    current_inventory = 0  # 当前库存数量
    matched_skus = []  # 用于存储所有匹配的 SKU 数据
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
                matched_skus.append({
                    'sku_code': sku.get('id'),
                    'sku_name': goods.name,
                    'description': goods.desc,
                    'inventory': sku.get('inventory'),
                    'price': sku.get('price'),
                    'attributes': f"{sku.get('specs', [{}])[0].get('name', '')}: {sku.get('specs', [{}])[0].get('valueName', '')}",
                    'picture': sku.get('picture'),
                    'sales_volume': sales_volume,  # 加入销量
                    'current_inventory': current_inventory  # 加入当前库存
                })
    if not matched_skus:
        return ResponseUtil.error(message='没有匹配的数据')
    print(matched_skus)
    print('查询到的数据销量为：', sales_volume, '查询到的库存为:', current_inventory)
    return ResponseUtil.success(result=matched_skus)


# 库存管理-更新库存
@bp.route('/<skuid>/update-stock', methods=['POST'])
def updateStock(skuid):
    data = request.json
    stock = data['stock']
    # 查询商品详情表中的所有商品记录，获取库存
    goods_list = GoodsDetail.query.all()
    # 遍历所有商品记录
    for goods in goods_list:
        # 解析 skus 字段
        skus = parse_skus(goods.skus)
        for sku in skus:
            if sku.get('skuCode') == skuid:
                sku['inventory'] = stock
        # 如果有更新库存，保存商品的变化
        if 'inventory' in sku:
            # 将更新后的 skus 字段写回 GoodsDetail 对象
            goods.skus = str(skus)
            # 提交到数据库保存
            db.session.commit()

    return ResponseUtil.success(message=f"商品 SKU {skuid} 的库存已成功更新")
