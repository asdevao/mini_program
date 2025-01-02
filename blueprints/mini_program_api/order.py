import json
import uuid
from datetime import datetime, timedelta
from flask import jsonify, Blueprint, request
from sqlalchemy.exc import SQLAlchemyError
from blueprints import db
from ..Models.AddressModel import MemberAddress
from ..Models.CartModel import CartData
from ..Models.GoodsDetailModel import GoodsDetail
from ..Models.OrderModel import Order
from ..Models.UserLoginModel import UserDataWithPhoneNumber
from ..Models.UserModel import User
from ..utils.cart_uitl import get_sku_data_from_db
from ..utils.parse_goods_field_util import parse_skus

bp = Blueprint('order', __name__)


# 获取订单列表
@bp.route('/', methods=['GET'])
def get_order_data():
    """
        从数据库读取订单数据并返回 JSON 格式，支持分页和订单状态筛选
    """
    try:
        # 从请求参数中获取分页和筛选参数
        page = int(request.args.get("page", 1))  # 页码，默认第 1 页
        page_size = int(request.args.get("pageSize", 10))  # 页容量，默认每页 10 条
        order_state = int(request.args.get("orderState", 0))  # 订单状态，默认 0 表示全部

        token = request.headers.get("Authorization")
        print('订单列表', token)
        # 获取对应的 UserDataWithPhoneNumber 表中的数据行
        user_data = UserDataWithPhoneNumber.query.filter_by(token=token).first()
        user = User.query.filter_by(mobile=user_data.mobile).first()
        print('角色', user.role_code)

        # 构建查询语句
        query = Order.query

        # 如果角色不是 admin，添加 token 过滤条件
        if user.role_code != 'admin':
            query = query.filter(Order.token == token)

        # 如果 order_state 不等于 0，则添加过滤条件
        if order_state != 0:
            query = query.filter(Order.order_state == order_state)

        # 总记录数
        total_records = query.count()

        # 分页处理
        orders = query.offset((page - 1) * page_size).limit(page_size).all()

        # 初始化返回数据
        result = {
            "counts": total_records,
            "pageSize": page_size,
            "pages": (total_records + page_size - 1) // page_size,  # 总页数
            "page": page,
            "items": []
        }

        # 遍历查询结果，将订单数据添加到结果中
        for order in orders:
            # 解析 skus 数据（假设 skus 字段为 JSON 字符串）
            skus_data = parse_skus(order.skus or '[]')  # 自定义函数解析 skus

            # 构造单条订单数据
            order_item = {
                "id": order.order_id,  # 使用数据库中的 order_id
                "createTime": order.create_time.strftime('%Y-%m-%d %H:%M:%S') if order.create_time else "",
                "payType": order.pay_type,
                "orderState": order.order_state,
                "payLatestTime": order.pay_latest_time.strftime('%Y-%m-%d %H:%M:%S') if order.pay_latest_time else "",
                "countdown": order.countdown,
                "postFee": order.post_fee,
                "payMoney": order.pay_money,
                "totalMoney": order.total_money,
                "totalNum": order.total_num,
                "skus": [
                    {
                        "id": sku.get("id", "string"),
                        "spuId": sku.get("spuId", "string"),
                        "name": sku.get("name", "string"),
                        "quantity": sku.get("quantity", 0),
                        "image": sku.get("image", "string"),
                        "curPrice": sku.get("curPrice", 0),
                        "realPay": sku.get("realPay", 0),
                        "properties": [
                            {
                                "propertyMainName": str(sku.get('properties', [{}])[0].get('propertyMainName', '')),
                                "propertyValueName": str(sku.get('properties', [{}])[0].get('propertyValueName', ''))
                            }
                            if sku.get('properties') else []
                        ],
                        "attrsText": sku.get("attrsText", "string")
                    }
                    for sku in skus_data
                ]
            }
            result["items"].append(order_item)

        return jsonify({"msg": "Operation successful", "result": result}), 200

    except SQLAlchemyError as e:
        return jsonify({"msg": f"Database error: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"msg": f"Internal server error: {str(e)}"}), 500


# 填写订单-获取预付订单
@bp.route('/pre', methods=['GET'])
def get_pre_order_data():
    """
    获取预订单数据（从本地文件读取）并返回给前端
    """
    # try:
    #     # 从 Excel 文件中读取用户地址
    #     addresses_df = pd.read_excel(ADDRESSES_FILE)
    #     user_addresses = [
    #         {
    #             "id": str(row["id"]),
    #             "provinceCode": str(row["provinceCode"]),
    #             "cityCode": str(row["cityCode"]),
    #             "countyCode": str(row["countyCode"]),
    #             "address": str(row["address"]),
    #             "isDefault": int(row["isDefault"]),
    #             "receiver": str(row["receiver"]),
    #             "contact": str(row["contact"]),
    #             "fullLocation": str(row["fullLocation"]),
    #             "postalCode": str(row["postalCode"])
    #         }
    #         for _, row in addresses_df.iterrows()
    #     ]
    #
    #     # 从 Excel 文件中读取购物车信息并筛选 Selected 为 True 的行
    #     cart_df = pd.read_excel(CART_FILE)
    #     selected_cart_items = cart_df[cart_df["Selected"] == True]
    #
    #     # 从 Excel 文件中读取商品信息
    #     goods_df = pd.read_excel(GOODS_FILE)
    #
    #     goods = []
    #
    #     # 遍历选中的购物车行，根据 SKU ID 和 ID 匹配 goods 数据
    #     for _, cart_item in selected_cart_items.iterrows():
    #         # 查找 goods 中与当前 cart ID 匮配的商品
    #         matched_goods = goods_df[goods_df["id"] == cart_item["ID"]]
    #
    #         for _, goods_row in matched_goods.iterrows():
    #             # 使用 parse_skus 方法解析 skus 数据
    #             skus_data = goods_row.get("skus", "[]")
    #             skus_data = parse_skus(skus_data)  # 调用你提供的 parse_skus 方法
    #
    #             matched_sku = next((item for item in skus_data if str(item['skuCode']) == str(cart_item["SKU ID"])),
    #                                None)
    #             print('matched_sku', matched_sku)
    #
    #             # 如果找到匹配的 SKU，则添加到结果中
    #             if matched_sku:
    #                 goods.append({
    #                     "id": str(goods_row.get("id", "")),
    #                     "name": str(goods_row.get("name", "")),
    #                     "picture": str(matched_sku.get("picture", "")),
    #                     "count": int(cart_item.get("Count", 1)),  # 购物车中的商品数量
    #                     "skuId": str(cart_item["SKU ID"]),
    #                     "attrsText": str(matched_sku.get('specs', [{}])[0].get('valueName', '')),
    #                     "price": float(goods_row.get("oldPrice", 0)),
    #                     "payPrice": float(goods_row.get("price", 0)),  # 假设支付价格取商品默认支付价格
    #                     "totalPrice": float(matched_sku.get("price", 0)) * cart_item.get("Count", 1),
    #                     "totalPayPrice": float(matched_sku.get("price", 0)) * cart_item.get("Count", 1)
    #                 })
    #
    #     # 构造 summary 信息
    #     goods_count = sum(item["count"] for item in goods)
    #     total_price = sum(item["totalPrice"] for item in goods)
    #     total_pay_price = sum(item["totalPayPrice"] for item in goods)
    #     post_fee = 10.0  # 假设邮费为固定值
    #     discount_price = total_price - total_pay_price  # 折扣为总价减去支付总价
    #     total_pay_price = total_pay_price + post_fee
    #     summary = {
    #         "goodsCount": goods_count,
    #         "totalPrice": total_price,
    #         "totalPayPrice": total_pay_price,
    #         "postFee": post_fee,
    #         "discountPrice": discount_price
    #     }
    #
    #     result = {
    #         "userAddresses": user_addresses,
    #         "goods": goods,
    #         "summary": summary
    #     }
    #
    #     return jsonify({"msg": "Operation successful", "result": result}), 200
    #
    # except Exception as e:
    #     return jsonify({"msg": f"Internal server error: {str(e)}"}), 500
    try:
        # 获取请求中的 token
        token = request.headers.get("Authorization")

        # 获取该 token 对应的用户地址
        user_addresses = MemberAddress.query.filter_by(token=token).all()

        addresses = [
            {
                "id": str(address.id),
                "provinceCode": str(address.provinceCode),
                "cityCode": str(address.cityCode),
                "countyCode": str(address.countyCode),
                "address": str(address.address),
                "isDefault": int(address.isDefault),
                "receiver": str(address.receiver),
                "contact": str(address.contact),
                "fullLocation": str(address.fullLocation),
                "postalCode": str(address.postalCode)
            }
            for address in user_addresses
        ]

        # 获取购物车中选中的商品
        cart_items = CartData.query.filter_by(token=token, selected=True).all()
        goods = []

        for cart_item in cart_items:

            # 查找 SKU 数据
            goods_row = get_sku_data_from_db(cart_item.sku_id)['goods_detail']
            skus_data = get_sku_data_from_db(cart_item.sku_id)['sku_data']
            if goods_row:
                goods.append({
                    "id": str(goods_row.id),
                    "name": str(goods_row.name),
                    "picture": str(skus_data.get("picture", "")),
                    "count": int(cart_item.count),  # 购物车中的商品数量
                    "skuId": str(cart_item.sku_id),
                    "attrsText": str(skus_data.get('specs', [{}])[0].get('valueName', '')),
                    "price": float(goods_row.oldPrice),
                    "payPrice": float(goods_row.price),  # 假设支付价格是商品价格
                    "totalPrice": float(skus_data.get("price", 0)) * cart_item.count,
                    "totalPayPrice": float(skus_data.get("price", 0)) * cart_item.count
                })

        # 计算订单的 summary
        goods_count = sum(item["count"] for item in goods)
        total_price = sum(item["totalPrice"] for item in goods)
        total_pay_price = sum(item["totalPayPrice"] for item in goods)
        post_fee = 10.0  # 假设邮费为固定值
        discount_price = total_price - total_pay_price  # 折扣为总价减去支付总价
        total_pay_price = total_pay_price + post_fee  # 计算包含邮费后的总支付价格

        summary = {
            "goodsCount": goods_count,
            "totalPrice": total_price,
            "totalPayPrice": total_pay_price,
            "postFee": post_fee,
            "discountPrice": discount_price
        }

        result = {
            "userAddresses": addresses,
            "goods": goods,
            "summary": summary
        }

        return jsonify({"msg": "Operation successful", "result": result}), 200

    except Exception as e:
        return jsonify({"msg": f"Internal server error: {str(e)}"}), 500


# 填写订单-获取立即购买订单
@bp.route('/pre/now', methods=['GET'])
def get_pre_order_now():
    # """
    # 获取预订单数据（根据 skuId、count 和 addressId ）
    # """
    #
    # try:
    #     # 从请求参数获取 skuId、count 和 addressId
    #     sku_id = request.args.get('skuId')  # 购物车 SKU ID
    #     count = request.args.get('count', 1)  # 商品数量，默认为 1
    #     address_id = request.args.get('addressId')  # 地址 ID
    #     print("填写订单立即购买",address_id)
    #
    #     # 验证 count 参数
    #     try:
    #         count = int(count)
    #     except ValueError:
    #         return jsonify({"msg": "Invalid count parameter"}), 400
    #
    #     # 从 Excel 文件中读取用户地址
    #     addresses_df = pd.read_excel(ADDRESSES_FILE)
    #     user_addresses = [
    #         {
    #             "id": str(row["id"]),
    #             "provinceCode": str(row["provinceCode"]),
    #             "cityCode": str(row["cityCode"]),
    #             "countyCode": str(row["countyCode"]),
    #             "address": str(row["address"]),
    #             "isDefault": int(row["isDefault"]),
    #             "selected": True if str(row["id"]) == address_id else False  # 标记选中的地址
    #         }
    #         for _, row in addresses_df.iterrows()
    #     ]
    #
    #     # 从 Excel 文件中读取商品信息
    #     goods_df = pd.read_excel(GOODS_FILE)
    #
    #     # 在 goods.xlsx 中遍历每个商品，查找包含 sku_id 的 skus 字段
    #     goods = []
    #
    #     for _, goods_row in goods_df.iterrows():
    #         skus_data = parse_skus(goods_row['skus'])  # 解析 skus 列
    #         matched_sku = next((item for item in skus_data if str(item['skuCode']) == sku_id),
    #                            None)
    #
    #         # 如果找到匹配的 SKU，则添加到结果中
    #         if matched_sku:
    #             goods.append({
    #                 "id": str(goods_row.get("id", "")),
    #                 "name": str(goods_row.get("name", "")),
    #                 "picture": str(matched_sku.get("picture", "")),
    #                 "count": count,
    #                 "skuId": sku_id,
    #                 "attrsText": str(matched_sku.get('specs', [{}])[0].get('valueName', '')),
    #                 "price": float(goods_row.get("oldPrice", 0)),
    #                 "payPrice": float(matched_sku.get("price", 0)),  # 假设支付价格取商品默认支付价格
    #                 "totalPrice": float(matched_sku.get("price", 0)) * count,
    #                 "totalPayPrice": float(matched_sku.get("price", 0)) * count
    #             })
    #
    #         # 构造 summary 信息
    #     goods_count = sum(item["count"] for item in goods)
    #     total_price = sum(item["totalPrice"] for item in goods)
    #     total_pay_price = sum(item["totalPayPrice"] for item in goods)
    #     post_fee = 10.0  # 假设邮费为固定值
    #     discount_price = total_price - total_pay_price  # 折扣为总价减去支付总价
    #     total_pay_price = total_pay_price + post_fee
    #     summary = {
    #         "goodsCount": goods_count,
    #         "totalPrice": total_price,
    #         "totalPayPrice": total_pay_price,
    #         "postFee": post_fee,
    #         "discountPrice": discount_price
    #     }
    #
    #     result = {
    #         "userAddresses": user_addresses,
    #         "goods": goods,
    #         "summary": summary
    #     }
    #
    #     return jsonify({"msg": "Operation successful", "result": result}), 200
    #
    # except Exception as e:
    #     print(f"Error occurred: {str(e)}")  # 打印详细的错误信息
    #     return jsonify({"msg": f"Internal server error: {str(e)}"}), 500
    """
        获取预订单数据（根据 skuId、count 和 addressId ）
        """

    try:
        # 从请求参数获取 skuId、count 和 addressId
        sku_id = request.args.get('skuId')  # 购物车 SKU ID
        count = request.args.get('count', 1)  # 商品数量，默认为 1
        address_id = request.args.get('addressId')  # 地址 ID

        # 验证 count 参数
        try:
            count = int(count)
        except ValueError:
            return jsonify({"msg": "Invalid count parameter"}), 400

        # 如果 address_id 为空，尝试获取默认地址
        if not address_id:
            address = MemberAddress.query.filter_by(isDefault=True).first()

            if not address:
                # 如果没有默认地址，尝试获取第一个地址（如果有的话）
                address = MemberAddress.query.first()
                if not address:
                    return jsonify({"msg": "Address is required"}), 400  # 如果没有地址，要求提供地址
        else:
            address = MemberAddress.query.filter_by(id=address_id).first()

        # 构造用户地址信息
        user_addresses = [
            {
                "id": str(address.id),
                "provinceCode": str(address.provinceCode),
                "cityCode": str(address.cityCode),
                "countyCode": str(address.countyCode),
                "address": str(address.address),
                "isDefault": int(address.isDefault),
                "selected": True if str(address.id) == address_id else False  # 标记选中的地址
            }
        ]

        # 从数据库获取商品信息
        goods = []
        result = get_sku_data_from_db(sku_id)
        goods_row = result['goods_detail']

        if goods_row:
            # 获取匹配的 SKU 信息
            matched_sku = result['sku_data']

            if matched_sku:
                goods.append({
                    "id": str(goods_row.id),
                    "name": str(goods_row.name),
                    "picture": str(matched_sku.get("picture", "")),
                    "count": count,
                    "skuId": sku_id,
                    "attrsText": str(matched_sku.get('specs', [{}])[0].get('valueName', '')),
                    "price": float(goods_row.oldPrice or 0),
                    "payPrice": float(matched_sku.get("price", 0)),  # 假设支付价格取商品默认支付价格
                    "totalPrice": float(matched_sku.get("price", 0)) * count,
                    "totalPayPrice": float(matched_sku.get("price", 0)) * count
                })

        # 计算订单的汇总信息
        goods_count = sum(item["count"] for item in goods)
        total_price = sum(item["totalPrice"] for item in goods)
        total_pay_price = sum(item["totalPayPrice"] for item in goods)
        post_fee = 10.0  # 假设邮费为固定值
        discount_price = total_price - total_pay_price  # 折扣为总价减去支付总价
        total_pay_price = total_pay_price + post_fee

        # 汇总信息
        summary = {
            "goodsCount": goods_count,
            "totalPrice": total_price,
            "totalPayPrice": total_pay_price,
            "postFee": post_fee,
            "discountPrice": discount_price
        }

        # 返回结果
        result = {
            "userAddresses": user_addresses,
            "goods": goods,
            "summary": summary
        }

        return jsonify({"msg": "Operation successful", "result": result}), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}")  # 打印详细的错误信息
        return jsonify({"msg": f"Internal server error: {str(e)}"}), 500


# 提交订单
@bp.route('/', methods=['POST'])
def create_order():
    """
        接收订单数据并返回订单信息
    """

    try:
        token = request.headers.get("Authorization")  # 从 Header 获取 token
        # 当前时间
        now = datetime.now()
        create_time = now.strftime("%Y-%m-%d %H:%M:%S")
        pay_latest_time = (now + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
        countdown = int((now + timedelta(minutes=30) - now).total_seconds())

        # 获取请求数据
        data = request.get_json()
        print('前端传入数据', data)
        # 参数提取
        goods_data = data.get('goods', [])
        address_id = data.get('addressId')
        delivery_time_type = data.get('deliveryTimeType')
        buyer_message = data.get('buyerMessage', '')
        pay_channel = data.get('payChannel')
        pay_type = data.get('payType')

        # 获取收货地址数据
        address_data = MemberAddress.query.filter_by(id=address_id).first()

        if not address_data:
            return jsonify({"msg": "Address not found"}), 400

        # 组装地址信息
        address_info = {
            "receiver": address_data.receiver,
            "contact": address_data.contact,
            "provinceCode": address_data.provinceCode,
            "cityCode": address_data.cityCode,
            "countyCode": address_data.countyCode,
            "receiverAddress": f'{address_data.fullLocation}{address_data.address}'
        }
        # 校验商品数据
        if not goods_data or not isinstance(goods_data, list):
            return jsonify({"msg": "Invalid goods parameter"}), 400

        # 初始化商品数据
        goods = []
        matched_goods_ids = []  # 用于存储所有匹配到的商品 ID
        summary = {}
        for item in goods_data:
            sku_id = item.get('skuId')
            count = item.get('count', 1)

            # 尝试通过 sku_id 查找商品
            goods_row = GoodsDetail.query.filter_by(id=sku_id).first()

            if goods_row:
                matched_goods_ids.append(goods_row.id)
                goods.append({
                    "id": sku_id,
                    "spuId": sku_id,
                    "name": goods_row.name,
                    "quantity": count,
                    "image": "",  # 根据需要添加商品图片
                    "realPay": float(goods_row.oldPrice or 0),
                    "curPrice": float(goods_row.price or 0),
                    "totalMoney": float(goods_row.price or 0) * count,
                    "attrsText": "",  # 如果需要额外的属性文本，可以继续补充
                    "totalPayPrice": float(goods_row.price or 0) * count,
                    "properties": [{

                    }]
                })


            # 如果没有通过 sku_id 匹配成功，可以继续尝试通过 skus 匹配
            else:
                goods_row = get_sku_data_from_db(sku_id)['goods_detail']
                skus_data = get_sku_data_from_db(sku_id)['sku_data']

                goods.append({
                    "id": sku_id,
                    "spuId": sku_id,
                    "name": goods_row.name,
                    "quantity": count,
                    "image": skus_data.get("picture", ""),
                    "realPay": float(goods_row.oldPrice or 0),
                    "curPrice": float(goods_row.price or 0),
                    "totalMoney": float(skus_data['price'] or 0) * count,
                    "attrsText": str(skus_data.get('specs', [{}])[0].get('valueName', '')),
                    "totalPayPrice": float(skus_data['price'] or 0) * count,
                    "properties": [{
                        "propertyMainName": str(skus_data.get('specs', [{}])[0].get('name', '')),
                        "propertyValueName": str(skus_data.get('specs', [{}])[0].get('valueName', ''))
                    }]
                })
                print(goods)

        goods_count = sum(item["quantity"] for item in goods)
        total_pay_price = sum(item["totalPayPrice"] for item in goods)
        post_fee = 10.0  # 假设邮费为固定值
        total_pay_price += post_fee

        order_id = f"{address_id}-{uuid.uuid4()}"
        result = {
            "code": "1",
            "msg": "操作成功",
            "result": {
                "id": order_id,
                "createTime": create_time,
                "payType": pay_type,
                "orderState": 1,
                "payLatestTime": pay_latest_time,
                "countdown": countdown,
                "postFee": post_fee,
                "payMoney": total_pay_price,
                "payChannel": pay_channel,
                "payState": 1,
                "totalMoney": total_pay_price,
                "totalNum": str(goods_count),
                "buyerMessage": buyer_message,
                "deliveryTimeType": delivery_time_type,
                "receiverContact": address_info['receiver'],
                "receiverMobile": address_info['contact'],
                "provinceCode": address_info['provinceCode'],
                "cityCode": address_info['cityCode'],
                "countyCode": address_info['countyCode'],
                "receiverAddress": address_info['receiverAddress'],
                "payTime": None,
                "consignTime": None,
                "endTime": None,
                "closeTime": None,
                "evaluationTime": None,
                "skus": goods,
            },

            "summary": summary
        }
        # 创建订单对象并保存到数据库
        new_order = Order(
            order_id=order_id,
            create_time=create_time,
            pay_type=pay_type,
            order_state=1,  # 假设初始状态为已创建
            pay_latest_time=pay_latest_time,
            countdown=countdown,
            post_fee=post_fee,
            pay_money=total_pay_price,
            total_money=total_pay_price,
            total_num=goods_count,
            skus=json.dumps(goods, ensure_ascii=False),  # 商品信息转为 JSON 字符串
            token=token  # 用户的 token
        )

        db.session.add(new_order)
        db.session.commit()
        # 查询并删除购物车中所有 `selected=True` 的商品
        CartData.query.filter_by(selected=True).delete()

        # 提交事务
        db.session.commit()
        print('result', result)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"msg": f"Internal server error: {str(e)}"}), 500


