from flask import Blueprint, session
from ..Models.OrderModel import Order
from ..utils.response_util import ResponseUtil
from ..Models.UserModel import ManageUser

bp = Blueprint('workbeach', __name__)


@bp.route('/', methods=['GET'])
def getWorkBeachData():
    # 使用filter_by来筛选name匹配且department不等于“小程序用户”
    order_count = Order.query.count()
    user_count = ManageUser.query.count()
    # 查询Order表中orderstate为2的数据并计数
    uncompleted_order_count = Order.query.filter(Order.order_state == 2).count()
    # 构造返回的数据
    data = {
        'order_count': order_count,
        'user_count': user_count,
        'uncompleted_order_count': uncompleted_order_count
    }
    return ResponseUtil.success(result=data)
