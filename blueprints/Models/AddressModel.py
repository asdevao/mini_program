from blueprints import db
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime


# 会员地址管理
class MemberAddress(db.Model):
    __tablename__ = 'member_addresses'

    # 主键
    id = db.Column(db.String(255), primary_key=True)  # 地址ID，自增
    # 收货人信息
    receiver = db.Column(db.String(255), nullable=False)  # 收货人姓名
    contact = db.Column(db.String(50), nullable=False)  # 联系方式（手机号等）
    # 地址编码
    provinceCode = db.Column(db.String(20), nullable=False)  # 省级编码
    cityCode = db.Column(db.String(20), nullable=False)  # 市级编码
    countyCode = db.Column(db.String(20), nullable=False)  # 县/区级编码
    # 详细地址
    address = db.Column(db.String(255), nullable=False)  # 详细地址
    isDefault = db.Column(db.Boolean, default=False)  # 是否默认地址，默认为 False
    # 地址的完整位置（可以存储完整的省市区地址信息）
    fullLocation = db.Column(db.String(255))  # 完整的地址（省市区等拼接
    # 邮政编码
    postalCode = db.Column(db.String(20))  # 邮政编码
    # 地址标签（可以是多个标签，存储为 JSON 格式）
    addressTags = db.Column(JSON)  # 地址标签，存储为 JSON 格式
    # 用户 token（如果有的话）
    token = db.Column(db.String(255))  # 用户 token，用于标识唯一用户
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间

    def __repr__(self):
        return f"<MemberAddress {self.receiver}, {self.address}>"