# 获取订单详情
@bp.route('/<string:order_id>', methods=['GET'])
def get_order(order_id):
    """
    根据订单 ID 从本地文件读取订单数据并返回
    """
    #
    # try:
    #     print("订单详情订单id", order_id)
    #     # 读取订单文件
    #     order_df = pd.read_excel(ORDER_EXCEL_FILE)
    #
    #     # 确保 ID 列为字符串类型以便匹配
    #     order_df['Order ID'] = order_df['Order ID'].astype(str)
    #
    #     # 转换传入的 order_id 为字符串
    #     order_id = str(order_id)
    #
    #     # 根据订单 ID 长度动态匹配
    #     if len(order_id) < 18:
    #         # 如果长度大于 18，仅匹配前 16 位
    #         matched_row = order_df[order_df['Order ID'].str[:16] == order_id[:16]]
    #     else:
    #         # 否则直接匹配完整 ID
    #         matched_row = order_df[order_df['Order ID'] == order_id]
    #
    #     if matched_row.empty:
    #         return jsonify({"msg": "Order not found"}), 404
    #
    #     # 将匹配的订单行转换为字典
    #     order_data = matched_row.iloc[0].to_dict()
    #
    #     # 读取地址数据
    #     address_df = pd.read_excel(ADDRESS_FILE)
    #     # 确保 ID 列为字符串类型
    #     address_df['id'] = address_df['id'].astype(str)
    #
    #     # 查询与订单关联的地址
    #     address_id = order_data.get("Order ID", "")
    #     matched_address = address_df[address_df['id'] == address_id[:18]]
    #
    #     if matched_address.empty:
    #         return jsonify({"msg": "Address not found"}), 404
    #
    #     # 转换地址数据为字典
    #     address_data = matched_address.iloc[0].to_dict()
    #
    #     # 解析 skus 字符串为数组
    #     skus_data = parse_skus(order_data.get("skus", "[]"))
    #     print("匹配的商品详情", skus_data)
    #
    #     # 按期望结构整理返回数据
    #     result = {
    #         "msg": "操作成功",
    #         "result": {
    #             "id": order_data.get("Order ID", ""),
    #             "createTime": order_data.get("Create Time", ""),
    #             "payType": order_data.get("Pay Type", 0),
    #             "orderState": order_data.get("Order State", 0),
    #             "payLatestTime": order_data.get("Pay Latest Time", ""),
    #             "countdown": order_data.get("Countdown", 0),
    #             "postFee": order_data.get("Post Fee", "0"),
    #             "payMoney": order_data.get("Pay Money", "0"),
    #             "payChannel": 0,
    #             "totalMoney": order_data.get("Total Money", "0"),
    #             "deliveryTimeType": 0,
    #             "receiverContact": address_data.get('receiver', ''),
    #             "receiverMobile": address_data.get('contact', ''),
    #             "provinceCode": address_data.get('provinceCode', ''),
    #             "cityCode": address_data.get('cityCode', ''),
    #             "countyCode": address_data.get('countyCode', ''),
    #             "receiverAddress": f"{address_data.get('fullLocation', '')}{address_data.get('address', '')}",
    #             "payTime": None,
    #             "consignTime": None,
    #             "endTime": None,
    #             "closeTime": None,
    #             "evaluationTime": None,
    #             "totalNum": order_data.get("Total Num", "0"),
    #             "skus": skus_data
    #         }
    #     }
    #
    #     return jsonify(result), 200
    #
    # except Exception as e:
    #     return jsonify({"msg": f"Internal server error: {str(e)}"}), 500
    """
        根据订单 ID 从数据库读取订单数据并返回
    """
    try:
        print("订单详情订单id", order_id)

        # 根据订单 ID 长度动态匹配
        if len(order_id) < 18:
            # 如果订单 ID 小于 18，匹配前 16 位
            order_data = Order.query.filter(Order.order_id.like(f'{order_id[:16]}%')).first()
        else:
            # 如果订单 ID 长度大于或等于 18，完全匹配
            order_data = Order.query.filter_by(order_id=order_id).first()

        if not order_data:
            return jsonify({"msg": "Order not found"}), 404

        # 根据订单 ID 获取地址信息
        address_data = MemberAddress.query.filter(MemberAddress.id.like(f'{order_id[:18]}%')).first()

        if not address_data:
            return jsonify({"msg": "Address not found"}), 404

        # 解析 skus 字符串为数组
        skus_data = parse_skus(order_data.skus)  # 假设 parse_skus 函数已实现
        print("匹配的商品详情", skus_data)

        # 按期望结构整理返回数据
        result = {
            "msg": "操作成功",
            "result": {
                "id": order_data.order_id,
                "createTime": order_data.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "payType": order_data.pay_type or 0,
                "orderState": order_data.order_state,
                "payLatestTime": order_data.pay_latest_time.strftime(
                    "%Y-%m-%d %H:%M:%S") if order_data.pay_latest_time else None,
                "countdown": order_data.countdown or 0,
                "postFee": order_data.post_fee or 0,
                "payMoney": order_data.pay_money or 0,
                "payChannel": 0,
                "totalMoney": order_data.total_money or 0,
                "deliveryTimeType": 0,
                "receiverContact": address_data.receiver,
                "receiverMobile": address_data.contact,
                "provinceCode": address_data.provinceCode,
                "cityCode": address_data.cityCode,
                "countyCode": address_data.countyCode,
                "receiverAddress": f"{address_data.fullLocation}{address_data.address}",
                "payTime": None,
                "consignTime": None,
                "endTime": None,
                "closeTime": None,
                "evaluationTime": None,
                "totalNum": order_data.total_num,
                "skus": skus_data
            }
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"msg": f"Internal server error: {str(e)}"}), 500


