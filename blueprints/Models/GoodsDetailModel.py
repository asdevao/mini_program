from blueprints import db
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime


# 商品详情
class GoodsDetail(db.Model):
    __tablename__ = 'goods_detail'

    # 主键
    id = db.Column(db.String(255), primary_key=True)
    # 商品基本信息
    name = db.Column(db.String(255), nullable=False)  # 商品名称
    spuCode = db.Column(db.String(255), nullable=False)  # 商品SPU编码
    desc = db.Column(db.Text)  # 商品描述
    price = db.Column(db.Numeric(10, 2), nullable=False)  # 当前价格
    oldPrice = db.Column(db.Numeric(10, 2))  # 原价
    discount = db.Column(db.Float)  # 折扣，默认为 0
    inventory = db.Column(db.Integer, nullable=False)  # 库存数量
    # 商品品牌信息
    brand = db.Column(JSON)  # 品牌信息，JSON 格式

    # 销量、评论、收藏等
    salesCount = db.Column(db.Integer, default=0)  # 销量
    commentCount = db.Column(db.Integer, default=0)  # 评论数量
    collectCount = db.Column(db.Integer, default=0)  # 收藏数量

    # 视频比例
    videoScale = db.Column(db.Numeric(5, 2), default=0)  # 视频比例（视频数量 / 图片数量）

    # 商品图片和视频
    mainPictures = db.Column(JSON)  # 主图，JSON 格式
    mainVideos = db.Column(JSON)  # 主视频，JSON 格式

    # 商品分类信息
    categories = db.Column(JSON)  # 商品分类，JSON 格式（包含分类ID、名称等）

    # 是否预售
    isPreSale = db.Column(db.Boolean, default=False)  # 是否预售，默认值为 False

    # 详细图片和属性
    detailsPictures = db.Column(JSON)  # 详细图片，JSON 格式
    detailProperties = db.Column(JSON)  # 详细属性，JSON 格式

    # 商品规格和SKU
    specs = db.Column(JSON)  # 商品规格，JSON 格式
    skus = db.Column(JSON)  # 商品的 SKU 集合，JSON 格式

    # 同类商品和热销商品
    similarProducts = db.Column(JSON)  # 同类商品，JSON 格式
    hotByDay = db.Column(JSON)  # 24小时热销商品，JSON 格式
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 商品创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)  # 商品更新时间

    def __repr__(self):
        return f"<GoodsDetail {self.name}>"
