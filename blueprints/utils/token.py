import base64
import hmac
import time
import hashlib


class Token:

    @classmethod
    def generate_token(cls, key, expire=43200):
        """
        生成一个基于 HMAC 的 token。

        Args:
            key (str): 用户提供的密钥，后续验证时需要使用相同的密钥。
            expire (int): token 的有效时长，单位为秒，默认 12 小时 (43200 秒)。

        Returns:
            str: 生成的 Base64 编码的 token 字符串。
        """
        # 生成过期时间的时间戳，使用整数以避免浮点数精度问题
        ts_int = int(time.time() + expire)
        ts_str = str(ts_int)

        # 生成 HMAC-SHA256 校验码
        ts_byte = ts_str.encode("utf-8")
        sha256 = hmac.new(key.encode("utf-8"), ts_byte, hashlib.sha256).hexdigest()

        # 生成最终的 token 格式为：过期时间:校验码
        token = f"{ts_str}:{sha256}"

        # 对 token 进行 Base64 编码
        b64_token = base64.urlsafe_b64encode(token.encode("utf-8"))

        return b64_token.decode("utf-8")

    @classmethod
    def certify_token(cls, key, token):
        """
        验证 token 是否有效。

        Args:
            key (str): 用户提供的密钥，应该与生成 token 时使用的密钥一致。
            token (str): 需要验证的 token 字符串。

        Returns:
            bool: 验证通过返回 True，否则返回 False。
        """
        try:
            # 解码 Base64 token
            token_str = base64.urlsafe_b64decode(token).decode('utf-8')

            # 拆分 token，格式应该为 [时间戳:校验码]
            token_list = token_str.split(':')
            if len(token_list) != 2:
                return False

            ts_str, known_sha256 = token_list
            ts_int = int(ts_str)  # 转换时间戳为整数

            # 检查 token 是否过期
            if ts_int < int(time.time()):
                return False

            # 重新计算 HMAC-SHA256 校验码并与已知校验码比较
            sha256 = hmac.new(key.encode("utf-8"), ts_str.encode('utf-8'), hashlib.sha256).hexdigest()

            # 比较校验码是否一致
            if sha256 != known_sha256:
                return False
        except (ValueError, base64.binascii.Error):
            # 处理 Base64 解码错误或时间戳转换错误
            return False

        return True