# 填写订单-获取再次购买订单
@bp.route('/repurchase/<string:id>', methods=['GET'])
def repurchase_order(id):
    """
    根据订单 ID 获取数据并返回前端
    """
    # try:
    #     print('id:', str(id))
    #     # 读取订单文件
    #     order_df = pd.read_excel(ORDER_EXCEL_FILE)
    #     # 确保 ID 列为字符串类型以便匹配
    #     order_df['Order ID'] = order_df['Order ID'].astype(str)
    #
    #     # 查找与订单 ID 匹配的行
    #     matched_order = order_df[order_df['Order ID'] == str(id)]
    #     if matched_order.empty:
    #         return jsonify({"msg": "Order not found"}), 404
    #
    #     # 将订单数据转换为字典
    #     order_data = matched_order.iloc[0].to_dict()
    #
    #     # 解析订单中的 skus 数据
    #     skus_str = order_data.get("skus", "[]").replace("'", '"')  # 替换单引号为双引号
    #     goods = parse_skus(skus_str)
    #
    #     # 读取地址数据
    #     address_df = pd.read_excel(ADDRESS_FILE)
    #     # 确保 ID 列为字符串类型
    #     address_df['id'] = address_df['id'].astype(str)
    #     address_str = address_df['id'].str[:15]  # 提取前 15 位
    #     # 查询与订单关联的地址
    #     matched_address = address_df[address_str == str(id[:15])]
    #     # 提取地址数据
    #     user_addresses = [
    #         {
    #             "id": row["id"],
    #             "provinceCode": row["provinceCode"],
    #             "cityCode": row["cityCode"],
    #             "countyCode": row["countyCode"],
    #             "address": row["address"],
    #             "isDefault": row.get("isDefault", 0)  # 默认值为 0
    #         }
    #         for _, row in matched_address.iterrows()
    #     ]
    #
    #     # 计算 summary 数据
    #     goods_count = sum(item["quantity"] for item in goods)
    #     total_price = sum(item["totalMoney"] for item in goods)
    #     total_pay_price = sum(item["totalPayPrice"] for item in goods)
    #     post_fee = 10.0  # 假设邮费固定
    #     discount_price = 0.0  # 假设无折扣
    #
    #     summary = {
    #         "goodsCount": goods_count,
    #         "totalPrice": total_price,
    #         "totalPayPrice": total_pay_price + post_fee,
    #         "postFee": post_fee,
    #         "discountPrice": discount_price
    #     }
    #
    #     # 构造返回结果
    #     result = {
    #         "msg": "操作成功",
    #         "result": {
    #             "userAddresses": user_addresses,
    #             "goods": [
    #                 {
    #                     "id": order_data['Order ID'],
    #                     "name": item.get("name"),
    #                     "picture": item.get("image"),
    #                     "count": item.get("quantity"),
    #                     "skuId": item.get("spuId"),
    #                     "attrsText": item.get("attrsText"),
    #                     "price": item.get("realPay"),
    #                     "payPrice": item.get("curPrice"),
    #                     "totalPrice": item.get("totalMoney"),
    #                     "totalPayPrice": item.get("totalPayPrice")
    #                 }
    #                 for item in goods
    #             ],
    #             "summary": summary
    #         }
    #     }
    #
    #     return jsonify(result), 200
    #
    # except Exception as e:
    #     return jsonify({"msg": f"Internal server error: {str(e)}"}), 500
    print('id:', str(id))

    # 查找与订单 ID 匹配的订单数据
    # 完全匹配
    order_data = Order.query.filter_by(order_id=id).first()
    skus_str = order_data.skus  # 假设 skus 字段是存储的 JSON 格式的字符串
    goods = parse_skus(skus_str)  # 假设 parse_skus 函数已实现

    # 获取与订单关联的地址数据
    address_data = MemberAddress.query.filter(MemberAddress.id.like(f'{id[:15]}%')).all()

    # 生成用户地址列表
    user_addresses = [
        {
            "id": addr.id,
            "provinceCode": addr.provinceCode,
            "cityCode": addr.cityCode,
            "countyCode": addr.countyCode,
            "address": addr.address,
            "isDefault": addr.isDefault  # 默认值为 False
        }
        for addr in address_data
    ]

    # 计算 summary 数据
    goods_count = sum(item["quantity"] for item in goods)
    total_price = sum(item["totalMoney"] for item in goods)
    total_pay_price = sum(item["totalPayPrice"] for item in goods)
    post_fee = 10.0  # 假设邮费固定
    discount_price = 0.0  # 假设无折扣

    summary = {
        "goodsCount": goods_count,
        "totalPrice": total_price,
        "totalPayPrice": total_pay_price + post_fee,
        "postFee": post_fee,
        "discountPrice": discount_price
    }

    # 构造返回结果
    result = {
        "msg": "操作成功",
        "result": {
            "userAddresses": user_addresses,
            "goods": [
                {
                    "id": order_data.order_id,
                    "name": item.get("name"),
                    "picture": item.get("image"),
                    "count": item.get("quantity"),
                    "skuId": item.get("spuId"),
                    "attrsText": item.get("attrsText"),
                    "price": item.get("realPay"),
                    "payPrice": item.get("curPrice"),
                    "totalPrice": item.get("totalMoney"),
                    "totalPayPrice": item.get("totalPayPrice")
                }
                for item in goods
            ],
            "summary": summary
        }
    }

    return jsonify(result), 200


