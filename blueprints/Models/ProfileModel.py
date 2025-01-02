from blueprints import db


# 会员个人信息
class MemberProfileData(db.Model):
    __tablename__ = 'member_profiles'  # 数据库表名

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 会员ID
    nickname = db.Column(db.String(255), nullable=False)  # 昵称
    account = db.Column(db.String(255), nullable=False)  # 账户名
    avatar = db.Column(db.String(255))  # 头像URL
    gender = db.Column(db.String(10))  # 性别（例如 '男' 或 '女'）
    birthday = db.Column(db.Date)  # 生日
    full_location = db.Column(db.String(255))  # 完整地址
    profession = db.Column(db.String(255))  # 职业
    token = db.Column(db.String(255))  # 用户token

    def __repr__(self):
        return f'<MemberProfileData {self.id} - {self.nickname}>'


