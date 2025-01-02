from datetime import datetime
from blueprints import db


# 小程序用户表
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(150), unique=True, nullable=False)
    nickname = db.Column(db.String(255))  # 昵称
    name = db.Column(db.String(50), unique=True, nullable=False)
    pwd = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    createTime = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    mobile = db.Column(db.String(20), nullable=False)  # 手机号
    role_code = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)  # 部门
    dept_id = db.Column(db.Integer, nullable=False)  # 部门Id
    status = db.Column(db.SmallInteger, default='1')  # 状态 1：有效 0：无效
    remark = db.Column(db.String(50))

    def __repr__(self):
        return "<User %r>" % self.name

# 小程序用户表
class ManageUser(db.Model):
    __tablename__ = 'manage_user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(150), unique=True, nullable=False)
    nickname = db.Column(db.String(255))  # 昵称
    name = db.Column(db.String(50), unique=True, nullable=False)
    pwd = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    createTime = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    mobile = db.Column(db.String(20), nullable=False)  # 手机号
    role_code = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)  # 部门
    dept_id = db.Column(db.Integer, nullable=False)  # 部门Id
    status = db.Column(db.SmallInteger, default='1')  # 状态 1：有效 0：无效
    remark = db.Column(db.String(50))

    def __repr__(self):
        return "<User %r>" % self.name



class Role(db.Model):
    __tablename__ = 'role'  # 表名

    # 字段定义
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键，自动递增
    role_id = db.Column(db.Integer)  # 角色id
    roleName = db.Column(db.String(100))  # 角色名称
    roleValue = db.Column(db.String(100))  # 角色值
    orderNo = db.Column(db.Integer)  # 排序号
    createTime = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    remark = db.Column(db.String(255))  # 备注
    status = db.Column(db.String(1), default='1')   # 状态 1：有效 0：无效

    def __repr__(self):
        return f'<Employee {self.username}>'


class Department(db.Model):
    __tablename__ = 'department'  # 表名为 'department'

    # 字段定义
    dept_id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键，自增
    department = db.Column(db.String(100), nullable=False)  # 部门名称，不能为空
    orderNo = db.Column(db.Integer, default=0)  # 排序号，默认值为 0
    createTime = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间，默认当前时间
    remark = db.Column(db.String(255), default='')  # 备注字段，默认空字符串
    status = db.Column(db.String(1), default='1')   # 状态 1：停用 0：启用

    def __repr__(self):
        return f'<Department {self.department}>'
