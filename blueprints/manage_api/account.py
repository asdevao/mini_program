import re
import uuid
from flask import Blueprint, request, session
from blueprints import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from ..Models.UserModel import ManageUser, Role, Department
from ..utils.manage_account_util import get_account_list, get_role_list, get_dept_list
from ..utils.response_util import ResponseUtil

bp = Blueprint('account', __name__)


# 账号管理-获取所有账号数据
@bp.route('/getAccountList', methods=['GET'])
def getAccountList():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 10))
    searchInfo = request.args.get('searchInfo', '').strip()
    account = request.args.get('account', '').strip()
    nickname = request.args.get('nickname', '').strip()
    dept_id = request.args.get('deptId', '').strip()
    result, total = get_account_list(page, page_size, account, nickname, dept_id, searchInfo)
    account_list = {
        'items': result,
        'total': total,
        'pae': page,
        'pageSize': page_size
    }
    return ResponseUtil.success('获取成功！', result=account_list)


# 账号管理-检测用户合法性
@bp.route('/accountExist', methods=['POST'])
def accountExist():
    data = request.json
    username = data.get('acount')
    result = {"username": username}
    return ResponseUtil.success('获取成功！', result=result)


# 账号管理-创建账号
@bp.route('/createAccount', methods=['POST'])
def createAccount():
    data = request.json
    username = session.get('username')
    role = ManageUser.query.filter_by(name=username).first().role_code
    if role != 'admin':
        return ResponseUtil.error(message='权限不足，无法操作')
    role_id = int(data.get('role'))  # 转换为整数
    roleName = Role.query.filter_by(roleValue=role_id).first().roleName
    if not all(i in data for i in ['account', 'nickname', 'email', 'role', 'dept']):
        return ResponseUtil.error(message='缺少必要的参数')
    matching_dept = Department.query.filter_by(dept_id=data['dept']).first()

    # 校验用户名长度
    if len(data['account']) < 3:
        return ResponseUtil.error(message='用户名长度必须大于等于3位')
    # 校验用户名和邮箱的唯一性
    if ManageUser.query.filter_by(name=data['account']).first():
        return ResponseUtil.error(message='用户名已存在')
    if ManageUser.query.filter_by(email=data['email']).first():
        return ResponseUtil.error(message='邮箱已被使用')
    # 创建新的用户对象
    new_account = ManageUser(
        uuid=str(uuid.uuid4()),
        nickname=data['nickname'],
        name=data['account'],
        pwd=generate_password_hash('a123456'),
        email=data['email'],
        createTime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        mobile='',
        role_code=roleName,
        dept_id=data['dept'],
        department=matching_dept.department,
        status=0, # 初始为不能使用的状态
        remark=data['remark'],

    )
    db.session.add(new_account)
    db.session.commit()
    return ResponseUtil.success({'message': '创建成功', 'id': new_account.id})


# 用户管理-更新账号信息
@bp.route('/updateAccount/<id>', methods=['POST'])
def updateAccount(id):
    data = request.json
    # 获取当前账号的用户名
    current_username = session.get('username')
    current_role = ManageUser.query.filter_by(name=current_username).first().role_code
    if current_role != 'admin':
        return ResponseUtil.error(message='权限不足，无法操作！')
    account = ManageUser.query.get(id)
    if not account:
        return ResponseUtil.error(message='账号不存在！')
    if 'nickname' in data:
        account.nickname = data['nickname']
    if 'email' in data:
        email = data['email']
        if ManageUser.query.filter(ManageUser.email == email, ManageUser.id != id).first():
            return ResponseUtil.error(message='邮箱已被使用')
        account.email = email
    if 'role' in data:
        account.role_code = data['role']
    if 'dept' in data:
        # 查找匹配的部门,dept是 dept_id
        matching_dept = Department.query.filter_by(dept_id=data['dept']).first()
        if matching_dept is None:
            return ResponseUtil.error(message='请选择部门')
        account.dept_id = data['dept']
        account.department = matching_dept.department
    if 'account' in data:
        # 检查用户名长度
        if len(data['account']) < 3:
            return ResponseUtil.error(message='用户名长度必须大于等于3位')
        if ManageUser.query.filter(ManageUser.name == data['account'], ManageUser.id != id).first():
            return ResponseUtil.error(message='用户名已存在')
        account.account = data['account']
    if 'remark' in data:
        account.remark = data['remark']
    if 'status' in data:
        account.status = data['status']  # 0:不可用, 1:可用
    db.session.commit()
    return ResponseUtil.success('修改成功')


# 用户管理-删除账号信息
@bp.route('/deleteAccount/<id>', methods=['DELETE'])
def deleteAccount(id):
    username = session.get('username')
    role = ManageUser.query.filter_by(name=username).first().role_code
    if role != 'admin':
        return ResponseUtil.error(message='权限不足，无法操作')
    account = ManageUser.query.get(id)
    # 删除该账户
    db.session.delete(account)
    db.session.commit()
    return ResponseUtil.success('删除成功')


