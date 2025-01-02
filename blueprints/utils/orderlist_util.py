from ..Models.AddressModel import MemberAddress
from ..utils.parse_goods_field_util import parse_skus


def mapping_order_State(order_state):
    # 状态映射字典
    order_state_map = {
        1: "待付款",
        2: "待发货",
        3: "待收货",
        4: "待评价",
        5: "已完成",
        6: "已取消"
    }
    # 获取订单状态文字
    order_state_text = order_state_map.get(order_state, "未知状态")
    return order_state_text


# 提取一个公共的函数来处理订单项
def process_order_item(order):
    # 解析 skus 数据（假设 skus 字段为 JSON 字符串）
    skus_data = parse_skus(order.skus or '[]')  # 自定义函数解析 skus
    # 获取订单状态文字
    order_state_text = mapping_order_State(order.order_state)
    # 从 order_id 获取前18位
    order_id_prefix = str(order.order_id)[:18]

    # 根据前18位 order_id 查询 member_address 表
    member_address = MemberAddress.query.filter(MemberAddress.id == order_id_prefix).first()
    full_Location = f'{member_address.fullLocation}{member_address.address}'

    # 构造单条订单数据
    order_item = {
        'receiver': member_address.receiver,
        "full_Location": full_Location,
        "id": order.order_id,  # 使用数据库中的 order_id
        "createTime": order.create_time.strftime('%Y-%m-%d %H:%M:%S') if order.create_time else "",
        "payType": order.pay_type,
        "orderState": order_state_text,
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
    return order_item