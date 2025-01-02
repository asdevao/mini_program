from ..Models.UserModel import ManageUser, Role, Department


def get_account_list(page, page_size, account, nickname, dept_id, searchInfo):
    query = ManageUser.query
    # 构建查询
    if account:
        query = query.filter(ManageUser.name.like(f'%{account}%'))
    if nickname:
        query = query.filter(ManageUser.nickname.like(f'%{nickname}%'))
    if dept_id:
        query = query.filter(ManageUser.dept_id == dept_id)  # 使用 `==` 而不是 `like`
    if searchInfo:
        query = query.filter(ManageUser.dept == searchInfo)  # 这里 `searchInfo` 应该和 `User.dept` 数据类型匹配

    # 获取分页结果
    total = query.count()
    users = query.offset((page - 1) * page_size).limit(page_size).all()

    # 结果返回转换为JSON
    result = [
        {
            'id': user.id,
            'account': user.name,
            'nickname': user.nickname,
            'email': user.email,
            'role': user.role_code,
            'createTime': user.createTime.strftime("%Y-%m-%d %H:%M:%S"),
            'remark': user.remark,
            'status': user.status,
            'dept': user.department,
        }
        for user in users  # 修正拼写错误
    ]

    return result, total


def get_role_list(page, pageSize, roleName, status):
    query = Role.query
    if roleName:
        query = query.filter(Role.roleName.like(f'%{roleName}%'))
    if status:
        query = query.filter(Role.status.like(f'%{status}%'))
    total = query.count()
    users = query.offset((page - 1) * pageSize).limit(pageSize).all()
    result = [
        {
            'id': user.id,
            'roleName': user.roleName,
            'roleValue': user.roleValue,
            'orderNo': user.orderNo,
            'status': user.status,
            'createTime': user.createTime.strftime("%Y-%m-%d %H:%M:%S"),
            'remark': user.remark,

        }
        for user in users
    ]
    return result, total


def get_dept_list(deptName, status):
    query = Department.query
    if deptName:
        query = query.filter(Department.department.like(f'%{deptName}%'))
    if status:
        query = query.filter(Department.status.like(f'%{status}%'))
    users = query.all()
    result = [
        {
            'id': user.dept_id,
            'deptName': user.department,
            'orderNo': user.orderNo,
            'status': user.status,
            'createTime': user.createTime.strftime("%Y-%m-%d %H:%M:%S"),
            'remark': user.remark,
        }
        for user in users
    ]
    return result

