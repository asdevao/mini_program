from flask import jsonify, Blueprint
from ..Models.CategoryModel import HotGoods

bp = Blueprint('category', __name__)


@bp.route('top', methods=['GET'])
def get_category_data():
    # 从数据库获取所有数据
    category_data = HotGoods.query.all()

    # 构建响应格式
    response = {
        "code": "1",
        "msg": "操作成功",
        "result": []
    }

    # 用于构建结构的辅助字典
    category_dict = {}

    for item in category_data:
        category_id = item.category_id
        child_id = item.child_id
        goods_id = item.goods_id

        # 如果主类不存在，添加它
        if category_id not in category_dict:
            category_dict[category_id] = {
                "id": category_id,
                "name": item.category_name,
                "picture": item.category_picture,
                "imageBanners": [],  # 目前假设没有处理的图片，保持为空
                "children": []
            }
            response['result'].append(category_dict[category_id])

        # 如果子类不存在，添加它
        child_found = next((child for child in category_dict[category_id]['children'] if child['id'] == child_id), None)
        if not child_found:
            child_found = {
                "id": child_id,
                "name": item.child_name,
                "picture": item.child_picture,
                "parentId": None,
                "parentName": None,
                "categories": None,
                "brands": None,
                "saleProperties": None,
                "goods": []
            }
            category_dict[category_id]['children'].append(child_found)

        # 添加商品
        child_found['goods'].append({
            "id": goods_id,
            "name": item.goods_name,
            "desc": item.goods_description if item.goods_description else None,
            "price": str(item.goods_price),  # 转换价格为字符串
            "picture": item.goods_picture,
            "orderNum": item.goods_order_num or 0  # 防止没有订单数量时报错
        })

    return jsonify(response)