# 模拟发货-
@bp.route('/consignment/<string:id>', methods=['GET'])
def get_order_consignment(id):
    # """
    #     根据订单 ID 更新订单状态为 3 为待发货，并返回操作成功消息
    # """
    # try:
    #     # 从请求中获取订单 ID 参数
    #     print("模拟发货", id)
    #
    #     # 读取订单文件
    #     order_df = pd.read_excel(ORDER_EXCEL_FILE)
    #
    #     # 确保 ID 列为字符串类型以便匹配
    #     order_df['Order ID'] = order_df['Order ID'].astype(str)
    #
    #     # 转换传入的 order_id 为字符串
    #     order_id = str(id)
    #     order_id_prefix = order_id[:16]
    #
    #     # 使用 str.slice 截取前 16 位并进行匹配
    #     order_df_order_id = order_df['Order ID'].str.slice(0, 16)  # 提取前 16 位
    #
    #     # 获取匹配到的订单行
    #     matched_row = order_df[order_df_order_id == order_id_prefix]
    #
    #     # 检查是否找到了匹配的订单且其状态为 2 (待发货)
    #     if not matched_row.empty:
    #         current_order_state = matched_row.iloc[0]["Order State"]
    #
    #         if current_order_state == 2:
    #             # 如果订单状态为 2，更新为 3
    #             order_df.loc[order_df_order_id == order_id_prefix, "Order State"] = 3
    #             # 保存回 Excel 文件
    #             order_df.to_excel(ORDER_EXCEL_FILE, index=False)
    #             return jsonify({"msg": "操作成功"}), 200
    #         else:
    #             return jsonify({"msg": f"订单当前状态为 {current_order_state}，无法更新为待发货"}), 400
    #     else:
    #         return jsonify({"msg": "订单未找到"}), 404
    #
    # except Exception as e:
    #     return jsonify({"msg": f"Internal server error: {str(e)}"}), 500
    """
            根据订单 ID 更新订单状态为 3 为待发货，并返回操作成功消息
        """
    try:
        # 从请求中获取订单 ID 参数
        print("模拟发货", id)

        # 转换传入的 order_id 为字符串
        order_id = str(id)
        order_id_prefix = order_id[:16]

        # 查找订单（完全匹配）
        matched_order = Order.query.filter(Order.order_id.like(f'{order_id}%')).first()
        print(matched_order.order_id)
        # 检查是否找到了匹配的订单且其状态为 2 (待发货)
        if matched_order:
            current_order_state = matched_order.order_state

            if current_order_state == 2:
                # 如果订单状态为 2，更新为 3
                matched_order.order_state = 3
                db.session.commit()  # 提交更改
                return jsonify({"msg": "操作成功"}), 200
            else:
                return jsonify({"msg": f"订单当前状态为 {current_order_state}，无法更新为待发货"}), 400
        else:
            return jsonify({"msg": "订单未找到"}), 404

    except Exception as e:
        return jsonify({"msg": f"Internal server error: {str(e)}"}), 500


