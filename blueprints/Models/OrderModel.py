from blueprints import db


# 订单模型
class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 自增的主键ID
    order_id = db.Column(db.String(255), nullable=False)  # 订单ID
    create_time = db.Column(db.DateTime, nullable=False)  # 创建时间
    pay_type = db.Column(db.String(50))  # 支付方式
    order_state = db.Column(db.Integer, default=0)  # 订单状态
    pay_latest_time = db.Column(db.DateTime)  # 最晚支付时间
    countdown = db.Column(db.Integer)  # 倒计时
    post_fee = db.Column(db.Float)  # 邮费
    pay_money = db.Column(db.Float)  # 支付金额
    total_money = db.Column(db.Float)  # 总金额
    total_num = db.Column(db.Integer)  # 商品总数量
    skus = db.Column(db.Text)  # 商品 SKU
    token = db.Column(db.String(255))  # 用户 Token

    def __repr__(self):
        return f'<Order {self.order_id}>'
