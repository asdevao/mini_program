from blueprints import db


# 商品分类列表
class HotGoods(db.Model):
    __tablename__ = 'hot_goods'

    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 自增ID

    # 类别信息
    category_id = db.Column(db.Integer)  # 类别ID
    category_name = db.Column(db.String(255))  # 类别名称
    category_picture = db.Column(db.String(255))  # 类别图片

    # 子类别信息
    child_id = db.Column(db.Integer)  # 子类别ID
    child_name = db.Column(db.String(255))  # 子类别名称
    child_picture = db.Column(db.String(255))  # 子类别图片

    # 商品信息
    goods_id = db.Column(db.Integer)  # 商品ID
    goods_name = db.Column(db.String(255))  # 商品名称
    goods_description = db.Column(db.String(255))  # 商品描述
    goods_price = db.Column(db.Float)  # 商品价格
    goods_picture = db.Column(db.String(255))  # 商品图片
    goods_discount = db.Column(db.Float)  # 商品折扣
    goods_order_num = db.Column(db.Integer)  # 商品订单数量

    def __repr__(self):
        return f"<HotGoods {self.goods_name}>"
