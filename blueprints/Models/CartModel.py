from blueprints import db


# 购物车列表
class CartData(db.Model):
    __tablename__ = 'cart'  # 数据库表名

    id = db.Column(db.Integer, primary_key=True)  # 购物车项唯一ID
    name = db.Column(db.String(255), nullable=False)  # 商品名称
    picture = db.Column(db.String(255))  # 商品图片URL
    price = db.Column(db.Numeric(10, 2))  # 商品原价
    count = db.Column(db.Integer, nullable=False)  # 商品数量
    sku_id = db.Column(db.String(50))  # SKU ID
    attributes_text = db.Column(db.String(255))  # 商品属性
    selected = db.Column(db.Boolean, default=True)  # 是否选中（默认为True）
    current_price = db.Column(db.Numeric(10, 2))  # 当前价格（可能有折扣）
    stock = db.Column(db.Integer)  # 商品库存
    is_collected = db.Column(db.Boolean, default=False)  # 是否已收藏
    discount = db.Column(db.Numeric(5, 2))  # 商品折扣
    is_effective = db.Column(db.Boolean, default=True)  # 是否有效（例如，是否过期）
    token = db.Column(db.String(255))  # 用户token

    def __repr__(self):
        return f'<CartData {self.id} - {self.name}>'
