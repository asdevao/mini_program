from flask import jsonify
from ..Models.CartModel import CartData
from ..Models.GoodsDetailModel import GoodsDetail
from ..utils.parse_goods_field_util import parse_skus
from blueprints import db
from sqlalchemy.exc import SQLAlchemyError


def get_sku_data_from_db(sku_id):
    """
    根据 sku_id 查询 GoodsDetail 表，返回匹配的行数据。
    """
    try:
        # 查询 GoodsDetail 表的所有记录
        goods_list = GoodsDetail.query.all()

        # 遍历每一行数据
        for goods in goods_list:
            # 解析 skus 字段
            skus = parse_skus(goods.skus)

            # 匹配 sku_id
            for sku in skus:
                if sku.get('id') == sku_id:
                    # 返回匹配的商品行和 SKU 数据
                    return {
                        'goods_detail': goods,  # 数据库中对应的商品行
                        'sku_data': sku  # 匹配的 SKU 数据
                    }

            # 如果没有匹配的 sku_id
        return None

    except Exception as e:
        print(f"Error during SKU query: {e}")
        return None


def add_to_cart(cart_id, goods_detail, sku_data, count, token):
    """
    将 query_result 数据添加到数据库中的购物车表。如果已存在相同的 ID、Name、Attributes Text 且 token 相同的数据，则直接更新 Count。
    """
    try:
        # 准备数据行
        attributes_text = f"{sku_data.get('specs', [{}])[0].get('name', '')}: {sku_data.get('specs', [{}])[0].get('valueName', '')}"

        # 查找是否有相同的记录
        existing_item = CartData.query.filter_by(
            sku_id=cart_id,
            name=goods_detail.name,
            attributes_text=attributes_text,
            token=token
        ).first()  # 查找匹配的第一条记录

        if existing_item:
            # 如果匹配记录存在，更新数量
            existing_item.count += count
            db.session.commit()  # 提交修改到数据库
            print(
                f"已更新购物车中 ID 为 {cart_id} 的商品数量，从 {existing_item.count - count} 增加到 {existing_item.count}")
        else:
            # 如果没有匹配记录，添加新记录
            new_item = CartData(
                id=cart_id,
                name=goods_detail.name,
                picture=sku_data.get("picture", ""),
                price=goods_detail.oldPrice,
                count=count,
                sku_id=cart_id,
                attributes_text=f"{sku_data.get('specs', [{}])[0].get('name', '')}: {sku_data.get('specs', [{}])[0].get('valueName', '')}",
                selected=True,
                current_price=goods_detail.price,
                stock=sku_data.get("inventory", 0),
                is_collected=False,
                discount=goods_detail.discount,
                is_effective=True,
                token=token
            )
            db.session.add(new_item)  # 添加新记录
            db.session.commit()  # 提交到数据库
            print(f"添加新商品到购物车：{new_item}")

        print("购物车数据库已成功更新！")
    except SQLAlchemyError as e:
        db.session.rollback()  # 回滚事务，避免数据库不一致
        print(f"添加到购物车时发生错误: {str(e)}")


def update_goods_inventory(sku_id, count):
    """
    更新商品库存
    :param sku_id: 商品的 SKU ID
    :param count: 减少的库存数量
    """
    try:
        # 查询 GoodsDetail 表中的所有商品记录
        goods_list = GoodsDetail.query.all()

        # 遍历所有商品记录
        for goods in goods_list:
            # 解析 skus 字段
            skus = parse_skus(goods.skus)

            # 查找对应的 SKU
            for sku in skus:
                if sku.get('skuCode') == sku_id:
                    current_inventory = sku.get('inventory', 0)
                    new_inventory = max(0, current_inventory - count)  # 确保库存不为负
                    sku['inventory'] = new_inventory
                    print(f"更新库存: SKU {sku_id} 的库存从 {current_inventory} 减少到 {new_inventory}")
                    break

            # 如果有更新库存，保存商品的变化
            if 'inventory' in sku:
                # 将更新后的 skus 字段写回 GoodsDetail 对象
                goods.skus = str(skus)

                # 提交到数据库保存
                db.session.commit()

        return jsonify({"msg": f"商品 SKU {sku_id} 的库存已成功更新"}), 200

    except Exception as e:
        db.session.rollback()  # 如果发生错误，回滚事务
        return jsonify({"msg": f"更新库存时发生错误: {str(e)}"}), 500