# 确认收货
@bp.route('/<string:id>/receipt', methods=['PUT'])
def update_order_receipt(id):
    # """
    # 向接口发送 PUT 请求，获取订单的收货信息，并返回给前端
    # :param id: 订单编号
    # :return: 返回处理后的数据给前端
    # """
    # try:
    #     # 读取订单文件
    #     order_df = pd.read_excel(ORDER_EXCEL_FILE)
    #
    #     # 确保 ID 列为字符串类型以便匹配
    #     order_df['Order ID'] = order_df['Order ID'].astype(str)
    #
    #     # 转换传入的 order_id 为字符串
    #     order_id = str(id)
    #     print("确认收货订单id", order_id)
    #
    #     # 仅匹配前 16 位
    #     matched_row = order_df[order_df['Order ID'].str[:16] == order_id[:16]]
    #
    #     if matched_row.empty:
    #         return jsonify({"msg": "Order not found"}), 404
    #
    #     # 更新订单状态为已收货 (4)
    #     order_df.loc[order_df['Order ID'].str[:16] == order_id[:16], "Order State"] = 4
    #     # 保存修改后的 Excel 文件
    #     order_df.to_excel(ORDER_EXCEL_FILE, index=False)
    #
    #     # 将匹配的订单行转换为字典
    #     order_data = matched_row.iloc[0].to_dict()
    #
    #     # 读取地址数据
    #     address_df = pd.read_excel(ADDRESS_FILE)
    #     # 确保 ID 列为字符串类型
    #     address_df['id'] = address_df['id'].astype(str)
    #
    #     # 查询与订单关联的地址
    #     address_id = order_data.get("Order ID", "")
    #     matched_address = address_df[address_df['id'] == address_id[:18]]
    #
    #     if matched_address.empty:
    #         return jsonify({"msg": "Address not found"}), 404
    #
    #     # 转换地址数据为字典
    #     address_data = matched_address.iloc[0].to_dict()
    #
    #     # 解析 skus 字符串为数组
    #     skus_data = parse_skus(order_data.get("skus", "[]"))
    #
    #     # 按期望结构整理返回数据
    #     result = {
    #         "msg": "操作成功",
    #         "result": {
    #             "id": order_data.get("Order ID", ""),
    #             "createTime": order_data.get("Create Time", ""),
    #             "payType": order_data.get("Pay Type", 0),
    #             "orderState": order_data.get("Order State", 0),
    #             "payLatestTime": order_data.get("Pay Latest Time", ""),
    #             "countdown": order_data.get("Countdown", 0),
    #             "postFee": order_data.get("Post Fee", "0"),
    #             "payMoney": order_data.get("Pay Money", "0"),
    #             "payChannel": 0,
    #             "totalMoney": order_data.get("Total Money", "0"),
    #             "deliveryTimeType": 0,
    #             "receiverContact": address_data.get('receiver', ''),
    #             "receiverMobile": address_data.get('contact', ''),
    #             "provinceCode": address_data.get('provinceCode', ''),
    #             "cityCode": address_data.get('cityCode', ''),
    #             "countyCode": address_data.get('countyCode', ''),
    #             "receiverAddress": f"{address_data.get('fullLocation', '')}{address_data.get('address', '')}",
    #             "payTime": None,
    #             "consignTime": None,
    #             "endTime": None,
    #             "closeTime": None,
    #             "evaluationTime": None,
    #             "totalNum": order_data.get("Total Num", "0"),
    #             "skus": skus_data
    #         }
    #     }
    #
    #     return jsonify(result), 200
    #
    # except Exception as e:
    #     return jsonify({"msg": f"Internal server error: {str(e)}"}), 500
    """
       向接口发送 PUT 请求，获取订单的收货信息，并返回给前端
       :param id: 订单编号
       :return: 返回处理后的数据给前端
       """
    try:
        # 转换传入的 order_id 为字符串
        order_id = str(id)
        print("确认收货订单id", order_id)

        # 查找订单（只匹配前 16 位）
        matched_order = Order.query.filter(Order.order_id.like(f'{order_id[:16]}%'), Order.order_state == 3).order_by(
            Order.create_time.desc()).first()
        print(matched_order.order_id)
        if not matched_order:
            return jsonify({"msg": "Order not found"}), 404

        # 更新订单状态为已收货 (4)
        matched_order.order_state = 4
        db.session.commit()  # 提交更改

        # 查询与订单关联的地址
        address = MemberAddress.query.filter(MemberAddress.id == order_id[:18]).first()

        if not address:
            return jsonify({"msg": "Address not found"}), 404

        # 解析 skus 字符串为数组
        skus_data = parse_skus(matched_order.skus)

        # 按期望结构整理返回数据
        result = {
            "msg": "操作成功",
            "result": {
                "id": matched_order.order_id,
                "createTime": matched_order.create_time.strftime(
                    "%Y-%m-%d %H:%M:%S") if matched_order.create_time else "",
                "payType": matched_order.pay_type or 0,
                "orderState": matched_order.order_state,
                "payLatestTime": matched_order.pay_latest_time.strftime(
                    "%Y-%m-%d %H:%M:%S") if matched_order.pay_latest_time else "",
                "countdown": matched_order.countdown or 0,
                "postFee": matched_order.post_fee or 0,
                "payMoney": matched_order.pay_money or 0,
                "payChannel": 0,  # 假设支付渠道为 0
                "totalMoney": matched_order.total_money or 0,
                "deliveryTimeType": 0,  # 假设为 0
                "receiverContact": address.receiver,
                "receiverMobile": address.contact,
                "provinceCode": address.provinceCode,
                "cityCode": address.cityCode,
                "countyCode": address.countyCode,
                "receiverAddress": f"{address.fullLocation or ''}{address.address}",
                "payTime": None,
                "consignTime": None,
                "endTime": None,
                "closeTime": None,
                "evaluationTime": None,
                "totalNum": matched_order.total_num or 0,
                "skus": skus_data
            }
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"msg": f"Internal server error: {str(e)}"}), 500


