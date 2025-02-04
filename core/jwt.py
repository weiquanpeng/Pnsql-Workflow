from datetime import datetime, timedelta
from jose import JWTError, jwt, ExpiredSignatureError
from initialize.init_config import config

# JWT 配置
SECRET_KEY = "www.pnsql-workflow.com"  # 替换为一个安全的随机字符串
ALGORITHM = "HS256"  # 加密算法
ACCESS_TOKEN_EXPIRE_MINUTES = config['jwt']['expipe_minutes']  # Token 过期时间（分钟）

class JWTUtils:
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str):
        """
        验证 JWT Token
        :param token: 需要验证的 Token
        :return:
            - 1: Token 有效
            - 2: Token 已过期
            - 3: Token 无效
            - payload: Token 解码后的数据（当 Token 有效时返回）
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return 1  # Token 有效，返回状态码和 payload
        except ExpiredSignatureError:
            return 2  # Token 已过期
        except JWTError as e:
            return 3  # Token 无效