from blueprints import db
from datetime import datetime


# 首页-广告区域-小程序 轮播图
class BannerData(db.Model):
    __tablename__ = 'banner'  # 数据库表名

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Banner的唯一ID
    imgUrl = db.Column(db.String(255), nullable=False)  # Banner图片URL
    hrefUrl = db.Column(db.String(255), nullable=False)  # Banner点击跳转的URL
    type = db.Column(db.String(50), nullable=False)  # Banner的类型（例如：广告、活动等）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间

    def __repr__(self):
        return f'<BannerData {self.id} - {self.type}>'


# 首页-前台分类-小程序
class MutliData(db.Model):
    __tablename__ = 'mutli_data'  # 数据库表名

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)  # 使用Excel中的id作为主键
    name = db.Column(db.String(255), nullable=False)  # 名称
    icon = db.Column(db.String(255), nullable=True)  # 图标URL（可为空）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间

    def __repr__(self):
        return f'<MutliData {self.id} - {self.name}>'


# 首页-热门推荐-小程序
class HotMutliData(db.Model):
    __tablename__ = 'hot_mutli_data'  # 数据库表名

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键ID
    pictures = db.Column(db.String(255), nullable=False)  # 图片链接
    title = db.Column(db.String(255), nullable=False)  # 标题
    alt = db.Column(db.String(255), nullable=True)  # 替代文本
    target = db.Column(db.String(255), nullable=False)  # 目标链接
    type = db.Column(db.String(50), nullable=False)  # 类型
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间


# 首页-新鲜好物-小程序
class NewData(db.Model):
    __tablename__ = 'new_data'  # 数据库表名

    id = db.Column(db.Integer, primary_key=True)  # 唯一的主键ID（直接使用Excel中的id）
    name = db.Column(db.String(255), nullable=False)  # 商品名称
    desc = db.Column(db.Text, nullable=True)  # 商品描述
    price = db.Column(db.Numeric(10, 2), nullable=False)  # 商品价格
    picture = db.Column(db.String(255), nullable=True)  # 商品图片URL
    order_num = db.Column(db.Integer, nullable=False)  # 商品的订单数量
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间

    def __repr__(self):
        return f'<NewData {self.id} - {self.name}>'


# 猜你喜欢-小程序
class GuessLikeData(db.Model):
    __tablename__ = 'guess_like_data'  # 数据库表名

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 唯一的主键ID
    counts = db.Column(db.Integer, nullable=False)  # 记录总数
    page_size = db.Column(db.Integer, nullable=False)  # 每页条数
    pages = db.Column(db.Integer, nullable=False)  # 总页数
    page = db.Column(db.Integer, nullable=False)  # 当前页码
    items = db.Column(db.JSON, nullable=False)  # 商品数据，存储为JSON格式
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间

    def __repr__(self):
        return f'<GuessLikeData {self.id} - {self.page}>'


class VideoGroup(db.Model):
    __tablename__ = 'video_groups'  # 视频组表名

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 视频组唯一标识
    title = db.Column(db.String(255), nullable=False)  # 视频组标题
    videos = db.relationship('Video', backref='group', lazy=True)  # 定义与 Video 之间的关系

    def __repr__(self):
        return f'<VideoGroup {self.title}>'


class Video(db.Model):
    __tablename__ = 'videos'  # 视频表名

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 视频唯一标识
    title = db.Column(db.String(255), nullable=False)  # 视频标题
    url = db.Column(db.String(255), nullable=False)  # 视频链接
    group_id = db.Column(db.Integer, db.ForeignKey('video_groups.id'), nullable=False)  # 外键，关联到 VideoGroup

    def __repr__(self):
        return f'<Video {self.title}>'