# # 模拟发货
# @bp.route('/<string:id>/logistics', methods=['GET'])
# def get_order_logistics(id):
#     """
#         获取订单物流信息
#         :param id: 订单 ID
#     """
#
#     # 拼接请求 URL（假设的第三方接口）
#     url = f"https://pcapi-xiaotuxian-front.itheima.net/member/order/{id}/logistics"
#
#     try:
#         # 发送 GET 请求获取物流数据
#         response = requests.get(url)
#
#         # 如果请求成功，响应的状态码应该是 200
#         if response.status_code == 200:
#             data = response.json()  # 解析返回的 JSON 数据
#             print('物流信息', data)
#
#             # 提取物流信息
#             result = data.get('result', {})
#             picture = result.get('picture', '')
#             count = result.get('count', 0)
#             company = result.get('company', {})
#             company_name = company.get('name', '')
#             company_number = company.get('number', '')
#             company_tel = company.get('tel', '')
#             logistics_list = result.get('list', [])
#
#             # 如果物流列表为空，返回信息
#             if not logistics_list:
#                 return jsonify({"msg": "No logistics data found"}), 404
#
#             # 创建一个 DataFrame 保存物流信息
#             logistics_data = []
#
#             for item in logistics_list:
#                 logistics_data.append({
#                     'Logistics ID': item.get('id', ''),
#                     'Text': item.get('text', ''),
#                     'Time': item.get('time', '')
#                 })
#
#             # 创建一个 DataFrame
#             logistics_df = pd.DataFrame(logistics_data)
#
#             # 确保 DataFrame 不为空，再保存到 Excel 文件
#             if not logistics_df.empty:
#                 logistics_df.to_excel(LOGISTICS_EXCEL_FILE, index=False, sheet_name='Logistics')
#             else:
#                 return jsonify({"msg": "No valid logistics data to save."}), 400
#
#             return jsonify({"msg": "获取物流信息成功", "data": logistics_data}), 200
#
#         else:
#             return jsonify({"msg": "Failed to fetch logistics data", "error": response.text}), response.status_code
#
#     except Exception as e:
#         return jsonify({"msg": f"Internal server error: {str(e)}"}), 500


