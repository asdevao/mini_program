# import random
# from flask_mail import Message
# from flask import current_app
# from blueprints.utils.response_util import ResponseUtil
#
#
#
# class EmailUtil:
#     def __init__(self, redis_client, mail):
#         self.r = redis_client
#         self.mail = mail
#
#     def send_verification_code(self, email, email_template=None, email_template_path="邮箱验证界面.txt",
#                                subject="注册账号通知"):
#         """发送验证码的功能"""
#
#         verification_code = str(random.randint(100000, 999999))
#
#         # 如果没有传入模板字符串，则从文件中读取
#         if email_template is None:
#             with open(email_template_path, 'r', encoding='utf-8') as f:
#                 email_template = f.read()
#
#         msg = Message(
#             subject=subject,
#             sender="1097802349@qq.com",
#             html=email_template.format("注册账号", verification_code),
#             recipients=[email]
#         )
#
#         try:
#             self.mail.send(msg)
#
#             # 将验证码存储到 Redis
#             self.r.setex(f"email:{email}:code", 600, verification_code)
#             self.r.setex(f"email:{email}:address", 600, email)  # 额外存储邮箱信息，10 分钟有效期
#             return ResponseUtil.success('验证码已发送！', result={'VerificationCode': verification_code})
#         except Exception as e:
#             return ResponseUtil.error(f'发送验证码失败: {str(e)}')
#
#     def validate_verification_code(self, email, input_code):
#         """校验验证码"""
#         stored_code = self.r.get(f"email:{email}:code")
#         stored_email = self.r.get(f"email:{email}:address")
#
#         print('stored_code:', stored_code)
#         print('input_code:', input_code)
#
#         # 首先检查存储的邮箱
#         if stored_email:
#             stored_email = stored_email.decode('utf-8')
#
#         # 如果邮箱不匹配，立即返回错误
#         if stored_email != email:
#             return ResponseUtil.error('验证码和邮箱不匹配，请重新发送验证码')
#
#             # 接着检查验证码是否存在
#         if stored_code:
#             stored_code = stored_code.decode('utf-8')
#
#         if not stored_code:
#             return ResponseUtil.error('验证码已过期或无效')
#
#         # 确保 input_code 是字符串
#         input_code = str(input_code)
#
#         # 直接比较 input_code 和 stored_code
#         if input_code != stored_code:
#             return ResponseUtil.error('验证码错误')
#
#         # 验证通过，删除验证码
#         self.r.delete(f"email:{email}:code")
#         return ResponseUtil.success('验证码校验通过')

import random
from flask_mail import Message
from blueprints.utils.response_util import ResponseUtil
from datetime import datetime, timedelta, timezone  # 导入 timezone
from flask import session

verification_cache = {}
class EmailUtil:
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

            # 存储验证码和邮箱信息到 session 中
            session['verification_data'] = session.get('verification_data', {})
            session['verification_data'][email] = {
                "verification_code": verification_code,
                "expiration_time": expiration_time
            }

            # Debug: 打印存储的信息
            print(f"验证码已发送，存储的数据: {session['verification_data'][email]}")

            return ResponseUtil.success('验证码已发送！', result={'VerificationCode': verification_code})
        except Exception as e:
            return ResponseUtil.error(f'发送验证码失败: {str(e)}')

    def validate_verification_code(self, email, input_code):
        """校验验证码"""
        # 获取存储在 session 中的验证码信息
        stored_data = session.get('verification_data', {}).get(email)

        # 检查存储的数据是否存在
        if not stored_data:
            return ResponseUtil.error('验证码已过期或无效')

        stored_code = stored_data['verification_code']
        expiration_time = stored_data['expiration_time']

        # 获取当前时间（带时区的时间）
        current_time = datetime.now(timezone.utc)  # 使用 UTC 时区作为例子

        # 如果验证码已经过期
        if current_time > expiration_time:
            # 删除过期的数据
            del session['verification_data'][email]
            return ResponseUtil.error('验证码已过期')

        # 比较输入的验证码和存储的验证码
        input_code = str(input_code)
        if input_code != stored_code:
            return ResponseUtil.error('验证码错误')

        # 验证通过，删除验证码
        del session['verification_data'][email]
        return ResponseUtil.success('验证码校验通过')







