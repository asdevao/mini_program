from collections import Counter
from datetime import datetime, timedelta

from flask import Blueprint
from blueprints import db
from sqlalchemy import func

from ..Models.AddressModel import MemberAddress
from ..Models.OrderModel import Order
from ..utils.orderlist_util import process_order_item
from ..utils.response_util import ResponseUtil

bp = Blueprint('dashboard', __name__)


# 返回 growCardList 数据
@bp.route('/growcard', methods=['GET'])
def growcard():
    # 查询订单的 total_money 字段的总和
    total_money_sum = db.session.query(func.sum(Order.total_money)).scalar()
    # 保留两位小数
    total_money_sum = round(total_money_sum, 2) if total_money_sum else 0.00
    # 查询总订单数（总销量）
    total_orders_count = db.session.query(Order).count()
    uncompleted_order_count = Order.query.filter(Order.order_state == 2).count()
    completed_order_count = Order.query.filter(Order.order_state == 5).count()

    # 获取当前时间和前七天的日期
    current_time = datetime.now()
    seven_days_ago = current_time - timedelta(days=7)

    # 查询过去七天的订单的 total_money 字段的总和
    seven_days_ago_total_money_sum = db.session.query(func.sum(Order.total_money)) \
        .filter(Order.create_time >= seven_days_ago) \
        .scalar()
    seven_days_ago_total_money_sum = round(seven_days_ago_total_money_sum,
                                           2) if seven_days_ago_total_money_sum else 0.00

    # 查询过去七天的总订单数（总销量）
    seven_days_ago_total_orders_count = db.session.query(Order) \
        .filter(Order.create_time >= seven_days_ago) \
        .count()

    # 查询过去七天的待发货订单数
    seven_days_ago_uncompleted_order_count = db.session.query(Order) \
        .filter(Order.create_time >= seven_days_ago, Order.order_state == 2) \
        .count()

    # 查询过去七天的已完成订单数
    seven_days_ago_completed_order_count = db.session.query(Order) \
        .filter(Order.create_time >= seven_days_ago, Order.order_state == 5) \
        .count()

    grow_card_list = [
        {
            "title": "销量",
            "icon": "visit-count|svg",
            "value": seven_days_ago_total_orders_count,
            "total": total_orders_count,
            "color": "green",

        },
        {
            "title": "成交额",
            "icon": "total-sales|svg",
            "value": seven_days_ago_total_money_sum,
            "total": total_money_sum,
            "color": "blue",

        },
        {
            "title": "待发货数",
            "icon": "download-count|svg",
            "value": seven_days_ago_uncompleted_order_count,
            "total": uncompleted_order_count,
            "color": "orange",

        },
        {
            "title": "成交数",
            "icon": "transaction|svg",
            "value": seven_days_ago_completed_order_count,
            "total": completed_order_count,
            "color": "purple",
        }
    ]
    return ResponseUtil.success(result=grow_card_list)


@bp.route('/AnalysisArea', methods=['GET'])
def AnalysisArea():
    orders = Order.query.all()
    result = {}

    for order in orders:
        order_item = process_order_item(order)
        full_location = order_item['full_Location'].split(' ')[0]
        total_num = order_item['totalNum']
        # 如果full_Location已经在字典中，累加totalNum，否则直接赋值
        if full_location in result:
            result[full_location] += total_num  # 累加totalNum
        else:
            result[full_location] = total_num  # 如果full_Location不存在，直接存储

    # 按销量排序并取前六个地区
    top_six_regions = sorted(result.items(), key=lambda x: x[1], reverse=True)[:6]

    # 转换为所需的数据格式
    data = [{"region": region, "sales": sales} for region, sales in top_six_regions]

    return ResponseUtil.success(result=data)


@bp.route('/SalesProduct', methods=['GET'])
def SalesProduct():
    todoTasks = Order.query.filter(Order.order_state == 2).count()
    completedTasks = Order.query.filter(Order.order_state == 5).count()
    data = [{
        "name": "待发货",
        "value": todoTasks
    }, {
        "name": "已完成",
        "value": completedTasks
    }
    ]
    return ResponseUtil.success(result=data)




@bp.route('/VisitSource', methods=['GET'])
def VisitSource():
    # 获取所有 fullLocation 数据
    addresses = db.session.query(MemberAddress.fullLocation).all()

    # 使用 Python 的 Counter 来统计省份出现次数
    province_counts = Counter()

    # 遍历所有 fullLocation，进行切分，只取省份（即 fullLocation 的第一个部分）
    for address in addresses:
        if address.fullLocation:
            province = address.fullLocation.split(" ")[0]  # 取地址的第一个部分，即省份
            province_counts[province] += 1  # 计数
        # 按销量排序并取前六个地区
    top_six_regions = sorted(province_counts.items(), key=lambda x: x[1], reverse=True)[:6]
    # 将结果转换为需要的格式
    customer_source_data = [{"name": province, "value": count} for province, count in top_six_regions]
    print(customer_source_data)

    return ResponseUtil.success(result=customer_source_data)