# 删除订单
@bp.route('/', methods=['DELETE'])
def delete_orders():
    # """
    # 根据订单 ID 和 token 删除订单
    # :return: 返回删除结果给前端
    # """
    # try:
    #     # 从请求体获取 token 和 ids 参数
    #     data = request.json
    #     token = request.headers.get("Authorization")  # 从 Header 获取 token
    #     ids = data.get('ids', [])  # 获取订单 ID 数组
    #
    #     # 如果 ids 或 token 为空，返回错误
    #     if not token or not ids:
    #         return jsonify({"msg": "Token or ids are missing"}), 400
    #
    #     # 读取订单数据
    #     order_df = pd.read_excel(ORDER_EXCEL_FILE)
    #
    #     # 确保订单 ID 和 token 列为字符串类型以便匹配
    #     order_df['Order ID'] = order_df['Order ID'].astype(str)
    #     order_df['token'] = order_df['token'].astype(str)
    #
    #     # 遍历 ids 数组，检查每个订单 ID 和 token 是否匹配
    #     for order_id in ids:
    #         # 查找符合条件的订单
    #         matched_row = order_df[(order_df['Order ID'] == str(order_id)) & (order_df['token'] == token)]
    #
    #         # 如果找到了匹配的订单，删除该行
    #         if not matched_row.empty:
    #             order_df = order_df.drop(matched_row.index)
    #
    #     # 将更新后的数据保存回 Excel 文件
    #     order_df.to_excel(ORDER_EXCEL_FILE, index=False)
    #
    #     # 返回成功消息
    #     return jsonify({"msg": "操作成功"}), 200
    #
    # except Exception as e:
    #     return jsonify({"msg": f"Internal server error: {str(e)}"}), 500
    """
       根据订单 ID 和 token 删除订单
       :return: 返回删除结果给前端
       """
    try:
        # 从请求体获取 token 和 ids 参数
        data = request.json
        token = request.headers.get("Authorization")  # 从 Header 获取 token
        ids = data.get('ids', [])  # 获取订单 ID 数组

        # 如果 ids 或 token 为空，返回错误
        if not token or not ids:
            return jsonify({"msg": "Token or ids are missing"}), 400

        # 遍历 ids 数组并尝试删除匹配的订单
        for order_id in ids:
            # 查找符合条件的订单
            order = Order.query.filter_by(order_id=str(order_id), token=token).first()

            # 如果找到订单，删除
            if order:
                db.session.delete(order)

        # 提交删除操作
        db.session.commit()

        # 返回成功消息
        return jsonify({"msg": "操作成功"}), 200

    except Exception as e:
        db.session.rollback()  # 如果出现异常，回滚事务
        return jsonify({"msg": f"Internal server error: {str(e)}"}), 500


