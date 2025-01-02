from flask import jsonify, Blueprint, request

from ..Models.GoodsDetailModel import GoodsDetail
from ..utils.cart_uitl import get_sku_data_from_db
from ..utils.parse_goods_field_util import (parse_goods_filed
                                                          )

bp = Blueprint('goods', __name__)


# 定义 /goods 接口
@bp.route('/', methods=['GET'])
def get_goods():
    # 获取商品 ID 参数
    goods_id = request.args.get("id")
    print(goods_id)
    if not goods_id:
        return jsonify({"code": "0", "msg": "Missing required parameter: id", "result": None}), 400

    # 从数据库中查询商品信息
    goods_data = GoodsDetail.query.filter_by(id=goods_id).first()
    # 如果数据库中没有找到商品数据，则使用自定义方法从数据库查询 SKU 数据
    if not goods_data:
        query_result = get_sku_data_from_db(goods_id)
        goods_detail = query_result.get('goods_detail')
        if not goods_detail:
            return jsonify({"code": "0", "msg": "Goods not found", "result": None}), 404
        # 如果通过自定义方法查询到数据，替换 goods_data 为 goods_detail
        goods_data = goods_detail

    result = parse_goods_filed(goods_data)

    return jsonify({"code": "1", "msg": "操作成功", "result": result})
