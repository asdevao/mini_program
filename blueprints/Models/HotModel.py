from blueprints import db


# 热门推荐-特惠推荐-小程序
class HotPreference(db.Model):
    __tablename__ = 'hot_mutil'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 自增的主键ID
    activity_id = db.Column(db.Integer)  # 活动ID
    title = db.Column(db.String(255))  # 活动标题
    banner_picture = db.Column(db.String(255))  # 活动图片
    sub_id = db.Column(db.Integer)  # 子类ID
    sub_title = db.Column(db.String(255))  # 子类标题
    goods_id = db.Column(db.Integer)  # 商品ID
    goods_name = db.Column(db.String(255))  # 商品名称
    goods_desc = db.Column(db.String(255))  # 商品描述
    goods_price = db.Column(db.Float)  # 商品价格
    goods_picture = db.Column(db.String(255))  # 商品图片
    order_num = db.Column(db.Integer)  # 订单数量
    pages = db.Column(db.String(255))  # 总页数
    page = db.Column(db.String(255))  # 当前页码

    def __repr__(self):
        return f'<HotMutil {self.title}>'


# 热门推荐-爆款推荐 - 小程序
class HotInVogue(db.Model):
    __tablename__ = 'hot_inVogue'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 自增的主键ID
    activity_id = db.Column(db.Integer)  # 活动ID
    title = db.Column(db.String(255))  # 活动标题
    banner_picture = db.Column(db.String(255))  # 活动图片
    sub_id = db.Column(db.Integer)  # 子类ID
    sub_title = db.Column(db.String(255))  # 子类标题
    goods_id = db.Column(db.Integer)  # 商品ID
    goods_name = db.Column(db.String(255))  # 商品名称
    goods_desc = db.Column(db.String(255))  # 商品描述
    goods_price = db.Column(db.Float)  # 商品价格
    goods_picture = db.Column(db.String(255))  # 商品图片
    order_num = db.Column(db.Integer)  # 订单数量
    pages = db.Column(db.String(255))  # 总页数
    page = db.Column(db.String(255))  # 当前页码

    def __repr__(self):
        return f'<HotInVogue {self.title}>'


# 热门推荐-一站买全-小程序
class HotOneStop(db.Model):
    __tablename__ = 'hot_oneStop'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 自增的主键ID
    activity_id = db.Column(db.Integer)  # 活动ID
    title = db.Column(db.String(255))  # 活动标题
    banner_picture = db.Column(db.String(255))  # 活动图片
    sub_id = db.Column(db.Integer)  # 子类ID
    sub_title = db.Column(db.String(255))  # 子类标题
    goods_id = db.Column(db.Integer)  # 商品ID
    goods_name = db.Column(db.String(255))  # 商品名称
    goods_desc = db.Column(db.String(255))  # 商品描述
    goods_price = db.Column(db.Float)  # 商品价格
    goods_picture = db.Column(db.String(255))  # 商品图片
    order_num = db.Column(db.Integer)  # 订单数量
    pages = db.Column(db.String(255))  # 总页数
    page = db.Column(db.String(255))  # 当前页码

    def __repr__(self):
        return f'<HotOneStop {self.title}>'


#  热门推荐-新鲜好物-小程序
class HotNew(db.Model):
    __tablename__ = 'hot_new'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 自增的主键ID
    activity_id = db.Column(db.Integer)  # 活动ID
    title = db.Column(db.String(255))  # 活动标题
    banner_picture = db.Column(db.String(255))  # 活动图片
    sub_id = db.Column(db.Integer)  # 子类ID
    sub_title = db.Column(db.String(255))  # 子类标题
    goods_id = db.Column(db.Integer)  # 商品ID
    goods_name = db.Column(db.String(255))  # 商品名称
    goods_desc = db.Column(db.String(255))  # 商品描述
    goods_price = db.Column(db.Float)  # 商品价格
    goods_picture = db.Column(db.String(255))  # 商品图片
    order_num = db.Column(db.Integer)  # 订单数量
    pages = db.Column(db.String(255))  # 总页数
    page = db.Column(db.String(255))  # 当前页码

    def __repr__(self):
        return f'<HotNew {self.title}>'