# 取消订单
@bp.route('<string:id>/cancel', methods=['PUT'])
def cancel_order(id):
    # """
    # 根据订单 ID 和取消理由取消订单
    # :param id: 订单编号
    # :return: 返回处理后的订单数据给前端
    # """
    # try:
    #     # 从请求体获取 cancelReason
    #     data = request.json
    #     cancel_reason = data.get('cancelReason')  # 获取取消理由
    #
    #     if not cancel_reason:
    #         return jsonify({"msg": "Cancel reason is missing"}), 400  # 如果取消理由为空，返回错误
    #
    #     # 读取订单文件
    #     order_df = pd.read_excel(ORDER_EXCEL_FILE)
    #
    #     # 确保 ID 列为字符串类型以便匹配
    #     order_df['Order ID'] = order_df['Order ID'].astype(str)
    #
    #     # 转换传入的 order_id 为字符串
    #     order_id = str(id)
    #     print(f"取消订单id: {order_id}")
    #
    #     # 匹配订单 ID
    #     matched_row = order_df[order_df['Order ID'] == order_id]
    #
    #     if matched_row.empty:
    #         return jsonify({"msg": "Order not found"}), 404  # 如果找不到对应的订单，返回 404
    #
    #     # 更新订单状态为已取消
    #     order_df.loc[order_df['Order ID'] == order_id, "Order State"] = 6
    #     order_df.loc[order_df['Order ID'] == order_id, "Cancel Reason"] = cancel_reason
    #
    #     # 保存修改后的 Excel 文件
    #     order_df.to_excel(ORDER_EXCEL_FILE, index=False)
    #
    #     # 将匹配的订单行转换为字典
    #     order_data = matched_row.iloc[0].to_dict()
    #
    #     # 读取地址数据
    #     address_df = pd.read_excel(ADDRESS_FILE)
    #     # 确保 ID 列为字符串类型
    #     address_df['id'] = address_df['id'].astype(str)
    #
    #     # 查询与订单关联的地址
    #     address_id = order_data.get("Order ID", "")
    #     matched_address = address_df[address_df['id'] == address_id[:18]]
    #
    #     if matched_address.empty:
    #         return jsonify({"msg": "Address not found"}), 404
    #
    #     # 转换地址数据为字典
    #     address_data = matched_address.iloc[0].to_dict()
    #
    #     # 解析 skus 字符串为数组
    #     skus_data = parse_skus(order_data.get("skus", "[]"))
    #
    #     # 按期望结构整理返回数据
    #     result = {
    #         "msg": "操作成功",
    #         "result": {
    #             "id": order_data.get("Order ID", ""),
    #             "createTime": order_data.get("Create Time", ""),
    #             "payType": order_data.get("Pay Type", 0),
    #             "orderState": order_data.get("Order State", 0),
    #             "payLatestTime": order_data.get("Pay Latest Time", ""),
    #             "postFee": order_data.get("Post Fee", "0"),
    #             "payMoney": order_data.get("Pay Money", "0"),
    #             "payChannel": 0,
    #             "totalMoney": order_data.get("Total Money", "0"),
    #             "totalNum": order_data.get("Total Num", "0"),
    #             "deliveryTimeType": 0,
    #             "receiverContact": address_data.get('receiver', ''),
    #             "receiverMobile": address_data.get('contact', ''),
    #             "receiverAddress": f"{address_data.get('fullLocation', '')}{address_data.get('address', '')}",
    #             "payTime": None,
    #             "consignTime": None,
    #             "endTime": None,
    #             "closeTime": None,
    #             "evaluationTime": None,
    #             "skus": skus_data
    #         }
    #     }
    #
    #     return jsonify(result), 200
    #
    # except Exception as e:
    #     return jsonify({"msg": f"Internal server error: {str(e)}"}), 500
    """
        根据订单 ID 和取消理由取消订单
        :param id: 订单编号
        :return: 返回处理后的订单数据给前端
        """
    try:
        # 从请求体获取 cancelReason
        data = request.json
        cancel_reason = data.get('cancelReason')  # 获取取消理由
        print(data)
        if not cancel_reason:
            return jsonify({"msg": "Cancel reason is missing"}), 400  # 如果取消理由为空，返回错误

        # 转换传入的 order_id 为字符串
        order_id = str(id)
        print(f"取消订单id: {order_id}")

        # 查询订单
        order = Order.query.filter_by(order_id=order_id).first()

        if not order:
            return jsonify({"msg": "Order not found"}), 404  # 如果找不到对应的订单，返回 404

        # 更新订单状态为已取消 (6)
        order.order_state = 6
        order.cancel_reason = cancel_reason  # 假设你在数据库模型中新增了 `cancel_reason` 字段

        # 提交数据库更改
        db.session.commit()

        # 查询地址数据
        address = MemberAddress.query.filter(MemberAddress.id == order_id[:18]).first()

        if not address:
            return jsonify({"msg": "Address not found"}), 404  # 如果找不到关联的地址，返回 404

        # 解析 skus 字符串为数组
        skus_data = parse_skus(order.skus or "[]")

        # 按期望结构整理返回数据
        result = {
            "msg": "操作成功",
            "result": {
                "id": order.order_id,
                "createTime": order.create_time.strftime('%Y-%m-%d %H:%M:%S') if order.create_time else "",
                "payType": order.pay_type or 0,
                "orderState": order.order_state,
                "payLatestTime": order.pay_latest_time.strftime('%Y-%m-%d %H:%M:%S') if order.pay_latest_time else "",
                "postFee": order.post_fee or 0,
                "payMoney": order.pay_money or 0,
                "payChannel": 0,
                "totalMoney": order.total_money or 0,
                "totalNum": order.total_num or 0,
                "deliveryTimeType": 0,
                "receiverContact": address.receiver,
                "receiverMobile": address.contact,
                "receiverAddress": f"{address.fullLocation or ''}{address.address}",
                "payTime": None,
                "consignTime": None,
                "endTime": None,
                "closeTime": None,
                "evaluationTime": None,
                "skus": skus_data
            }
        }

        return jsonify(result), 200

    except Exception as e:
        db.session.rollback()  # 回滚事务，防止意外错误
        return jsonify({"msg": f"Internal server error: {str(e)}"}), 500
