import random
import uuid
from datetime import datetime
from flask import Blueprint, request, session, current_app
from blueprints import db
from werkzeug.security import generate_password_hash, check_password_hash
from ..Models.UserModel import ManageUser
from ..utils.email_util import EmailUtil
from ..utils.token import Token  # 导入 Token 类
from ..utils.response_util import ResponseUtil

bp = Blueprint('manage_auth', __name__)


# 注册
@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    print('注册信息', data)

    # 获取用户数据
    username = data.get('username') if data.get('username') else data.get('account')
    password = data.get('password')
    email = data.get('email')
    input_code = data.get('emailCode')  # 获取用户输入的验证码

    # 生成一个 6 位的随机数字
    random_number = random.randint(100000, 999999)
    nickname, mobile, department, dept_id, role_code = f"云上用户{random_number}", '', '', 0, 'admin'

    # 实例化 EmailUtil类
    email_util = EmailUtil(current_app.extensions['mail'])

    # 校验验证码
    verify_response = email_util.validate_verification_code(email, input_code)

    # 从 Response 对象中提取 JSON 数据
    verify_result = verify_response.get_json()
    if verify_result['code'] != 0:
        return ResponseUtil.error(verify_result['message'])

    if ManageUser.query.filter_by(name=username).first() is not None:
        return ResponseUtil.error('用户名已存在！')

    if ManageUser.query.filter_by(email=email).first() is not None:
        return ResponseUtil.error('邮箱已存在！')
        # 创建新用户实例

    new_user = ManageUser(
        uuid=str(uuid.uuid4()),
        nickname=nickname,
        name=username,
        pwd=generate_password_hash(password),
        email=email,
        createTime=datetime.utcnow(),
        mobile=mobile,
        role_code=role_code,
        department=department,
        dept_id=dept_id,
        status=0,
        remark='',
    )
    db.session.add(new_user)
    db.session.commit()

    return ResponseUtil.success('注册成功！', result={
        'userId': new_user.uuid,
        'username': new_user.name
    })


# 登录
@bp.route('/login', methods=['GET', 'POST'])
def login():
    data = request.get_json()
    print('登陆信息', data)
    username = data['username']
    password = data['password']
    user = ManageUser.query.filter_by(name=username).first()
    if user is None or not check_password_hash(user.pwd, password):
        return ResponseUtil.error('用户名或密码错误！')
        # 检查用户状态是否为0，表示尚未激活
    if user.status == 0:
        return ResponseUtil.error('当前账号尚未激活，请联系管理员！')

    else:
        token = Token.generate_token(str(user.uuid))
        session['username'] = user.name
        session['role_code'] = user.role_code
        session['uuid'] = str(user.uuid)

        return ResponseUtil.success(result={
            'userId': user.uuid,
            'username': user.name,
            'token': token,
            'realName': ''
        })


# 获取用户信息
@bp.route('/user/info', methods=['GET'])
def getUserInfo():
    token = request.headers.get('Authorization')
    if not token:
        return ResponseUtil.error('未提供 token', code=401)

    # 获取用户信息的公共部分
    def get_user_info(user):
        return ResponseUtil.success(result={
            'roles': user.role_code,
            'userId': user.uuid,
            'username': user.name,
            'realName': user.name,
            'avatar': '',
            'desc': ''
        })

    # 非小程序请求，按 session 获取用户
    if Token.certify_token(session.get('uuid'), token):
        user = ManageUser.query.filter_by(name=session.get('username')).first()
        return get_user_info(user)

    return ResponseUtil.error('token鉴权失败', code=401)


# 获取用户详细信息
@bp.route('/getUserData', methods=['GET'])
def getUserData():
    token = request.headers.get('Authorization')
    if not token:
        return ResponseUtil.error('未提供 token', code=401)

    # 校验token并获取用户信息
    if Token.certify_token(session.get('uuid'), token):
        user = ManageUser.query.filter_by(uuid=session.get('uuid')).first()  # 使用uuid获取用户
        if user is None:
            return ResponseUtil.error('用户不存在', code=404)

        # 返回用户的基本信息
        return ResponseUtil.success(result={
            'username': user.name,
            'nickname': user.nickname or '',  # 如果没有昵称，返回空字符串
            'email': user.email or '',  # 如果没有邮箱，返回空字符串
            'phone': user.mobile or '',  # 如果没有电话，返回空字符串
        })

    return ResponseUtil.error('token鉴权失败', code=401)


# 修改用户信息
@bp.route('/changeUser', methods=['POST'])
def updateUser():
    token = request.headers.get('Authorization')
    if not token:
        return ResponseUtil.error('未提供 token', code=401)

    # 校验 token 并获取用户信息
    if Token.certify_token(session.get('uuid'), token):
        user = ManageUser.query.filter_by(uuid=session.get('uuid')).first()
        if user is None:
            return ResponseUtil.error('用户不存在', code=404)

        # 获取前端传递的数据
        data = request.get_json()

        # 获取要更新的字段
        nickname = data.get('nickname')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')

        # 更新用户信息
        if nickname:
            user.nickname = nickname
        if email:
            user.email = email
        if phone:
            user.mobile = phone
        if password:
            user.pwd = generate_password_hash(password)  # 密码加密处理

        # 提交到数据库
        db.session.commit()

        return ResponseUtil.success('修改成功！', result={
            'nickname': user.nickname,
            'email': user.email,
            'phone': user.mobile,
        })

    return ResponseUtil.error('token鉴权失败', code=401)
