import hashlib


def hash_auth(password):
    # 创建一个 SHA-256 哈希对象
    sha256 = hashlib.sha256()
    # 将密码编码为字节类型
    password_bytes = password.encode('utf-8')
    # 更新哈希对象的内容
    sha256.update(password_bytes)
    # 获取哈希值的十六进制表示
    hashed_password = sha256.hexdigest()
    return hashed_password
