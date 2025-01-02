import random
from flask_mail import Message
from datetime import datetime, timedelta, timezone  # 导入 timezone
from blueprints.utils.response_util import ResponseUtil

# 用一个全局字典存储验证码数据
# 格式: {'email': {'verification_code': '123456', 'expiration_time': datetime}}
verification_cache = {}

class EmailUtilMiniProgram:
    def __init__(self, mail):
        self.mail = mail

    def send_verification_code(self, email, email_template=None, email_template_path="邮箱验证界面.txt", subject="注册账号通知"):
        """发送验证码的功能"""

        verification_code = str(random.randint(100000, 999999))

        # 如果没有传入模板字符串，则从文件中读取
        if email_template is None:
            with open(email_template_path, 'r', encoding='utf-8') as f:
                email_template = f.read()

        msg = Message(
            subject=subject,
            sender="1097802349@qq.com",
            html=email_template.format("注册账号", verification_code),
            recipients=[email]
        )

        try:
            self.mail.send(msg)

            # 获取当前时间并加上 10 分钟，生成带时区的时间
            expiration_time = datetime.now(timezone.utc) + timedelta(seconds=600)  # 设置 10 分钟后过期

            # 存储验证码和邮箱信息到内存中
            verification_cache[email] = {
                "verification_code": verification_code,
                "expiration_time": expiration_time
            }

            return ResponseUtil.success('验证码已发送！', result={'VerificationCode': verification_code})
        except Exception as e:
            return ResponseUtil.error(f'发送验证码失败: {str(e)}')

    def validate_verification_code(self, email, input_code):
        """校验验证码"""
        # 获取存储在内存中的验证码信息
        stored_data = verification_cache.get(email)

        # 检查存储的数据是否存在
        if not stored_data:
            return ResponseUtil.error('验证码已过期或无效')

        stored_code = stored_data['verification_code']
        expiration_time = stored_data['expiration_time']

        # 获取当前时间（带时区的时间）
        current_time = datetime.now(timezone.utc)

        # 如果验证码已经过期
        if current_time > expiration_time:
            # 删除过期的数据
            del verification_cache[email]
            return ResponseUtil.error('验证码已过期')

        # 比较输入的验证码和存储的验证码
        input_code = str(input_code)
        if input_code != stored_code:
            return ResponseUtil.error('验证码错误')

        # 验证通过，删除验证码
        del verification_cache[email]
        return ResponseUtil.success('验证码校验通过')