# 用户管理-用户详情页
@bp.route('/selectMoreAccount/<id>', methods=['GET'])
def selectMoreAccount(id):
    # 查询目标用户信息
    target_user = ManageUser.query.filter_by(id=id).first()
    if not target_user:
        return ResponseUtil.error(message='目标用户不存在')

    # 构造返回数据
    user_data = {
        "id": target_user.id,
        "name": target_user.name,
        "nickname": target_user.nickname,
        "email": target_user.email,
        "mobile": target_user.mobile,
        "role": target_user.role_code,
        "dept": target_user.dept_id,
        "dept_id": target_user.dept_id,
        "department": target_user.department,  # 假设 department 字段存储部门名称
        "createTime": target_user.createTime,
        "remark": target_user.remark,
        'status': target_user.status
    }

    # 返回用户详情
    return ResponseUtil.success(result=user_data)


@bp.route('/setAccountStatus', methods=['POST'])
def setAccountStatus():
    username = session.get('username')
    role = ManageUser.query.filter_by(name=username).first().role_code
    if role != 'admin':
        return ResponseUtil.error(message='权限不足，无法操作')
    # 获取前端传递的数据
    data = request.get_json()
    user_id = data.get('id')  # 用户ID
    print(user_id)
    status = data.get('status')  # 账号状态，'0'表示禁用，'1'表示启用

    # 查找用户
    user = ManageUser.query.filter_by(id=user_id).first()
    # 更新账号状态
    user.status = status

    # 提交到数据库
    db.session.commit()

    return ResponseUtil.success('修改成功')


# 角色管理-获取所有角色信息
@bp.route('/getAllRoleList', methods=['GET'])
def getAllRoleList():
    query = Role.query
    roles = query.all()
    all_role_list = [
        {
            'id': role.role_id,
            'roleName': role.roleName,
            'roleValue': role.roleValue,
            'orderNo': role.orderNo,
            'status': role.status,
            'createTime': role.createTime.strftime("%Y-%m-%d"),
            'remark': role.remark,
        }
        for role in roles
    ]
    return ResponseUtil.success('获取成功！', result=all_role_list)


# 角色管理-获取角色列表
@bp.route('/getRoleListByPage', methods=['GET'])
def getRoleListByPage():
    # 分页参数
    page = int(request.args.get('page', 1))
    pageSize = int(request.args.get('pageSize', 10))
    # 搜索参数
    roleName = request.args.get('roleName', '').strip()
    stauts = request.args.get('status', '').strip()
    result, total = get_role_list(page, pageSize, roleName, stauts)
    role_list = {
        'items': result,
        'total': total,
        'pae': page,
        'pageSize': pageSize,
    }
    print(role_list)
    return ResponseUtil.success(result=role_list)


# 角色管理-设置角色状态
@bp.route('/setRoleStatus', methods=['POST'])
def setRoleStatus():
    username = session.get('username')
    role = ManageUser.query.filter_by(name=username).first().role_code
    if role != 'admin':
        return ResponseUtil.error(message='权限不足，无法操作')
    # 获取前端数据
    data = request.json
    id = data.get('id')
    status = data.get('status')
    print(id, status)
    role = Role.query.filter_by(id=id).first()
    role.status = status
    db.session.commit()
    return ResponseUtil.success('修改成功')


# 角色管理-创建角色信息
@bp.route('/createRole', methods=['POST'])
def createRole():
    data = request.json
    username = session.get('username')
    roleName = data.get('roleName')
    roleValue = data.get('roleValue')
    status = data.get('status')
    remark = data.get('remark', '')

    role = ManageUser.query.filter_by(name=username).first().role_code
    if role != 'admin':
        return ResponseUtil.error(message='权限不足，无法操作')
        # 查询当前数据库中最大的 orderNo 值
    max_order_no = db.session.query(db.func.max(Role.orderNo)).scalar()
    orderNo = (max_order_no or 0) + 1  # 如果数据库中没有记录，则从 1 开始
    max_Role_id = db.session.query(db.func.max(Role.role_id)).scalar()
    role_id = (max_Role_id or 0) + 1  # 如果数据库中没有记录，则从 1 开始
    new_role = Role(
        role_id=role_id,
        roleName=roleName,
        roleValue=roleValue,
        orderNo=orderNo,
        status=status,
        remark=remark,
    )
    db.session.add(new_role)
    db.session.commit()
    return ResponseUtil.success({'message': '创建成功', 'id': new_role.id})


