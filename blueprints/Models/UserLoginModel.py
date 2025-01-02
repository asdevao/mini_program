from blueprints import db


# 用户数据表模型
class UserDataWithPhoneNumber(db.Model):
    __tablename__ = 'user_data_with_phone_number'  # 数据库表名

    id = db.Column(db.Integer, primary_key=True)  # 用户ID
    mobile = db.Column(db.String(20), nullable=False)  # 手机号
    token = db.Column(db.String(255))  # 用户token
    nickname = db.Column(db.String(255))  # 昵称
    avatar = db.Column(db.String(255))  # 头像URL
    account = db.Column(db.String(255))  # 账户名

    def __repr__(self):
        return f'<UserDataWithPhoneNumber {self.id} - {self.nickname}>'