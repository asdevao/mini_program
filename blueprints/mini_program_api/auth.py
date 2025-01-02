import uuid
from datetime import datetime
from flask import Blueprint, request, session, current_app
from blueprints import db
from werkzeug.security import generate_password_hash, check_password_hash

from ..Models.ProfileModel import MemberProfileData
from ..Models.UserLoginModel import UserDataWithPhoneNumber
from ..Models.UserModel import User
from ..utils.mini_program_email_util  import EmailUtilMiniProgram
from ..utils.token import Token  # 导入 Token 类
from ..utils.response_util import ResponseUtil

bp = Blueprint('auth', __name__)

DEFAULT_AVATAR_URL = "https://yjy-xiaotuxian-dev.oss-cn-beijing.aliyuncs.com/avatar/2024-05-14/a3bbc2a5-2826-4bd8-b61c-4e9e2f8cc495.jpg"


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
    nickname = data.get('displayName')
    mobile = data.get('phone')
    department = '小程序用户'
    dept_id = '0'
    role_code = data.get('role')

    # 实例化 EmailUtil类
    email_util = EmailUtilMiniProgram(current_app.extensions['mail'])

    # 校验验证码
    verify_response = email_util.validate_verification_code(email, input_code)

    # 从 Response 对象中提取 JSON 数据
    verify_result = verify_response.get_json()
    # 打印验证结果
    print('验证码校验的结果:', verify_result)
    if verify_result['code'] != 0:
        return ResponseUtil.error(verify_result['message'])

    if User.query.filter_by(name=username).first() is not None:
        return ResponseUtil.error('用户名已存在！')

    if User.query.filter_by(email=email).first() is not None:
        return ResponseUtil.error('邮箱已存在！')
        # 创建新用户实例

    new_user = User(
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
        status=1,
        remark='',
    )
    db.session.add(new_user)
    db.session.commit()

    # 注册成功后，向 UserDataWithPhoneNumber 表插入相关数据
    user_data = UserDataWithPhoneNumber(
        mobile=mobile,
        token="",  # 你可以根据需要生成或获取 token
        nickname=nickname,
        avatar=DEFAULT_AVATAR_URL,
        account=username
    )
    db.session.add(user_data)
    db.session.commit()

    # 注册成功后，向member_profile 表插入相关数据
    # 设置 birthday 为当前日期，格式化为 YYYY-MM-DD
    current_date = datetime.now().strftime('%Y-%m-%d')
    member_profile = MemberProfileData(
        nickname=nickname,
        account=username,
        avatar=DEFAULT_AVATAR_URL,
        gender=0,
        birthday=current_date,
        full_location="",
        profession="",
        token="",
    )

    db.session.add(member_profile)
    db.session.commit()

    return ResponseUtil.success('注册成功！', result={
        'userId': new_user.uuid,
        'username': new_user.name
    })


# 邮箱验证
@bp.route('/send-email', methods=['POST'])
def send_email():
    data = request.get_json()
    email = data.get('email')

    # 实例化 EmailUtil 类
    email_util = EmailUtilMiniProgram(current_app.extensions['mail'])

    # 发送验证码
    result = email_util.send_verification_code(email)

    # 从 Response 对象中提取 JSON 数据
    result_json = result.get_json()

    if result_json['code'] == 0:
        return ResponseUtil.success('验证码发送成功！')
    else:
        return ResponseUtil.error(result_json['message'])


# 登录
@bp.route('/login', methods=['GET', 'POST'])
def login():
    data = request.get_json()
    print('登陆信息', data)
    username = data['username']
    password = data['password']
    mini_programs = data.get('mini_program', '')
    user = User.query.filter_by(name=username).first()
    if user is None or not check_password_hash(user.pwd, password):
        return ResponseUtil.error('用户名或密码错误！')

    else:
        token = Token.generate_token(str(user.uuid))
        session['username'] = user.name
        session['role_code'] = user.role_code
        session['uuid'] = str(user.uuid)
        if mini_programs:
            # 在 UserDataWithPhoneNumber 表中根据 username 更新对应用户的 token
            user_data = UserDataWithPhoneNumber.query.filter_by(account=username).first()
            if user_data:
                user_data.token = token
                db.session.commit()  # 提交更新到数据库
                # 在 member_profile 表中根据 username 或其他标识更新对应用户的 token
            member_profile = MemberProfileData.query.filter_by(account=username).first()  # 假设 account 字段表示用户名
            if member_profile:
                member_profile.token = token
                db.session.commit()  # 提交更新到数据库
            return ResponseUtil.success(result={
                'account': user_data.account,
                'avatar': user_data.avatar,
                'id': user_data.id,
                'mobile': user_data.mobile,
                'nickname': user_data.nickname,
                'token': token,

            })
        else:
            return ResponseUtil.success(result={
                'userId': user.uuid,
                'username': user.name,
                'token': token,
                'realName': ''
            })


# 获取用户信息
@bp.route('/user/info', methods=['GET', 'POST'])
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

    user_data = UserDataWithPhoneNumber.query.filter_by(token=token).first()
    if user_data:
        user = User.query.filter_by(mobile=user_data.mobile).first()
        return get_user_info(user)
    else:
        return ResponseUtil.error('用户数据未找到', code=404)

    return ResponseUtil.error('token鉴权失败', code=401)