# 角色管理—更新角色信息
@bp.route('/updateRole/<id>', methods=['POST'])
def updateRole(id):
    data = request.json
    # 获取当前账号的用户名
    current_username = session.get('username')
    current_role = ManageUser.query.filter_by(name=current_username).first().role_code
    if current_role != 'admin':
        return ResponseUtil.error(message='权限不足，无法操作！')
    role = Role.query.get(id)
    if not role:
        return ResponseUtil.error(message='部门不存在！')
    if 'roleName' in data:
        role.roleName = data['roleName']
    if 'roleValue' in data:
        role.roleValue = data['roleValue']
    if 'status' in data:
        role.status = data['status']
    if 'remark' in data:
        role.remark = data['remark']
    db.session.commit()
    return ResponseUtil.success('修改成功')


# 角色管理-删除角色信息
@bp.route('/deleteRole/<id>', methods=['DELETE'])
def deleteRole(id):
    username = session.get('username')
    role = ManageUser.query.filter_by(name=username).first().role_code
    if role != 'admin':
        return ResponseUtil.error(message='权限不足，无法操作')
    role = Role.query.get(id)
    # 删除该账户
    db.session.delete(role)
    db.session.commit()
    return ResponseUtil.success('删除成功')


# 部门管理-获取所有部门信息
@bp.route('/getDeptList', methods=['GET'])
def getDeptList():
    deptName = request.args.get('deptName', '').strip()
    status = request.args.get('status', '').strip()
    result = get_dept_list(deptName, status)

    return ResponseUtil.success(result=result)


# 部门管理-创建部门信息
@bp.route('/createDepartment', methods=['POST'])
def createDepartment():
    data = request.json
    username = session.get('username')
    departmentName = data.get('deptName')
    orderNo = data.get('orderNo')
    status = data.get('status')
    remark = data.get('remark', '')

    role = ManageUser.query.filter_by(name=username).first().role_code
    if role != 'admin':
        return ResponseUtil.error(message='权限不足，无法操作')
    new_department = Department(
        department=departmentName,
        orderNo=orderNo,
        status=status,
        remark=remark,
    )
    db.session.add(new_department)
    db.session.commit()
    return ResponseUtil.success({'message': '创建成功', 'id': new_department.dept_id})


# 部门管理—更新部门信息
@bp.route('/updateDepartment/<id>', methods=['POST'])
def updateDepartment(id):
    data = request.json
    # 获取当前账号的用户名
    current_username = session.get('username')
    current_role = ManageUser.query.filter_by(name=current_username).first().role_code
    if current_role != 'admin':
        return ResponseUtil.error(message='权限不足，无法操作！')
    dep = Department.query.get(id)
    if not dep:
        return ResponseUtil.error(message='部门不存在！')
    if 'deptName' in data:
        dep.department = data['deptName']
    if 'orderNo' in data:
        dep.orderNo = data['orderNo']
    if 'status' in data:
        dep.status = data['status']
    if 'remark' in data:
        dep.remark = data['remark']
    db.session.commit()
    return ResponseUtil.success('修改成功')


# 用户管理-删除部门信息
@bp.route('/deleteDepartment/<id>', methods=['DELETE'])
def deleteDepartment(id):
    dep = Department.query.get(id)
    # 删除该账户
    db.session.delete(dep)
    db.session.commit()
    return ResponseUtil.success('删除成功')


# 密码修改
@bp.route('/changepassword', methods=['POST'])
def changepassword():
    try:
        # 获取请求数据
        data = request.json
        if not data:
            return ResponseUtil.error('请求数据为空', 400)

        # 从 session 获取当前登录用户
        current_username = session.get('username')

        # 查询用户信息
        user = ManageUser.query.filter_by(name=current_username).first()
        if not user:
            return ResponseUtil.error('用户不存在', 404)

        # 验证旧密码
        current_pwd = user.pwd
        passwordOld = data.get('passwordOld')

        if not passwordOld:
            return ResponseUtil.error('缺少旧密码字段', 400)

        if not check_password_hash(current_pwd, passwordOld):
            return ResponseUtil.error('旧密码错误', 400)

        # 更新新密码
        passwordNew = data.get('passwordNew')
        if not passwordNew:
            return ResponseUtil.error('缺少新密码字段', 400)
        # 校验新密码必须包含字母和数字
        if not re.match(r'^(?=.*[a-zA-Z])(?=.*\d)[A-Za-z\d]{6,}$', passwordNew):
            return ResponseUtil.error('新密码必须包含字母和数字，并且长度至少为6个字符', 400)
        user.pwd = generate_password_hash(passwordNew)

        # 提交更改到数据库
        db.session.commit()

        return ResponseUtil.success('密码修改成功')

    except Exception as e:
        # 捕获异常，返回错误响应
        return ResponseUtil.error(f'内部服务器错误: {str(e)}', 500)


